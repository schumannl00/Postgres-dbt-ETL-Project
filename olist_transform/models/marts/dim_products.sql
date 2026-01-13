
-- use cte for better readability and use ref to ensure dependencies are tracked and run before
with products as (
    select * from {{ ref('stg_products') }}
),

translation as (
    select * from {{ ref('stg_category_translate') }}
)

select
    p.product_id,
    -- Use English name if available, otherwise fallback to Portuguese, that is what coalesce does
    coalesce(t.category_name_en, p.product_category_name) as category_name,
    p.weight_g,
    p.length_cm,
    p.height_cm,
    p.width_cm,
    (p.length_cm * p.height_cm * p.width_cm) as volume_cm3
from products p
left join translation t 
    on p.product_category_name = t.category_name_pt