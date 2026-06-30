-- Typed repayments with amounts normalized to USD.

with source as (
    select * from {{ source('raw', 'repayments') }}
),

cleaned as (
    select
        payment_id,
        loan_id,
        payment_date,
        round(amount / case currency
            when 'XOF' then 655.957
            when 'NGN' then 1550.0
            when 'KES' then 130.0
            else 1.0
        end, 2)                                as amount_usd,
        channel
    from source
    where payment_id is not null
      and amount > 0
)

select * from cleaned
