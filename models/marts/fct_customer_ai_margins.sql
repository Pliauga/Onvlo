with fct_unit_economics as (
    select * from {{ ref('fct_token_unit_economics') }}
),

-- In a real production setup, this would be a source model fed by Stripe, Salesforce, or Hubspot
mock_subscription_revenue as (
    select 'ENT-0001' as customer_id, 'Enterprise' as tier, 500.00 as daily_subscription_revenue_usd
    union all select 'ENT-0002', 'Enterprise', 500.00
    union all select 'ENT-0003', 'Enterprise', 500.00
    union all select 'CUST-0001', 'Pro', 50.00
    union all select 'CUST-0002', 'Pro', 50.00
    -- All other customers will fallback to standard below
),

daily_cost_aggregated as (
    select
        customer_id,
        date_trunc('day', trace_timestamp) as report_date,
        sum(total_cost_usd) as total_llm_cost_usd,
        sum(prompt_tokens) as total_prompt_tokens,
        sum(completion_tokens) as total_completion_tokens,
        count(*) as total_api_calls
    from fct_unit_economics
    group by 1, 2
)

select
    agg.customer_id,
    agg.report_date,
    agg.total_api_calls,
    agg.total_prompt_tokens,
    agg.total_completion_tokens,
    agg.total_llm_cost_usd,
    
    -- Join mock subscription tier or default to 'Standard'
    coalesce(sub.tier, 'Standard') as subscription_tier,
    coalesce(sub.daily_subscription_revenue_usd, 15.00) as daily_subscription_revenue_usd,
    
    -- Net margin per customer per day
    (coalesce(sub.daily_subscription_revenue_usd, 15.00) - agg.total_llm_cost_usd) as net_margin_usd,
    
    -- Flag unprofitable accounts
    case 
        when (coalesce(sub.daily_subscription_revenue_usd, 15.00) - agg.total_llm_cost_usd) < 0 then true
        else false
    end as is_unprofitable

from daily_cost_aggregated agg
left join mock_subscription_revenue sub on agg.customer_id = sub.customer_id
