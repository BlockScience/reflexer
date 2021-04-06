import datetime
import os
import numpy as np

from models.system_model_v3.model.params.init import params

from experiments.system_model_v3.configure import generate_params, configure_experiment
#from experiments.system_model_v3.run import run_experiment
from experiments.system_model_v3.run_search import run_experiment
from experiments.utils import save_to_HDF5
from models.constants import SPY, RAY


exponents = np.linspace(-10, -6, 5)
scales = list(range(-9, 10, 1))
kp_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

exponents = np.linspace(-10, -6, 5)
scales = list(range(-9, 10, 1))
ki_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# Close
kp_sweep = [7.935707605565458e-05]
ki_sweep = [6.70247183991102e-05]
kd_sweep = [-9.01062284066631e-05]
alpha_sweep = [0.06096201979295979 * RAY]

sweeps = {
    'kp': kp_sweep,
    'ki': ki_sweep,
    'kd': kd_sweep,
    'alpha': alpha_sweep,
}

SIMULATION_TIMESTEPS = 24 * 30 * 12
MONTE_CARLO_RUNS = 2

# Configure sweep and update parameters
params_update, experiment_metrics = configure_experiment(sweeps, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS)
params.update(params_update)
print(params_update)

experiment_metrics = f'''
{experiment_metrics}

```
{kp_sweep=}
{ki_sweep=}
{kd_sweep=}
{alpha_sweep=}
```
'''

# Override parameters
params_override = {
    'controller_enabled': [True],
    'liquidation_ratio': [1.45],
    'interest_rate': [1.03],
    'liquidity_demand_enabled': [True],
    'arbitrageur_considers_liquidation_ratio': [True],
    'liquidity_demand_shock': [False],
    'trader_market_premium': [1.05],
    'price_trader_bound': [0.20],
    'rate_trader_apy_bound': [60]
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

if __name__ == "__main__":
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params)
