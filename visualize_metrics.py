import os
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "dbname": os.getenv("DB_NAME", "onvlo"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432))
}

try:
    conn = psycopg2.connect(**db_config)
    df_margins = pd.read_sql("SELECT * FROM public.fct_customer_ai_margins LIMIT 10", conn)
    df_units = pd.read_sql("SELECT * FROM public.fct_token_unit_economics LIMIT 10", conn)
    conn.close()
except Exception as err:
    print(f"Failed to query database for visualization: {err}")
    exit(1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Customer Margins
num_cols_margins = df_margins.select_dtypes(include=['number']).columns
if len(num_cols_margins) > 0 and 'customer_id' in df_margins.columns:
    df_margins.plot(x='customer_id', y=num_cols_margins[:2], kind='bar', ax=axes[0])
    axes[0].set_title("Customer Unit Margins")
    axes[0].set_ylabel("USD ($)")
    axes[0].grid(axis='y', linestyle='--', alpha=0.6)

# Unit Economics
num_cols_units = df_units.select_dtypes(include=['number']).columns
if len(num_cols_units) > 0:
    first_col = df_units.columns[0]
    df_units.plot(x=first_col, y=num_cols_units[:2], kind='bar', ax=axes[1])
    axes[1].set_title("Token Unit Economics")
    axes[1].grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("onvlo_dashboard.png")
print("Dashboard saved to onvlo_dashboard.png")
