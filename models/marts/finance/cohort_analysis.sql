-- cohort_analysis.sql
-- Loan cohort retention/repayment analysis
-- Key for understanding product performance over time

with loans as (
    select * from {{ ref('loan_portfolio_risk') }}
),

cohorts as (
    select
        date_trunc('month', disbursed_at)   as cohort_month,
        product_type,
        country_code,
        count(distinct loan_id)             as loans_originated,
        sum(principal_usd)                  as total_disbursed_usd,
        avg(interest_rate_pct)              as avg_rate_pct,
        count(*) filter (where loan_status = 'closed')
          * 100.0 / count(*)               as repayment_rate_pct,
        count(*) filter (where loan_status = 'npl')
          * 100.0 / count(*)               as npl_rate_pct,
        sum(npl_exposure_usd)               as npl_exposure_usd,
        avg(days_past_due) filter
            (where days_past_due > 0)       as avg_dpd_delinquent
    from loans
    group by 1, 2, 3
)

select * from cohorts
order by cohort_month desc, product_type, country_code
