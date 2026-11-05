# Findings and interpretation

## What the extract shows

The 2024 ACS 1-year B25070, B25003, and B25064 files join at county geography for **855 counties**. Each county has one row. For every included row, B25070 categories sum to its renter-occupied total, B25003 owners plus renters equal occupied households, and the B25070 total matches the B25003 renter total. The dashboard should default to all included counties and expose state and county filters.

- The median of county 30%+ rent-burden estimates is **50.15%**. This treats each county equally.
- Pooling the 30%+ numerator and calculable denominator across included counties yields **52.55%**. This weights counties by the relevant renter-unit count, but it excludes counties absent from the extract and is not a U.S. rate.
- Among states with at least five included counties, Florida's **40 included counties** have a **61.29% median county rate**; Wisconsin's **25 included counties** have a **42.30% median county rate**. These are medians of included counties, not state-level ACS estimates or a formal test of differences.
- The median of county B25064 gross-rent estimates is **$1,244**. It is an unweighted county median and should not be described as the median rent paid by U.S. renters.

## How to read the dashboard

Use a state selector to narrow counties, then compare the 30%+ and 50%+ burden shares. A scatter plot of median gross rent against burden rate can identify counties for follow-up, but cannot establish that rent levels caused burden: income distribution, household composition, and local sampling uncertainty also matter. A state-to-county drill or filtered ranking can show within-state variation. KPI cards should label whether they show a county median or covered-county pooled rate.

## Limits

- The ACS is a sample survey. The published table files include margins of error (MOE); the curated CSV retains source MOEs for renter households, B25070 total, and median gross rent. The derived ratios do not include a calculated MOE, so close county comparisons are descriptive only.
- The standard ACS 1-year county release generally covers places with at least 65,000 people. This extract excludes smaller counties and six counties without B25070 data: Columbia (FL), Lea (NM), Liberty (TX), Pender (NC), Toa Alta Municipio (PR), and Waller (TX).
- B25070's `Not computed` category is excluded from the burden denominator. Never use all renters as that denominator without this exclusion.
- B25064 median gross rent covers renter-occupied units paying cash rent; B25003 tenure covers all occupied units. Their denominators differ.
- County rates are estimates for 2024, not measured changes over time. Do not infer a trend or make causal claims from this cross-section.

