import dill
import pandas as pd
import datetime
from types import LambdaType
import os


def save_to_HDF5(experiment, store_file_name, store_key, now):
    store = pd.HDFStore(store_file_name)
    store.put(f'results_{store_key}', pd.DataFrame(experiment.results))
    exceptions = pd.DataFrame(experiment.exceptions)
    exceptions['parameters'] = exceptions['parameters'].to_json()
    store.put(f'exceptions_{store_key}', exceptions)
    store.get_storer(f'results_{store_key}').attrs.metadata = {
        'date': now.isoformat()
    }
    store.get_storer(f'exceptions_{store_key}').attrs.metadata = {
        'date': now.isoformat()
    }
    store.close()
    print(f"Saved experiment results to HDF5 store file {store_file_name} with key {store_key}")

def update_experiment_run_log(experiment_folder, passed, results_id, hash, exceptions, experiment_metrics, experiment_time, now):
    experiment_run_log = f'''
# Experiment on {now.isoformat()}
* Passed: {passed}
* Time: {experiment_time / 60} minutes
* Results folder: {experiment_folder}
* Results ID: {results_id}
* Git Hash: {hash}

Exceptions:

```
{exceptions}
```

Experiment metrics:
{experiment_metrics}
    '''

    log_file = f'{experiment_folder}/experiment_run_log.md'
    if not os.path.exists(log_file):
        os.mknod(log_file)

    with open(log_file, 'r') as original: experiment_run_log_orig = original.read()
    with open(log_file, 'w') as modified: modified.write(experiment_run_log + experiment_run_log_orig)
