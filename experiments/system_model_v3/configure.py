import numpy as np
import itertools


timestep_duration = 0.004 # seconds

def generate_params(sweeps):
    cartesian_product = list(itertools.product(*sweeps.values()))
    params = {key: [x[i] for x in cartesian_product] for i, key in enumerate(sweeps.keys())}
    return params

def configure_experiment(sweeps: dict, timesteps=24*30*6):
    params = generate_params(sweeps)
    param_sweeps = len(params[next(iter(params))])
    param_values = len(sweeps[next(iter(sweeps))])

    experiment_metrics = f'''
* Number of timesteps: {timesteps} / {timesteps / 24} days
* Timestep duration: {timestep_duration} seconds
* Control parameters: {list(params.keys())}
* Approx. number of values per parameter: {param_values}
* Number of parameter combinations: {param_sweeps}
* Expected experiment duration: {param_sweeps * timesteps * timestep_duration / 60} minutes / {param_sweeps * timesteps * timestep_duration / 60 / 60} hours
    '''
    print (experiment_metrics)

    return params, experiment_metrics
