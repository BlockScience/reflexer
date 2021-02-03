import numpy as np
import itertools


timestep_duration = 0.025 # seconds

def generate_params(sweeps):
    cartesian_product = list(itertools.product(*sweeps.values()))
    params = {key: [x[i] for x in cartesian_product] for i, key in enumerate(sweeps.keys())}
    return params

def configure(subset=False, timesteps=24*365):
    if subset:
        control_period = np.linspace(1 * 3600, 6 * 3600, 2) # Default: 3 hours
        kp = np.linspace(1e-10, 1e-4, 2) # Default: 1e-8
        ki = np.linspace(-1e-10, -1e-4, 2) # Default: -1e-10
        sweeps = {
            'control_period': control_period,
            'kp': kp,
            'ki': ki,
        }
    else:
        control_period = np.linspace(1 * 3600, 6 * 3600, 3) # Default: 3 hours
        kp = np.linspace(1e-10, 1e-4, 3) # Default: 1e-8
        ki = np.linspace(-1e-10, -1e-4, 3) # Default: -1e-10
        alpha = np.linspace(
            999998857063901981428416512,
            1000000000000000000000000000, # Disabled
            3
        )

        sweeps = {
            'control_period': control_period,
            'kp': kp,
            'ki': ki,
            'alpha': alpha
        }

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

if __name__ == "__main__":
    configure()
