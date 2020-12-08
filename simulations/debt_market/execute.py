import papermill as pm
import multiprocessing
import os
import argparse
import json
from datetime import datetime


def run_papermill(config):
    ''' Function to run notebook(s) in paralell using papermill.
    '''

    simulation_directory = config['simulation_directory']
    simulation_id = config['simulation_id']

    os.makedirs(f'{simulation_directory}/results/{simulation_id}', exist_ok=True)

    print(f'Running simulation {simulation_directory}/{simulation_id}')

    notebook = f'''{simulation_directory}/simulation_notebook_template.ipynb'''
    generate_notebook_cmd = f'''cat {simulation_directory}/simulation_notebook_template.py |
    jupytext --from py:percent --to ipynb --set-kernel - > {notebook}
    '''
    os.system(generate_notebook_cmd)
    
    output_path = f'''{simulation_directory}/results/{simulation_id}/simulation_notebook.ipynb'''

    # run notebook using papermill
    pm.execute_notebook(
        notebook,
        output_path,
        parameters=config,
        log_output=True
    )

    print(f'Analysing simulation {simulation_directory}/{simulation_id}')

    notebook = f'''{simulation_directory}/simulation_analysis_notebook_template.ipynb'''
    generate_notebook_cmd = f'''cat {simulation_directory}/simulation_analysis_notebook_template.py |
    jupytext --from py:percent --to ipynb --set-kernel - > {notebook}
    '''
    os.system(generate_notebook_cmd)
    
    output_path = f'''{simulation_directory}/results/{simulation_id}/simulation_analysis_notebook.ipynb'''

    pm.execute_notebook(
        notebook,
        output_path,
        parameters=config,
        log_output=True
    )

    print(f'Simulation {simulation_directory}/{simulation_id} analysis complete')

if __name__ == '__main__':
    now = datetime.now()

    config = {
        'simulation_directory': 'simulations/debt_market' ,
        'simulation_id': f'controller_enabled_{now}',
        # Overrides model parameters
        'execution_parameters': {
            'controller_enabled': [True]
        }
    }
    p = multiprocessing.Process(
        target=run_papermill,
        args=(config,)
    )
    p.start()
