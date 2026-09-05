with source as (
    -- Assuming a sources.yml configuration exists for raw_data, otherwise this could be raw_data.raw_llm_traces
    select * from {{ source('raw_data', 'raw_llm_traces') }}
)

select
    trace_id,
    customer_id,
    feature_name,
    model_name,
    
    -- Handle potential nulls with sensible defaults
    coalesce(prompt_tokens, 0) as prompt_tokens,
    coalesce(completion_tokens, 0) as completion_tokens,
    coalesce(execution_time_ms, 0) as execution_time_ms,
    coalesce(agent_step_number, 1) as agent_step_number,
    coalesce(cost_usd, 0.0) as estimated_cost_usd,
    
    -- Cast timestamp explicitly to ensure timezone consistency across the pipeline
    cast(timestamp as timestamp) as trace_timestamp

from source
