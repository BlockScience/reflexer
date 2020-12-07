import papermill as pm
import multiprocessing
import os
import argparse
import json
from datetime import datetime


def run_papermill(parameters):
    ''' Function to run notebook(s) in paralell using papermill.
    '''

    simulation_directory = parameters['simulation_directory']
    simulation_id = parameters['simulation_id']

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
        parameters=parameters
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
        parameters=parameters
    )

    print(f'Simulation {simulation_directory}/{simulation_id} analysis complete')

if __name__ == '__main__':
    parameters = {'simulation_directory': 'simulations/debt_market' , 'simulation_id': str(datetime.now())}
    p = multiprocessing.Process(
        target=run_papermill,
        args=(parameters,)
    )
    p.start()
