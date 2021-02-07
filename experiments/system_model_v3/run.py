from .configure import configure
from experiments.utils import save_to_HDF5, update_experiment_run_log
from experiments.system_model_v3.post_process import post_process_results

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

from models.system_model_v3.model.partial_state_update_blocks import partial_state_update_blocks
from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables

from models.system_model_v3.model.params.init import eth_price_df

import logging
import datetime
import subprocess
import time
import os
import pandas as pd


# Get experiment details
experiment_folder = os.path.dirname(__file__) # "experiments/system_model_v3"
hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
now = datetime.datetime.now()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename=f'{experiment_folder}/logs/{now.isoformat()}.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Set the number of simulation timesteps, with a maximum of `len(debt_market_df) - 1`
SIMULATION_TIMESTEPS = 10  # len(eth_price_df) - 1
MONTE_CARLO_RUNS = 1

# Update parameters
params_update, experiment_metrics = configure(timesteps=SIMULATION_TIMESTEPS, subset=True)
params.update(params_update)


passed = False
experiment_time = 0.0
exceptions = []
try:
    start = time.time()
    
    # Run experiment
    logging.info("Starting experiment")
    logging.debug(experiment_metrics)
    logging.debug(params)

    # Run cadCAD simulation
    model = Model(
        initial_state=state_variables,
        state_update_blocks=partial_state_update_blocks,
        params=params
    )
    simulation = Simulation(model=model, timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS)
    experiment = Experiment([simulation])
    experiment.engine = Engine(
        raise_exceptions=False,
        deepcopy=False,
    )
    experiment.after_experiment = lambda experiment: save_to_HDF5(experiment, experiment_folder + '/experiment_results.hdf5', 'experiment_check_controller_constant_bounds')
    experiment.run()
    
    exceptions = pd.DataFrame(experiment.exceptions)
    
    logging.debug(exceptions)
    logging.debug(df.info())

    passed = True
    logging.info("Experiment complete")
    end = time.time()
    experiment_time = end - start

    update_experiment_run_log(experiment_folder, passed, results_id, hash, exceptions, experiment_metrics, experiment_time)
except AssertionError as e:
    logging.info("Experiment failed")
    logging.error(e)

    update_experiment_run_log(experiment_folder, passed, results_id, hash, exceptions, experiment_metrics, experiment_time)
