# digital-lending-analytics-dbt

Data warehouse for digital lending portfolio analytics with dbt on DuckDB: loan-level risk, country-level PAR, and monthly origination cohorts.

```
raw.loans / raw.repayments   (seeded synthetic loan book with on-time / late / default behaviors)
    ↓ staging   type, normalize XOF/NGN/KES → USD
    ↓ marts
        risk/loan_portfolio_risk   DPD, delinquency buckets, IFRS9-style provisioning ladder
        risk/portfolio_summary     PAR30/60/90 ratios, NPL exposure per country
        finance/cohort_analysis    repayment & NPL rate by disbursement month × product
```

Data is **synthetic** (seeded generator in `data_generator/`, ~12k loans, ~10% defaulters) — no proprietary data. Guardrails: uniqueness/relationships tests plus singular tests (outstanding never negative, PAR30 ≥ PAR60 ≥ PAR90 by construction).

## Run

```bash
pip install dbt-duckdb pytest
python data_generator/generate.py --db lending.duckdb
export LENDING_DB_PATH=$PWD/lending.duckdb
dbt build --project-dir . --profiles-dir .
pytest
```
