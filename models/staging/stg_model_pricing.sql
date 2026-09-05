with model_pricing as (
    -- Static lookup CTE for current LLM pricing per 1M tokens (in USD)
    select
        'gpt-4o' as model_name,
        5.00 as cost_per_1m_input_tokens,
        15.00 as cost_per_1m_output_tokens
        
    union all
    
    select
        'claude-3-5-sonnet' as model_name,
        3.00 as cost_per_1m_input_tokens,
        15.00 as cost_per_1m_output_tokens
        
    union all
    
    select
        'gpt-4o-mini' as model_name,
        0.15 as cost_per_1m_input_tokens,
        0.60 as cost_per_1m_output_tokens
)

select 
    model_name,
    cost_per_1m_input_tokens,
    cost_per_1m_output_tokens
from model_pricing
