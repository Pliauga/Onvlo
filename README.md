# Onvlo

Onvlo is a local FinOps engine for monitoring LLM consumption, cost unit economics, and runaway agent loops. It ingests traces into PostgreSQL, models costs using dbt, calculates Z-scores to flag anomalies, and sends alerts to Slack.

## Quick Start

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database & Data Pipeline
```bash
createdb onvlo
psql -d onvlo -f schema.sql
python3 generate_dataset.py
python3 load_data.py
```

### 3. Run Pipeline & Anomaly Checks
```bash
./run_test.sh
```

### 4. Generate Visual Dashboard
```bash
python3 visualize_metrics.py
```

## Configuration

Copy `.env.example` to `.env` and set your local credentials:

```ini
DB_NAME="onvlo"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT=5432
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```
