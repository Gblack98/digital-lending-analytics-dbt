-- Headline risk KPIs per country, the first table a risk officer opens.
-- PAR30/60/90 = share of outstanding held by loans more than 30/60/90 days
-- past due (standard microfinance portfolio-at-risk definition).

with loans as (
    select * from {{ ref('loan_portfolio_risk') }}
),

by_country as (
    select
        country_code,
        count(*)                                              as total_loans,
        sum(principal_usd)                                    as disbursed_usd,
        sum(outstanding_balance_usd)                          as outstanding_usd,
        sum(outstanding_balance_usd) filter (days_past_due > 30)
                                                              as par30_exposure_usd,
        sum(outstanding_balance_usd) filter (days_past_due > 60)
                                                              as par60_exposure_usd,
        sum(outstanding_balance_usd) filter (days_past_due > 90)
                                                              as par90_exposure_usd,
        sum(npl_exposure_usd)                                 as npl_exposure_usd,
        sum(provision_required_usd)                           as provision_required_usd
    from loans
    group by 1
)

select
    *,
    round(par30_exposure_usd / nullif(outstanding_usd, 0), 4) as par30_ratio,
    round(par60_exposure_usd / nullif(outstanding_usd, 0), 4) as par60_ratio,
    round(par90_exposure_usd / nullif(outstanding_usd, 0), 4) as par90_ratio
from by_country
order by outstanding_usd desc
