{{
    config(
        materialized='incremental',
        unique_key=['trace_id', 'agent_step_number']
    )
}}

with traces as (
    select * from {{ ref('stg_llm_traces') }}
    
    {% if is_incremental() %}
        -- Only process new traces since the last run
        where trace_timestamp >= (select max(trace_timestamp) from {{ this }})
    {% endif %}
),

pricing as (
    select * from {{ ref('stg_model_pricing') }}
),

cost_calculations as (
    select
        t.trace_id,
        t.customer_id,
        t.feature_name,
        t.model_name,
        t.prompt_tokens,
        t.completion_tokens,
        t.execution_time_ms,
        t.agent_step_number,
        t.trace_timestamp,
        
        -- Calculate input and output costs based on pricing per 1M tokens
        (t.prompt_tokens / 1000000.0) * p.cost_per_1m_input_tokens as input_cost_usd,
        (t.completion_tokens / 1000000.0) * p.cost_per_1m_output_tokens as output_cost_usd,
        
        -- Calculate total cost for this specific API call
        ((t.prompt_tokens / 1000000.0) * p.cost_per_1m_input_tokens) + 
        ((t.completion_tokens / 1000000.0) * p.cost_per_1m_output_tokens) as total_cost_usd

    from traces t
    left join pricing p on t.model_name = p.model_name
)

select
    trace_id,
    customer_id,
    feature_name,
    model_name,
    prompt_tokens,
    completion_tokens,
    execution_time_ms,
    agent_step_number,
    trace_timestamp,
    input_cost_usd,
    output_cost_usd,
    total_cost_usd,
    
    -- Calculate running cumulative cost for each multi-step workflow
    sum(total_cost_usd) over (
        partition by trace_id 
        order by trace_timestamp asc
        rows between unbounded preceding and current row
    ) as cumulative_trace_cost_usd

from cost_calculations
