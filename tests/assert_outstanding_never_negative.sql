-- Negative outstanding means repayments were double-counted somewhere.

select loan_id, outstanding_balance_usd
from {{ ref('loan_portfolio_risk') }}
where outstanding_balance_usd < 0
