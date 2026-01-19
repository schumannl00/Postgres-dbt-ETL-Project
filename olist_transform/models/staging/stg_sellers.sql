select 
    seller_id, 
    seller_zip_code_prefix as zip,
    seller_ciy, 
    seller_state
from {{ source('raw', 'sellers') }}