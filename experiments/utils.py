import pandas as pd
import dill
import datetime


def save_to_HDF5(experiment, store_file_name, store_key):
    now = datetime.datetime.now()
    store = pd.HDFStore(store_file_name)
    store.put(f'{store_key}_results', pd.DataFrame(experiment.results))
    store.put(f'{store_key}_exceptions', pd.DataFrame(experiment.exceptions))
    store.get_storer(store_key).attrs.metadata = {
        'date': now.isoformat()
    }
    store.close()
    print(f"Saved experiment results to HDF5 store file {store_file_name} with key {store_key}")

def update_experiment_run_log(experiment_folder, passed, results_id, hash, exceptions, experiment_metrics, experiment_time):
    now = datetime.datetime.now()

    experiment_run_log = f'''
# Experiment on {now.isoformat()}
* Passed: {passed}
* Time: {experiment_time / 60} minutes
* Results folder: {experiment_folder}
* Results ID: {results_id}
* Git Hash: {hash}

Exceptions:
{exceptions}

Experiment metrics:
{experiment_metrics}
    '''

    with open(f'{experiment_folder}/experiment_run_log.md', 'r+') as original: experiment_run_log_orig = original.read()
    with open(f'{experiment_folder}/experiment_run_log.md', 'w') as modified: modified.write(experiment_run_log + experiment_run_log_orig)
