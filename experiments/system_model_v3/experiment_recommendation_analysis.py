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


SIMULATION_TIMESTEPS = 24 * 30 * 12
MONTE_CARLO_RUNS = 5

experiment_metrics = ""

# Override parameters
params_override = {
    'controller_enabled': [True],
    'kp': [2e-07, 1e-6, 2e-07, 1e-6, 2e-07*3, 2e-07*3],
    'ki': [-5.000000e-09, -5.000000e-09, 0, 0, -5.000000e-09, 0],
    'control_period': [3600 * 4], # seconds; must be multiple of cumulative time
    'liquidity_demand_shock': [False],
    'liquidation_ratio': [1.45],
    'liquidity_demand_enabled': [True],
    'alpha': [0.999*RAY], # in 1/RAY
    'interest_rate': [1.03],
    'arbitrageur_considers_liquidation_ratio': [True],
    'rescale_target_price': [True],
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

if __name__ == '__main__':
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params, initial_state=state_variables)
