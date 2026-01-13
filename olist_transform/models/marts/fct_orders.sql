with orders as (
    select * from {{ ref('stg_order') }}
),

order_items as (
    -- We aggregate here so we don't duplicate order rows
    select 
        order_id,
        round(sum(price)::numeric, 2) as total_price,
        round(sum(freight_value)::numeric, 2) as total_freight,
        round(sum(total_item_cost)::numeric, 2) as total_order_amount,
        count(product_id) as total_items
    from {{ ref('stg_order_items') }}
    group by 1 -- this is just shorthand for order_id
)

select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.purchase_at,
    coalesce(oi.total_price, 0) as total_price,
    coalesce(oi.total_freight, 0) as total_freight,
    coalesce(oi.total_order_amount, 0) as total_order_amount,
    coalesce(oi.total_items, 0) as total_items
from orders o
left join order_items oi using (order_id)