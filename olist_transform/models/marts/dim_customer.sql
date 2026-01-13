

with customers_unique as (
    -- We only need one row per human to get their city/state
    -- Using DISTINCT ON is a handy Postgres trick for this
    select distinct on (customer_unique_id)
        customer_unique_id,
        customer_city,
        customer_state
    from {{ ref('stg_customer') }}
),

order_stats as (
    select
        c.customer_unique_id,
        min(o.purchase_at) as first_order_date,
        max(o.purchase_at) as last_order_date,
        count(o.order_id) as total_orders,
        sum(o.total_order_amount) as lifetime_value,
        round(avg(o.total_order_amount)::numeric, 2) as average_order_value
    from {{ ref('fct_orders') }} o
    join {{ ref('stg_customer') }} c using (customer_id)
    group by 1
)

select
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    s.first_order_date,
    s.last_order_date,
    coalesce(s.total_orders, 0) as total_orders,
    coalesce(s.lifetime_value, 0) as lifetime_value,
    coalesce(s.average_order_value, 0) as average_order_value,
    case 
        when s.lifetime_value >= 3000 then 'VIP'
        when s.lifetime_value >= 1000 then 'High Value'
        when s.lifetime_value >= 200 then 'Medium Value'
        when s.lifetime_value > 0 then 'Low Value'
        else 'Lead / No Purchase'
    end as customer_segment
from customers_unique c
left join order_stats s using (customer_unique_id)