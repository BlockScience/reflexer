import pandas as pd
import dill
import datetime


def save_experiment_results(results_id, df, params, experiment_folder):
    now = datetime.datetime.now()

    # store in hdf5 file format 
    store_file = f'{experiment_folder}/results/results.hdf5'
    store_data = pd.HDFStore(store_file)

    # data
    store_data.put(results_id, df)

    # including metadata
    metadata = {'experiment_folder': experiment_folder, 'date': now.isoformat(), 'params': dill.dumps(params)}
    
    # getting attributes
    store_data.get_storer(results_id).attrs.metadata = metadata
    
    # closing the store_data 
    store_data.close() 
    
    # getting data 
    with pd.HDFStore(store_file) as store_data:
        keys = store_data.keys()
        data = store_data[results_id]
        metadata = store_data.get_storer(results_id).attrs.metadata

    return keys
