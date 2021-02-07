import datetime
import os

from models.system_model_v3.model.params.init import params

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run import run_experiment
from experiments.utils import save_to_HDF5


# exponents = list(range(-7, -5, 2))
# scales = list(range(-9, -1, 1))
# kp_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# exponents = list(range(-7, -5, 2))
# scales = list(range(1, 9, 1))
# ki_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# proportional term for the stability controller: units 1/USD
kp_sweep = [1e-20, 1e-15, 1e-10, 1e-5, 1e-1, 0, -1e-1, -1e-5, -1e-10, -1e-15, -1e-20]
# integral term for the stability controller: units 1/(USD*seconds)
ki_sweep = [1e-20, 1e-15, 1e-10, 1e-5, 1e-1, 0, -1e-1, -1e-5, -1e-10, -1e-15, -1e-20]

sweeps = {
    'kp': kp_sweep,
    'ki': ki_sweep,
}

# Configure sweep and update parameters
params_update, experiment_metrics = configure_experiment(sweeps, timesteps=24*30*6)
params.update(params_update)

# Override parameters
params_override = {
    'controller_enabled': [True],
    'liquidation_ratio': [1.5],
    'interest_rate': [1.03],
    'liquidity_demand_enabled': [True],
    'arbitrageur_considers_liquidation_ratio': [True],
    'liquidity_demand_shock': [False]
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
experiment_folder = os.path.dirname(__file__).split('.py')[0]
results_id = now.isoformat()

SIMULATION_TIMESTEPS = 24 * 7
MONTE_CARLO_RUNS = 1

if __name__ == "__main__":
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params)
