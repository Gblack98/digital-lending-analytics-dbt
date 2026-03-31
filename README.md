# 📊 Digital Lending Analytics — dbt Data Warehouse

![dbt](https://img.shields.io/badge/dbt-1.7-orange) ![SQL](https://img.shields.io/badge/SQL-Analytics-blue) ![Lending](https://img.shields.io/badge/Domain-Digital_Lending-green) ![BI](https://img.shields.io/badge/BI-Portfolio_Analytics-purple)

> dbt data warehouse for digital lending platforms — loan portfolio KPIs, cohort analysis, NPL tracking, and operational dashboards. Inspired by **Rubyx.io** (€125M disbursed, 0.55% NPL rate).

## Models

### Risk Mart
| Model | Description |
|-------|-------------|
| `loan_portfolio_risk` | DPD buckets, NPL identification, loan status |
| `cohort_analysis` | Repayment rates by cohort month × product × country |

### Finance Mart  
| Model | Description |
|-------|-------------|
| `revenue_recognition` | Interest income, fees, provisions |
| `portfolio_summary` | AUM, at-risk exposure, coverage ratios |

### Operations Mart
| Model | Description |
|-------|-------------|
| `disbursement_funnel` | Application → approval → disbursement rates |
| `collections_efficiency` | Recovery rates by DPD bucket |

## Key Metrics Tracked

| KPI | Formula | Target |
|-----|---------|--------|
| **NPL Rate** | Loans > 90 DPD / Total Portfolio | < 2% |
| **PAR30** | Loans > 30 DPD / Total Portfolio | < 5% |
| **Repayment Rate** | Closed loans / Matured loans | > 92% |
| **Cost of Risk** | Provisions / Average Portfolio | < 3% |

## Loan Status Buckets (DPD)

```sql
'active'    → not yet matured
'dpd_1_30'  → 1-30 days past due (early warning)
'dpd_31_60' → 31-60 days (collection triggered)
'dpd_61_90' → 61-90 days (escalation)
'npl'       → > 90 days (non-performing, provisioned)
'closed'    → fully repaid
```

## Setup

```bash
pip install dbt-postgres
dbt deps
dbt run
dbt test
dbt docs generate && dbt docs serve  # Interactive docs at localhost:8080
```

## Author

**Ibrahima Gabar Diop** — [GitHub](https://github.com/Gblack98) · [Kaggle](https://www.kaggle.com/ibrahimagabardiop)
