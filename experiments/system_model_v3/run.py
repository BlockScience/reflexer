from .configure import params, experiment_metrics

import logging
import datetime
import subprocess
import time
import os

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

results_id = f'{hash}_{now.year}_{now.month}_{now.day}T{str(now.timestamp()).replace(".", "_")}'

# # store in hdf5 file format 
# store_file = './exports/system_model_v3/results.hdf5'
# storedata = pd.HDFStore(store_file) 

# # data
# store_key = f'raw_results_system_model_v3_{str(label)}_{now.year}_{now.month}_{now.day}T{str(now.timestamp()).replace(".", "_")}'
# storedata.put(store_key, simulation_result) 

# # including metadata
# metadata = {'date': now.isoformat(), 'params': dill.dumps(params_update) }
  
# # getting attributes
# storedata.get_storer(store_key).attrs.metadata = metadata 
  
# # closing the storedata 
# storedata.close() 
  
# # getting data 
# with pd.HDFStore(store_file) as storedata:
#     data = storedata[store_key]
#     metadata = storedata.get_storer(store_key).attrs.metadata

passed = False
experiment_time = 0.0
try:
    start = time.time()
    
    # Run experiment
    logging.info("Starting experiment")
    logging.debug(experiment_metrics)
    logging.debug(params)
    
    passed = True

    logging.info("Experiment complete")
    
    end = time.time()
    experiment_time = end - start
except AssertionError as e:
    print(e)

experiment_run_log = f'''
# Experiment on {now.isoformat()}
* Passed: {passed}
* Time: {experiment_time / 60} minutes
* Results ID: {results_id}
* Git Hash: {hash}

```
{experiment_metrics}
```
'''

with open(f'{experiment_folder}/experiment_run_log.md', 'r') as original: experiment_run_log_orig = original.read()
with open(f'{experiment_folder}/experiment_run_log.md', 'w') as modified: modified.write(experiment_run_log + experiment_run_log_orig)
