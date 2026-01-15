with product_base_stats as (
    select
        p.product_id,
        coalesce(p.category_name, 'Unknown') as category,
        count(*) as sales_count,
        -- Using existing columns
        round(avg(oi.price)::numeric, 2) as avg_price,
        round(avg(oi.freight_value)::numeric, 2) as avg_freight,
        round(avg(oi.total_item_cost)::numeric, 2) as avg_total_cost, -- Assuming this is your total column
        case 
            when count(*) = 1 then 'Single Sale'
            when count(*) < 4 then 'Low Confidence'
            else 'High Confidence'
         end as reliability_score,
        -- Volatility (Standard Deviation)
        round(coalesce(stddev(oi.price), 0)::numeric, 4) as price_volatility,
        round(coalesce(stddev(oi.freight_value), 0)::numeric, 4) as freight_volatility,
        round(coalesce(stddev(oi.total_item_cost), 0)::numeric, 4) as total_cost_volatility
        
    from {{ ref('stg_order_items') }} oi
    join {{ ref('dim_products') }} p using (product_id)
    group by 1, 2
),

category_analysis as (
    select
        *,
        -- Freight Impact:
        (avg_freight / nullif(avg_total_cost, 0)) * 100 as freight_share_pct,
        
        -- Category Benchmarks using Window Functions
        avg(avg_total_cost) over(partition by category) as cat_avg_total_cost,
        stddev(avg_total_cost) over(partition by category) as cat_stddev_total_cost,
        avg(avg_freight) over(partition by category) as cat_avg_freight_share, 
        case 
            when total_cost_volatility < (price_volatility + freight_volatility) * 0.3  
                 and sales_count > 1 
                 and (price_volatility > 0 or freight_volatility > 0)
            then True else False 
        end as is_price_rebalanced
    from product_base_stats
), 

final_feature_engineering as (
    select 
        *,
    -- Z-Score for the Total Cost
    (avg_total_cost - cat_avg_total_cost) / nullif(cat_stddev_total_cost, 0) as total_cost_z_score,
    
    -- Deviation from Category Freight Norm
    -- (e.g., Is shipping this item way more expensive than other items in the same category?)
    (freight_share_pct - cat_avg_freight_share) as freight_pct_diff_from_avg,
    total_cost_volatility / nullif(avg_total_cost, 0) as total_cost_cv, 
    (avg_price * sales_count) as product_revenue
    from category_analysis
),

pareto_analysis as (
    select
        *,
        -- Running total within the category (The "Pareto Line")
        sum(avg_price * sales_count) over (
            partition by category 
            order by (avg_price * sales_count) desc
        ) as cumulative_category_revenue,
        -- Total category revenue for percentage calculation
        sum(avg_price * sales_count) over (partition by category) as total_category_revenue
    from final_feature_engineering
)

select
    *,
    round(((avg_price * sales_count) / nullif(total_category_revenue, 0)) * 100 ::numeric, 4) as product_revenue_share_pct,
    round(
        (cumulative_category_revenue / nullif(total_category_revenue, 0)) * 100, 4
    ) as pareto_revenue_pct,
    case 
        when (cumulative_category_revenue / nullif(total_category_revenue, 0)) <= 0.8
        then True else False 
    end as is_revenue_workhorse
from pareto_analysis