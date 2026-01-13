with raw_customers as (
    select * from {{ source('raw', 'customers') }}
)

select
    -- Primary key for joining to orders
    customer_id,
    -- Unique ID for identifying the actual person (for LTV/Loyalty)
    customer_unique_id,
    customer_zip_code_prefix as zip_code,
    customer_city,
    customer_state
from raw_customers