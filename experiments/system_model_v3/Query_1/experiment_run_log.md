
# Experiment on 2021-02-24T14:20:44.999693
* Passed: True
* Time: 4.371484533945719 minutes
* Results folder: /home/aclarkdata/repos/reflexer/experiments/system_model_v3/Query_1
* Results ID: 2021-02-24T14:20:44.999979
* Git Hash: 63fca90

Exceptions:

```
  exception  ...                                      initial_state
0      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[4 rows x 8 columns]
```

Experiment metrics:


**Parameter subsets are spread across multiple experiments, with the results ID having the same timestamp and an extension for the subset index.**


* Number of timesteps: 4320 / 180.0 days
* Number of MC runs: 1
* Timestep duration: 0.004 seconds
* Control parameters: ['arbitrageur_considers_liquidation_ratio', 'rescale_target_price']
* Number of parameter combinations: 4
* Expected experiment duration: 1.1520000000000001 minutes / 0.019200000000000002 hours
    

```
sweeps={'arbitrageur_considers_liquidation_ratio': [True, False], 'rescale_target_price': [True, False]}
```

    