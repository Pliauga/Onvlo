CREATE SCHEMA IF NOT EXISTS raw_data;

CREATE TABLE IF NOT EXISTS raw_data.raw_llm_traces (
    id SERIAL PRIMARY KEY,
    trace_id UUID NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    agent_step_number INTEGER NOT NULL,
    cost_usd NUMERIC(10, 6),
    timestamp TIMESTAMPTZ NOT NULL
);
