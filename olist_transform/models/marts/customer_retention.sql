with order_mapping as (
    select
        o.order_id,
        o.purchase_at,
        c.customer_unique_id
    from {{ ref('fct_orders') }} o
    join {{ ref('stg_customer') }} c using (customer_id)
),

dataset_metadata as (
    select max(purchase_at) as max_data_date
    from order_mapping
),

retention_calc as (
    select
        customer_unique_id,
        order_id,
        purchase_at,
        d.max_data_date,
        -- Look back at the previous order date for this specific person
        lag(purchase_at) over (
            partition by customer_unique_id 
            order by purchase_at
        ) as previous_order_at,
        -- Sequence the orders
        row_number() over (
            partition by customer_unique_id 
            order by purchase_at
        ) as order_sequence, 
        count(*) over (partition by customer_unique_id) as total_customer_orders
    from order_mapping 
    cross join dataset_metadata d
),


final_calculations as (
    select
        *,
        extract(epoch from (purchase_at - previous_order_at))/ 86400 as days_between_orders,
        extract(day from (max_data_date - purchase_at)) as recency_days
    from retention_calc
)
select
    customer_unique_id,
    order_id,
    purchase_at as most_recent_purchase_at,
    previous_order_at,
    coalesce(order_sequence, 0) as order_sequence,
    coalesce(total_customer_orders, 0) as total_customer_orders,
    round(days_between_orders, 2) as days_between_orders,
    recency_days,
    
    -- Lifecycle logic using our clean alias
  case 
        -- 1. The actual repeat transactions (Order 2, 3, etc.)
        when order_sequence > 1 then 'Repeat Transaction'
        
        -- 2. The very first order of a person who WE KNOW came back later
        when order_sequence = 1 and total_customer_orders > 1 then 'Initial Purchase (Loyalist)'
        
        -- 3. The only order of someone who bought long ago
        when total_customer_orders = 1 and recency_days > 365 then 'Lapsed (One-Time)'
        
        -- 4. The only order of someone who bought recently
        when total_customer_orders = 1 and recency_days <= 365 then 'New (Potential Repeat)'
        
        else 'No Order'
    end as lifecycle_stage,

    -- Retention Window logic using our clean alias
    case 
        when order_sequence = 1 then 'First Order'
        when days_between_orders <= 30 then 'Quick Return (<30d)'
        when days_between_orders <= 90 then 'Standard (30-90d)'
        else 'Delayed (>90d)'
    end as retention_window
from final_calculations