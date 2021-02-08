Experiment metadata:

```
params['controller_enabled']=[True]
params['kp']=[1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-20, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 1e-05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-05, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-10, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-15, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20, -1e-20]
params['ki']=[1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20, 1e-20, 1e-15, 1e-10, 1e-05, 0.1, 0, -0.1, -1e-05, -1e-10, -1e-15, -1e-20]
params['liquidation_ratio']=[1.5]
params['arbitrageur_considers_liquidation_ratio']=[True]
params['liquidity_demand_enabled']=[True]
params['liquidity_demand_shock']=[False]
params['liquidity_demand_max_percentage']=[0.1]
params['liquidity_demand_shock_percentage']=[0.5]
params['alpha']=[999998857063901981428416512]
state_variables['cdps'].to_dict()={'open': {0: 1}, 'time': {0: 0}, 'locked': {0: 51008.41058261749}, 'drawn': {0: 10000000.0}, 'wiped': {0: 0.0}, 'freed': {0: 0.0}, 'w_wiped': {0: 0.0}, 'dripped': {0: 0.0}, 'v_bitten': {0: 0.0}, 'u_bitten': {0: 0.0}, 'w_bitten': {0: 0.0}, 'arbitrage': {0: 1}}
```

# Notes

1. Sweep controller parameters for default conditions
2. Find regions of stability, filtering for substeps where: simulation completes
3. When simulation doesn't complete, analyse reason and add check