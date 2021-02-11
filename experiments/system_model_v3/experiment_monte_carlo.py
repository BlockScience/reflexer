import datetime
import os
import numpy as np
import click
import math

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables
from models.constants import RAY

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run import run_experiment
from experiments.utils import save_to_HDF5, batch, merge_parameter_sweep
from radcad.core import generate_parameter_sweep


# proportional term for the stability controller: units 1/USD
kp_sweep = np.unique(np.append(np.linspace(1e-6/5, 1e-6, 2), np.linspace(1e-6, 5e-6, 2)))
# integral term for the stability controller: units 1/(USD*seconds)
ki_sweep = np.unique(np.append(np.linspace(-1e-9/5, -1e-9, 2), np.linspace(-1e-9, -5e-9, 2)))

sweeps = {
    'controller_enabled': [True, False],
    'kp': kp_sweep,
    'ki': ki_sweep,
    'control_period': [3600 * 1, 3600 * 4, 3600 * 7], # seconds; must be multiple of cumulative time
    'liquidity_demand_shock': [True, False],
    'arbitrageur_considers_liquidation_ratio': [True, False],
    'rescale_target_price': [True, False],
}

SIMULATION_TIMESTEPS = 24 * 30 * 6
MONTE_CARLO_RUNS = 5

# Configure sweep and update parameters
params_update, experiment_metrics = configure_experiment(sweeps, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS)
params.update(params_update)

experiment_metrics = f'''

**Parameter subsets are spread across multiple experiments, with the results ID having the same timestamp and an extension for the subset index.**

{experiment_metrics}

```
{sweeps=}
```
'''

# Override parameters
params_override = {
    'liquidation_ratio': [1.45],
    'liquidity_demand_enabled': [True],
    'alpha': [0.999*RAY], # in 1/RAY
    'interest_rate': [1.03],
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

@click.command()
@click.option("--remote_count", default=1, help="Number of remote machines")
@click.option("--remote_index", default=1, help="Index of remote machine")
@click.option("--batch_size", default=15, help="Execution batch size")
def cli(remote_count, remote_index, batch_size):
    parameter_sweep = generate_parameter_sweep(params)
    parameter_sweep_len = len(parameter_sweep)
    remote_subset = list(batch(parameter_sweep, math.ceil(parameter_sweep_len / remote_count)))[remote_index - 1]

    for sweep_index, sweep_subset in enumerate(batch(remote_subset, batch_size)):
        print(f"Running sweep subset {sweep_index} of {int(len(parameter_sweep) / remote_count / batch_size)} on remote machine {remote_index} of {remote_count}")
        _params = merge_parameter_sweep(sweep_subset)
        run_experiment(f'{results_id}_{sweep_index}', experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=_params, initial_state=state_variables, ray=False)

if __name__ == '__main__':
    cli()
