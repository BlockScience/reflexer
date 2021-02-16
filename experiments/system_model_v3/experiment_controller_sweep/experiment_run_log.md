
# Experiment on 2021-02-08T15:29:00.423549
* Passed: True
* Time: 11.080405410130819 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_controller_sweep
* Results ID: 2021-02-08T15:29:00.423801
* Git Hash: af83ebd

Exceptions:

```
                                            exception  ...                                      initial_state
0                                                None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1   ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2   ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3   ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4              overflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                ...  ...                                                ...
95  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
96  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
97  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
98  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
99  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[100 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 4320 / 180.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 10
* Number of parameter combinations: 100
* Expected experiment duration: 28.8 minutes / 0.48000000000000004 hours

## Notes

* Outputs: 1_controller_parameter_sweep.png
* Stable Kp, Ki combinations:

```
kp = [-1e-10, -1e-10, -1e-10, -1e-08, -1e-08, -1e-08, 1e-10, 1e-10, 1e-10, 1e-08, 1e-08, 1e-08, 1e-06, 1e-06, 1e-06, 1e-06]
ki = [-1e-10, 1e-10, 1e-08, -1e-10, 1e-10, 1e-08, -1e-10, 1e-10, 1e-08, -1e-10, 1e-10, 1e-08, -1e-10, -1e-08, 1e-10, 1e-08]
```

* New center of region of stability for search: kp=1e-06 ki=-1e-08
* Prices run to near zero for majority of parameter combinations, see output
* Updating target price to 3.14 and liquidation ratio to 1.45 for next experiment

# Experiment

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
