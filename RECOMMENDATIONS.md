# Parameter Choice Recommendations

* Ideal Kp parameter value for launch: `-1.5e-6`
* Range of Kp parameters given KPI metrics (response time, stability, sensitivity, error): `-3e-06, -2e-06, -1e-06, -9e-07, -8e-07, -7e-07`

## Relevant Analysis and Resources

See `exports/shock_datasets` for raw Pandas dataframes.

See `exports/shock_analysis/v1`:
* Paramater choice analysis: `shock_analysis.ipynb`
* Shock metrics: for range of Kp parameters that meet KPIs
* Shock standard deviations: for range of Kp parameters that meet KPIs

See `notebook_solidity_validation.ipynb` for Solidity/cadCAD validation and error stats.

## Outputs for Kp `-1.5e-6`

### Shock Metrics

![](./exports/shock_analysis/v1/shock_metrics/kp_-1.5000E-06-ki_0.0000E+00.png)

### Shock Standard Deviation

![](./exports/shock_analysis/v1/shock_std/kp_-1.5000E-06-ki_0.0000E+00.png)

### Market Shock Response

![](./exports/shock_analysis/v1/plots/market.png)

### Regression Model Response

![](./exports/shock_analysis/v1/plots/regression.png)

### Solidity cadCAD Validation

![](./exports/shock_analysis/v1/plots/solidity-cadcad-market.png)

![](./exports/shock_analysis/v1/plots/solidity-cadcad-error.png)
