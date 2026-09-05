import json
import os
import sys
import warnings
import pandas as pd
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings('ignore', category=UserWarning)


def send_slack_alert(anomalies):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    user_id = os.getenv("SLACK_USER_ID")

    if not webhook_url or "YOUR/WEBHOOK" in webhook_url:
        print("Slack webhook not set. Skipping alert.")
        return

    user_tag = f"<@{user_id}> " if user_id else ""

    summary_lines = [
        f"• *Trace:* `{row['trace_id']}` | *Customer:* `{row['customer_id']}` | "
        f"*Steps:* {row['total_steps']} | *Tokens:* {row['total_tokens']:,} | *Cost:* ${row['total_cost_usd']:.2f}"
        for _, row in anomalies.head(10).iterrows()
    ]

    payload = {
        "text": f"Anomaly Alert: {len(anomalies)} trace(s) flagged",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{user_tag}Flagged *{len(anomalies)}* trace(s) exceeding normal step or token thresholds (Z-score > 3.0)."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Top Anomalies:*\n" + "\n".join(summary_lines)
                }
            }
        ]
    }

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        if res.status_code == 200:
            print("Slack alert sent.")
        else:
            print(f"Failed to post Slack alert: HTTP {res.status_code}")
    except Exception as err:
        print(f"Error posting alert to Slack: {err}")


def detect_infinite_loops(db_params):
    try:
        conn = psycopg2.connect(**db_params)
        query = """
        SELECT 
            trace_id,
            customer_id,
            MAX(agent_step_number) AS total_steps,
            SUM(prompt_tokens + completion_tokens) AS total_tokens,
            SUM(cost_usd) AS total_cost_usd
        FROM raw_data.raw_llm_traces
        GROUP BY trace_id, customer_id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as err:
        print(f"Database query failed ({err}). Trying local JSON fallback...")
        try:
            df = pd.read_json("raw_llm_traces.json", lines=True)
            df['total_tokens'] = df['prompt_tokens'] + df['completion_tokens']
            df = df.groupby(['trace_id', 'customer_id']).agg(
                total_steps=('agent_step_number', 'max'),
                total_tokens=('total_tokens', 'sum'),
                total_cost_usd=('cost_usd', 'sum')
            ).reset_index()
        except Exception as json_err:
            print(f"Failed to read raw_llm_traces.json: {json_err}")
            sys.exit(1)

    if df.empty:
        print("No trace data available.")
        return

    # Calculate Z-scores to flag statistical outliers (> 3 std dev)
    df['z_score_steps'] = (df['total_steps'] - df['total_steps'].mean()) / df['total_steps'].std()
    df['z_score_tokens'] = (df['total_tokens'] - df['total_tokens'].mean()) / df['total_tokens'].std()

    anomalies = df[(df['z_score_steps'] > 3.0) | (df['z_score_tokens'] > 3.0)]

    if anomalies.empty:
        print("No trace anomalies detected.")
        return

    print(f"Flagged {len(anomalies)} anomalous trace(s):")
    anomalies = anomalies.sort_values('z_score_tokens', ascending=False)

    for _, row in anomalies.iterrows():
        print(f"Trace: {row['trace_id']} | Customer: {row['customer_id']} | "
              f"Steps: {row['total_steps']} (Z: {row['z_score_steps']:.2f}) | "
              f"Tokens: {row['total_tokens']:,} (Z: {row['z_score_tokens']:.2f}) | "
              f"Cost: ${row['total_cost_usd']:.2f}")

    send_slack_alert(anomalies)


if __name__ == "__main__":
    db_config = {
        "dbname": os.getenv("DB_NAME", "onvlo"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432))
    }

    detect_infinite_loops(db_config)
