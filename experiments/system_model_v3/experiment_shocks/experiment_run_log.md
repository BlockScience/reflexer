
# Experiment on 2021-02-08T19:20:25.052766
* Passed: True
* Time: 1.4365687449773152 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T19:20:25.053328
* Git Hash: 4c2e4f7

Exceptions:

```
                                             exception  ...                                      initial_state
0              underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                 ...  ...                                                ...
139  ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
140  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
141  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
142  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
143  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[144 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 6
* Number of parameter combinations: 36
* Expected experiment duration: 3.4560000000000004 minutes / 0.057600000000000005 hours

## Notes

* The liquidation ratio is used to initialize state. For this reason, a state initialization method is needed when sweeping these parameters.
* Updating state liquidation ratio on next experiment.
* Reducing shock size, introducing base case of stable 300 dollar ETH price 

# Experiment on 2021-02-08T19:11:14.828985
* Passed: True
* Time: 1.0491442600886027 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T19:11:14.829535
* Git Hash: 4c2e4f7

Exceptions:

```
                                             exception  ...                                      initial_state
0    ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                 ...  ...                                                ...
139                            list index out of range  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
140                            list index out of range  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
141                            list index out of range  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
142                            list index out of range  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
143                            list index out of range  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[144 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 6
* Number of parameter combinations: 36
* Expected experiment duration: 3.4560000000000004 minutes / 0.057600000000000005 hours
    
    