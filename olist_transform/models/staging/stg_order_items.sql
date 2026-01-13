select
    order_id,
    order_item_id, 
    product_id,
    seller_id,
    price,
    freight_value,
    (price + freight_value) as total_item_cost
from {{ source('raw', 'order_items') }}