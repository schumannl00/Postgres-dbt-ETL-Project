with products as (
    select * from {{ ref('stg_products') }}
),
orders as (
    select * from {{ ref('stg_order') }}
),
order_items as (
    select * from {{ ref('stg_order_items') }}
),
category_translation as (
    select * from {{ ref('stg_category_translate') }}
)

select 
    date_trunc('month', o.purchase_at)::date as revenue_month,
    extract(year from o.purchase_at) as revenue_year,
    extract(month from o.purchase_at) as revenue_month_num,
    to_char(o.purchase_at, 'YYYY-MM') as revenue_year_month,  -- '2017-01'
    coalesce(ct.category_name_en, 'Unknown') as product_category,
    round(sum(oi.total_item_cost)::numeric,2)   as monthly_revenue,
    count(oi.product_id) as product_sold
from orders o
join order_items oi using (order_id)
join products p using (product_id)
left join category_translation ct on p.product_category_name = ct.category_name_pt
group by 1, 2, 3, 4, 5
order by revenue_year desc, revenue_month_num desc, monthly_revenue desc