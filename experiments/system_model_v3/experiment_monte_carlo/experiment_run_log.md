
# Experiment on 2021-02-10T23:03:46.416477
* Passed: True
* Time: 27.09282350540161 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_monte_carlo
* Results ID: 2021-02-10T23:03:46.418089_0
* Git Hash: 1dfe23b

Exceptions:

```
                       exception  ...                                      initial_state
0   ETH_delta=2968.3462371722376  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    ETH_delta=767.8686961652883  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    ETH_delta=935.2883564568504  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3   ETH_delta=-856.0763679107223  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4                           None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                           ...  ...                                                ...
70               Arb. CDP closed  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
71                          None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
72                          None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
73                          None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
74               Arb. CDP closed  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[75 rows x 8 columns]
```

Experiment metrics:


**Parameter subsets are spread across multiple experiments, with the results ID having the same timestamp and an extension for the subset index.**


* Number of timesteps: 4320 / 180.0 days
* Number of MC runs: 5
* Timestep duration: 0.004 seconds
* Control parameters: ['controller_enabled', 'kp', 'ki', 'control_period', 'liquidity_demand_shock', 'arbitrageur_considers_liquidation_ratio', 'rescale_target_price']
* Number of parameter combinations: 432
* Expected experiment duration: 622.08 minutes / 10.368 hours
    

```
sweeps={'controller_enabled': [True, False], 'kp': array([2.e-07, 1.e-06, 5.e-06]), 'ki': array([-5.e-09, -1.e-09, -2.e-10]), 'control_period': [3600, 14400, 25200], 'liquidity_demand_shock': [True, False], 'arbitrageur_considers_liquidation_ratio': [True, False], 'rescale_target_price': [True, False]}
```

    
# Experiment on 2021-02-10T22:33:29.788818
* Passed: True
* Time: 24.314744869867962 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_monte_carlo
* Results ID: 2021-02-10T22:33:29.790394_0
* Git Hash: 1dfe23b

Exceptions:

```
                                            exception  ...                                      initial_state
0                        ETH_delta=2968.3462371722376  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1                         ETH_delta=767.8686961652883  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2   open         1.000000e+00\ntime         0.0000...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3   open         1.000000e+00\ntime         0.0000...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4                                                None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                ...  ...                                                ...
70  open         1.000000e+00\ntime         0.0000...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
71  open         1.000000e+00\ntime         0.0000...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
72                                               None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
73                                               None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
74                                    Arb. CDP closed  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[75 rows x 8 columns]
```

Experiment metrics:


**Parameter subsets are spread across multiple experiments, with the results ID having the same timestamp and an extension for the subset index.**


* Number of timesteps: 4320 / 180.0 days
* Number of MC runs: 5
* Timestep duration: 0.004 seconds
* Control parameters: ['controller_enabled', 'kp', 'ki', 'control_period', 'liquidity_demand_shock', 'arbitrageur_considers_liquidation_ratio', 'rescale_target_price']
* Number of parameter combinations: 432
* Expected experiment duration: 622.08 minutes / 10.368 hours
    

```
sweeps={'controller_enabled': [True, False], 'kp': array([2.e-07, 1.e-06, 5.e-06]), 'ki': array([-5.e-09, -1.e-09, -2.e-10]), 'control_period': [3600, 14400, 25200], 'liquidity_demand_shock': [True, False], 'arbitrageur_considers_liquidation_ratio': [True, False], 'rescale_target_price': [True, False]}
```

    