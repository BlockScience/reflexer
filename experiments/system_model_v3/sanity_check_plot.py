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


SIMULATION_TIMESTEPS = 8758 #len(eth_price_df) - 1
MONTE_CARLO_RUNS = 1



experiment_metrics = ""

# Override parameters
params_override = {
    'controller_enabled': [False],
    'liquidity_demand_shock': [False],
    'rescale_target_price': [True],
    'arbitrageur_considers_liquidation_ratio': [True]
}
params.update(params_override)

# Experiment details
now = datetime.datetime.now()
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
results_id = now.isoformat()

if __name__ == '__main__':
    run_experiment(results_id, experiment_folder, experiment_metrics, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=params, initial_state=state_variables)
