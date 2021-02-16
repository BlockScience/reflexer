
# Experiment on 2021-02-09T23:51:42.951502
* Passed: True
* Time: 22.94438906908035 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_liquidation_ratio
* Results ID: 2021-02-09T23:51:42.952840
* Git Hash: 56ac6da

Exceptions:

```
    exception  ...                                      initial_state
0        None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1        None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2        None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3        None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4        None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..        ...  ...                                                ...
139      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
140      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
141      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
142      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
143      None  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[144 rows x 8 columns]
```

Experiment metrics:


* Number of timesteps: 1440 / 60.0 days
* Number of MC runs: 4
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki', 'rescale_target_price', 'arbitrageur_considers_liquidation_ratio']
* Number of parameter combinations: 36
* Expected experiment duration: 13.824000000000002 minutes / 0.23040000000000002 hours
    

```
kp_sweep=array([2.e-07, 1.e-06, 5.e-06])
ki_sweep=array([-5.e-09, -1.e-09, -2.e-10])
```

    
# Experiment on 2021-02-09T22:02:18.257620
* Passed: True
* Time: 0.055404810110727946 minutes
* Results folder: /home/bscholtz/workspace/reflexer/experiments/system_model_v3/experiment_liquidation_ratio
* Results ID: 2021-02-09T22:02:18.259338
* Git Hash: 56ac6da

Exceptions:

```
                               exception  ...                                      initial_state
0    assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
1    assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
2    assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
3    assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
4    assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
..                                   ...  ...                                                ...
395  assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
396  assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
397  assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
398  assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...
399  assignment destination is read-only  ...  {'cdp_metrics': {}, 'optimal_values': {}, 'sim...

[400 rows x 8 columns]
```

Experiment metrics:


* Number of timesteps: 1440 / 60.0 days
* Number of MC runs: 4
* Timestep duration: 0.004 seconds
* Control parameters: ['kp', 'ki', 'rescale_target_price', 'arbitrageur_considers_liquidation_ratio']
* Number of parameter combinations: 100
* Expected experiment duration: 38.4 minutes / 0.64 hours
    

```
kp_sweep=array([2.e-07, 6.e-07, 1.e-06, 3.e-06, 5.e-06])
ki_sweep=array([-5.e-09, -3.e-09, -1.e-09, -6.e-10, -2.e-10])
```

    