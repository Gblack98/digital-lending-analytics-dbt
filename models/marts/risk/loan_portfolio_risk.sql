-- loan_portfolio_risk.sql
-- Real-time portfolio risk KPIs — used by risk officers dashboard

with loans as (
    select * from {{ ref('stg_loans') }}
),

repayments as (
    select * from {{ ref('stg_repayments') }}
),

loan_performance as (
    select
        l.loan_id,
        l.customer_id,
        l.disbursed_at,
        l.maturity_date,
        l.principal_usd,
        l.interest_rate_pct,
        l.product_type,        -- nano_loan, micro_loan, sme_loan, bnpl
        l.country_code,
        l.segment,

        -- Repayment metrics
        coalesce(r.total_paid_usd, 0)                       as total_paid_usd,
        coalesce(r.last_payment_date, l.disbursed_at)       as last_payment_date,
        l.principal_usd - coalesce(r.total_paid_usd, 0)    as outstanding_balance_usd,

        -- Days past due (DPD) — key risk metric
        case
            when coalesce(r.total_paid_usd, 0) >= l.principal_usd then 0
            when current_date <= l.maturity_date then 0
            else date_part('day', current_date - l.maturity_date)
        end                                                  as days_past_due,

        -- Loan status
        case
            when coalesce(r.total_paid_usd, 0) >= l.principal_usd then 'closed'
            when current_date <= l.maturity_date then 'active'
            when date_part('day', current_date - l.maturity_date) <= 30 then 'dpd_1_30'
            when date_part('day', current_date - l.maturity_date) <= 60 then 'dpd_31_60'
            when date_part('day', current_date - l.maturity_date) <= 90 then 'dpd_61_90'
            else 'npl'  -- Non-performing loan (>90 days past due, like Rubyx's 0.55% NPL)
        end                                                  as loan_status

    from loans l
    left join (
        select loan_id,
               sum(amount_usd) as total_paid_usd,
               max(payment_date) as last_payment_date
        from repayments
        group by loan_id
    ) r using (loan_id)
),

final as (
    select
        *,
        -- Portfolio risk ratios
        case when loan_status = 'npl' then outstanding_balance_usd else 0 end
            as npl_exposure_usd,
        outstanding_balance_usd * 0.05  as provision_required_usd  -- 5% provision on active
    from loan_performance
)

select * from final
