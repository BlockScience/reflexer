import datetime
import os
import json
import numpy as np

from models.system_model_v3.model.params.init import params

from experiments.system_model_v3.configure import configure_experiment
from experiments.system_model_v3.run_search import run_experiment
from experiments.utils import save_to_HDF5
from models.constants import SPY, RAY
from experiments.metrics import score

run_params = {'kp': [1e-08], 'ki': [-1e-06], 'kd': [0], 'alpha': [0.975 * RAY]}

SIMULATION_TIMESTEPS = 24 * 30 * 12
MONTE_CARLO_RUNS = 8

params.update(run_params)

experiment_metrics = f''' '''

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
    score = score(experiment_folder, results_id, params, MONTE_CARLO_RUNS, SIMULATION_TIMESTEPS)
    print(f" {score=}")
