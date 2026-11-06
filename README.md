# U.S. county rental cost burden | Power BI

**Status:** validated source data, published interactive Power BI report, and two-page PDF export.

**Explore the work:** [Interactive Power BI report](https://app.powerbi.com/groups/e6426da3-9b36-4519-acf1-2434daa552ae/reports/c343f3cf-10f5-4df1-ab4b-17008f3050ee/689ae9f8380962dcd938?experience=power-bi) · [Two-page PDF](US-County-Rent-Burden-2024-ACS.pdf) · [Dashboard overview](dashboard-preview-1.png) · [County explorer](dashboard-preview-2.png)

This case study asks where a higher share of renter-occupied households spends at least 30% of household income on gross rent, and how that share sits alongside median gross rent and renter share. It is a cross-sectional description of the counties with published 2024 ACS 1-year estimates, not a ranking of all U.S. counties or a causal study.

## Report design

The overview combines four KPI cards, a top-ten state comparison, and a county scatter plot whose bubble size represents renter households. The state selector filters these visuals. The second page is a county explorer with a state selector, sortable county table, coverage KPIs, and interpretation notes. The PDF records the default all-county view; use the live report for filtering and visual interaction. Power BI access may require signing in to an authorized Microsoft account.

## Data and reproduction

The source is the U.S. Census Bureau's [2024 table-based ACS 1-year Summary File](https://www.census.gov/programs-surveys/acs/data/summary-file.2024.html). The script downloads the official [geography file](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/Geos20241YR.txt) and detailed tables [B25070](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b25070.dat) (gross rent as a percentage of income), [B25003](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b25003.dat) (tenure), and [B25064](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b25064.dat) (median gross rent). Run `python build_dataset.py` using Python 3.10+; no third-party package or API key is needed. The output CSV and `validation_summary.json` are reproducible from those files. Raw-file SHA-256 hashes are in the validation summary.

## Metric definitions

- **Rent burden 30%+**: B25070 categories 30–34.9%, 35–39.9%, 40–49.9%, and 50%+ combined, divided by renter-occupied units for which the rent-to-income percentage was computed. The `Not computed` category is excluded from the denominator.
- **Severe burden 50%+**: B25070 50%+ category divided by the same calculable denominator.
- **Renter share**: B25003 renter-occupied units divided by all occupied housing units.
- **Median gross rent**: B25064 estimate in dollars. It measures a different universe (units paying cash rent) and is not a household-level explanation for burden.

The included panel has **855 counties** across the 50 states, DC, and Puerto Rico. The geography and tenure files contain 861 counties, but the B25070 file omits six; all six are named in `validation_summary.json`. Standard 1-year county estimates are published for counties with populations of about 65,000 or more, so smaller counties are outside this panel. See the Census Bureau's [2024 ACS 1-year coverage notes](https://www.census.gov/data/developers/data-sets/acs-1year.2024.html).

## Checked headline

The **median of the 855 county rent-burden rates is 50.15%**. Pooling the numerator and denominator across those *covered counties* gives **52.55%**. These answer different questions; neither is a U.S. national rate. The data are survey estimates with margins of error, so small differences in rankings should not be read as statistically meaningful. See [findings and interpretation](FINDINGS.md).

## Files

| File | Purpose |
| --- | --- |
| `build_dataset.py` | Downloads and validates Census table-based files |
| `acs_2024_county_rent_burden.csv` | Curated county-grain Power BI source |
| `validation_summary.json` | Source hashes, coverage, and reconciled metrics |
| `FINDINGS.md` | Descriptive findings and limitations |
| `US-County-Rent-Burden-2024-ACS.pdf` | Two-page report export |
| `dashboard-preview-1.png`, `dashboard-preview-2.png` | Page previews |

