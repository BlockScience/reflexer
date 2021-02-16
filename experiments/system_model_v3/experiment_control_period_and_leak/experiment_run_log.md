
# Experiment on 2021-02-10T08:43:25.676732
* Passed: True
* Time: 62.608404489358264 minutes
* Results folder: /home/ubuntu/reflexer/experiments/system_model_v3/experiment_control_period_and_leak
* Results ID: 2021-02-10T08:43:25.677821
* Git Hash: 1dfe23b

Exceptions:

```
    exception traceback  ...                                         parameters                                      initial_state
0        None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1        None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2        None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3        None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4        None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..        ...       ...  ...                                                ...                                                ...
400      None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
401      None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
402      None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
403      None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
404      None      None  ...  {'debug': False, 'raise_on_assert': True, 'fre...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[405 rows x 8 columns]
```

Experiment metrics:


* Number of timesteps: 1440 / 60.0 days
* Number of MC runs: 5
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki', 'control_period', 'alpha']
* Number of parameter combinations: 81
* Expected experiment duration: 38.88 minutes / 0.648 hours
    

```
kp_sweep=array([2.e-07, 1.e-06, 5.e-06])
ki_sweep=array([-5.e-09, -1.e-09, -2.e-10])
```

## Notes

* Clear effect of alpha in non-stochastic experiment, where windup occurs
* Controller becomes unstable / price runs away in some cases for 6 hour control period, retuning required
