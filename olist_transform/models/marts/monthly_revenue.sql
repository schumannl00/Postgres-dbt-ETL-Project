with orders as (
    select * from {{ ref('fct_orders') }}
)

select
    date_trunc('month', purchase_at)::date as order_month,
    count(order_id) as total_fullfilled_orders,
    sum(total_order_amount) as revenue,
    sum(total_items) as items_sold
from orders
-- Only include revenue-generating statuses, so delivered, shipped, invoiced, processed orders
where order_status not in ('canceled', 'unavailable')
  and total_order_amount > 0
group by 1
order by 1 desc