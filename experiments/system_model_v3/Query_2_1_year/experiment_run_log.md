
# Experiment on 2021-02-26T12:43:00.674217
* Passed: True
* Time: 14.618143061796824 minutes
* Results folder: /home/aclarkdata/repos/reflexer/experiments/system_model_v3/Query_2_1_year
* Results ID: 2021-02-26T12:43:00.674531
* Git Hash: d702f40

Exceptions:

```
                      exception  ...                                      initial_state
0                          None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1  ETH_delta=1312.6575978212907  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2                          None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3  ETH_delta=23159.507084132543  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[4 rows x 8 columns]
```

Experiment metrics:


****


* Number of timesteps: 8640 / 360.0 days
* Number of MC runs: 1
* Timestep duration: 0.004 seconds
* Control parameters: ['arbitrageur_considers_liquidation_ratio', 'rescale_target_price']
* Number of parameter combinations: 4
* Expected experiment duration: 2.3040000000000003 minutes / 0.038400000000000004 hours
    

```
sweeps={'arbitrageur_considers_liquidation_ratio': [True, False], 'rescale_target_price': [True, False]}
```

    