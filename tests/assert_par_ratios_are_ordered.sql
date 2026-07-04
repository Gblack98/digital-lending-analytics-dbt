-- By construction PAR30 exposure includes PAR60, which includes PAR90.
-- An inversion means the DPD bucketing is broken.

select country_code, par30_ratio, par60_ratio, par90_ratio
from {{ ref('portfolio_summary') }}
where par30_ratio < par60_ratio
   or par60_ratio < par90_ratio
