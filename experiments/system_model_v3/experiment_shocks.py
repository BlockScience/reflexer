import datetime
import os
import numpy as np

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run import run_experiment
from experiments.utils import save_to_HDF5


# exponents = np.linspace(-10, -1, 5)
# scales = list(range(-9, -1, 1))
# kp_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# exponents = np.linspace(-10, -1, 5)
# scales = list(range(1, 9, 1))
# ki_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# proportional term for the stability controller: units 1/USD
kp_sweep = [-1e-10, -1e-8, -1e-6, -1e-4, -1e-2, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]
# integral term for the stability controller: units 1/(USD*seconds)
ki_sweep = [-1e-10, -1e-8, -1e-6, -1e-4, -1e-2, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]

sweeps = {
    'kp': kp_sweep,
    'ki': ki_sweep,
}

SIMULATION_TIMESTEPS = 24 * 30 * 2 # Updated to two month horizon for shock tests
MONTE_CARLO_RUNS = 3 # Each MC run will map to different shock

# Configure sweep and update parameters
params_update, experiment_metrics = configure_experiment(sweeps, timesteps=SIMULATION_TIMESTEPS)
params.update(params_update)

# Override parameters
params_override = {
    'controller_enabled': [True],
    'liquidation_ratio': [1.45],
    'interest_rate': [1.03],
    'liquidity_demand_enabled': [True],
    'arbitrageur_considers_liquidation_ratio': [True],
    'liquidity_demand_shock': [True], # Updated in this experiment to true, to allow setting of shocks
    'eth_price': [lambda run, timestep, df=None: 300],
    'liquidity_demand_events': [lambda run, timestep, df=None: 0],
    'token_swap_events': [lambda run, timestep, df=None: 0],
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

if __name__ == "__main__":
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params, initial_state=state_variables)
