import datetime
import os
import numpy as np

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run import run_experiment
from experiments.utils import save_to_HDF5


# proportional term for the stability controller: units 1/USD
kp_sweep = [1e-6/3, 1e-6, 3*1e-6] # TODO: update with edge cases
# integral term for the stability controller: units 1/(USD*seconds)
ki_sweep = [-1e-9/3, -1e-9, 3*-1e-9] # TODO: update with edge cases

sweeps = {
    'kp': kp_sweep,
    'ki': ki_sweep,
    'liquidity_demand_shock': [False, True],
}

SIMULATION_TIMESTEPS = 24 * 30 * 6 # 6 months
MONTE_CARLO_RUNS = 10 # Stochastic processes for ETH price and liquidity demand

# Configure sweep and update parameters
params_update, experiment_metrics = configure_experiment(sweeps, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS)
params.update(params_update)

experiment_metrics = f'''
{experiment_metrics}

```
{kp_sweep=}
{ki_sweep=}
```
'''

# Override parameters
params_override = {
    'liquidation_ratio': [1.45],
    'interest_rate': [1.03],
    'liquidity_demand_enabled': [True],
    'arbitrageur_considers_liquidation_ratio': [True],
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

# if __name__ == "__main__":
#     run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params, initial_state=state_variables)
