-- Typed loans with amounts normalized to USD.

with source as (
    select * from {{ source('raw', 'loans') }}
),

cleaned as (
    select
        loan_id,
        customer_id,
        disbursed_at,
        maturity_date,
        round(principal / case currency
            when 'XOF' then 655.957
            when 'NGN' then 1550.0
            when 'KES' then 130.0
            else 1.0
        end, 2)                                as principal_usd,
        interest_rate_pct,
        product_type,
        country                                as country_code,
        segment
    from source
    where loan_id is not null
      and principal > 0
)

select * from cleaned
