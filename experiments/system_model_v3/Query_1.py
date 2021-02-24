import datetime
import os
import numpy as np
import click
import math
import dill

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables
from models.constants import RAY

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run import run_experiment
from experiments.utils import save_to_HDF5, batch, merge_parameter_sweep
from radcad.core import generate_parameter_sweep


sweeps = {
    'arbitrageur_considers_liquidation_ratio': [True,False],
    'rescale_target_price': [True, False]
}



params.update(sweeps)


SIMULATION_TIMESTEPS = 24 * 30 * 6
MONTE_CARLO_RUNS = 1

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
    'controller_enabled': [False],
    'liquidity_demand_shock': [False],
    'arbitrageur_considers_liquidation_ratio': [True,False]
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
experiment_folder = __file__.split('.py')[0]
print(experiment_folder)
results_id = now.isoformat()

if __name__ == '__main__':
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params, initial_state=state_variables)
