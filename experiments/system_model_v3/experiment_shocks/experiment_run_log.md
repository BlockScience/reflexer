
# Experiment on 2021-02-08T23:20:54.834274
* Passed: True
* Time: 0.4040114680926005 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T23:20:54.834451
* Git Hash: 417efc1

Exceptions:

```
                                 exception  ...                                      initial_state
0  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[5 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 1
* Number of parameter combinations: 1
* Expected experiment duration: 0.096 minutes / 0.0016 hours

## Notes

* Increased ETH price shock from 10% to 30%
* Remained stable, see outputs
* Next step: expand parameter search again, higher resolution sweep

# Experiment on 2021-02-08T22:54:43.005715
* Passed: True
* Time: 0.40724543333053587 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T22:54:43.005952
* Git Hash: 417efc1

Exceptions:

```
                                 exception  ...                                      initial_state
0  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4  underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[5 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 1
* Number of parameter combinations: 1
* Expected experiment duration: 0.096 minutes / 0.0016 hours

## Notes

* kp=1e-6 and ki=-1e-8 remained stable during shock tests
* Previous experiments run with 30% shock; reduced to 10% for this experiment
* Investigate effect of initial conditions, and how to initialize states using parameters
* See output plots, named with ID

# Experiment on 2021-02-08T20:05:35.826999
* Passed: True
* Time: 1.6832241972287496 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T20:05:35.827550
* Git Hash: 417efc1

Exceptions:

```
                                             exception  ...                                      initial_state
0              underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                 ...  ...                                                ...
175  ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
176  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
177  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
178  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
179  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[180 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 6
* Number of parameter combinations: 36
* Expected experiment duration: 3.4560000000000004 minutes / 0.057600000000000005 hours
    
    
# Experiment on 2021-02-08T19:45:15.538308
* Passed: True
* Time: 1.7803827762603759 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_shocks
* Results ID: 2021-02-08T19:45:15.538863
* Git Hash: 417efc1

Exceptions:

```
                                             exception  ...                                      initial_state
0              underflow encountered in double_scalars  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4    ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                                 ...  ...                                                ...
175  ('InvalidSecondaryMarketDeltaException', ('Inv...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
176  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
177  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
178  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
179  ('NegativeBalanceException', ('NegativeBalance...  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[180 rows x 7 columns]
```

Experiment metrics:

* Number of timesteps: 1440 / 60.0 days
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki']
* Approx. number of values per parameter: 6
* Number of parameter combinations: 36
* Expected experiment duration: 3.4560000000000004 minutes / 0.057600000000000005 hours
    
    
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
    
    