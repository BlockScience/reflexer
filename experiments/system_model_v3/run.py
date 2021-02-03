from .configure import configure
from experiments.utils import save_experiment_results
from shared import run, configs, ConfigWrapper, system_model_v3

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables
from models.system_model_v3.model.params.init import env_process_df

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
results_id = f'{now.year}_{now.month}_{now.day}T{str(now.timestamp()).replace(".", "_")}'

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename=f'{experiment_folder}/logs/{now.isoformat()}.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Set the number of simulation timesteps, with a maximum of `len(debt_market_df) - 1`
SIMULATION_TIMESTEPS = 10  # len(env_process_df) - 1

# Update parameters
params_update, experiment_metrics = configure(timesteps=SIMULATION_TIMESTEPS, subset=True)
params.update(params_update)

# Create a wrapper for the model simulation, and update the existing parameters and initial state
system_simulation = ConfigWrapper(system_model_v3, T=range(SIMULATION_TIMESTEPS), M=params, initial_state=state_variables)


passed = False
experiment_time = 0.0
try:
    start = time.time()
    
    # Run experiment
    logging.info("Starting experiment")
    logging.debug(experiment_metrics)
    logging.debug(params)
    
    # Run cadCAD simulation
    del configs[:] # Clear any prior configs
    system_simulation.append() # Append the simulation config to the cadCAD `configs` list
    (simulation_result, _tensor_field, _sessions) = run(drop_midsteps=False) # Run the simulation
    df = pd.DataFrame(simulation_result)
    logging.debug(df.info())
    results = save_experiment_results(results_id, df, params_update, experiment_folder)
    assert results_id in results

    passed = True

    logging.info("Experiment complete")
    
    end = time.time()
    experiment_time = end - start
except AssertionError as e:
    logging.info("Experiment failed")
    logging.error(e)

experiment_run_log = f'''
# Experiment on {now.isoformat()}
* Passed: {passed}
* Time: {experiment_time / 60} minutes
* Results ID: {results_id}
* Git Hash: {hash}

Experiment metrics:
{experiment_metrics}
'''

with open(f'{experiment_folder}/experiment_run_log.md', 'r') as original: experiment_run_log_orig = original.read()
with open(f'{experiment_folder}/experiment_run_log.md', 'w') as modified: modified.write(experiment_run_log + experiment_run_log_orig)
