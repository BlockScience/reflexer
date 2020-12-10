import papermill as pm
import multiprocessing
import os
import argparse
import json
from datetime import datetime
import itertools
import secrets


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
    simulation_timesteps = 10

    median_cdp_collateral = 2500
    mean_cdp_collateral = 50
    
    new_cdp_proportion = [0.25, 0.5, 0.75]
    new_cdp_collateral = [mean_cdp_collateral, median_cdp_collateral]
    
    cdp_sweep = list(itertools.product(new_cdp_proportion, new_cdp_collateral))

    new_cdp_proportion_sweep = [x[0] for x in cdp_sweep]
    new_cdp_collateral_sweep = [x[1] for x in cdp_sweep]

    print(new_cdp_proportion_sweep)
    print(new_cdp_collateral_sweep)

    for new_cdp_proportion, new_cdp_collateral in zip(new_cdp_proportion_sweep, new_cdp_collateral_sweep):
        config = {
            'simulation_directory': 'simulations/debt_market' ,
            'simulation_id': f'{now}_{secrets.token_hex(8)}_controller_disabled',
            'simulation_timesteps': simulation_timesteps,
            'parameter_ki': 0,
            # Overrides model parameters
            'execution_parameters': {
                'controller_enabled': [False],
                'new_cdp_proportion': [new_cdp_proportion],
                'new_cdp_collateral': [new_cdp_collateral],
            }
        }
        p = multiprocessing.Process(
            target=run_papermill,
            args=(config,)
        )
        p.start()

        kp = 5e-07
        ki = -1e-7

        config = {
            'simulation_directory': 'simulations/debt_market' ,
            'simulation_id': f'{now}_{secrets.token_hex(8)}_controller_enabled_kp_{kp}_ki_{ki}',
            'simulation_timesteps': simulation_timesteps,
            'parameter_ki': ki,
            # Overrides model parameters
            'execution_parameters': {
                'controller_enabled': [True],
                'kp': [kp], # -1.5e-6
                'new_cdp_proportion': [new_cdp_proportion],
                'new_cdp_collateral': [new_cdp_collateral],
                # Functions not serializable
                #'ki': [lambda control_period=3600: 0 / control_period],
            }
        }
        p = multiprocessing.Process(
            target=run_papermill,
            args=(config,)
        )
        p.start() 

        kp = 5e-07
        ki = 0

        config = {
            'simulation_directory': 'simulations/debt_market' ,
            'simulation_id': f'{now}_{secrets.token_hex(8)}_controller_enabled_kp_{kp}_ki_{ki}',
            'simulation_timesteps': simulation_timesteps,
            'parameter_ki': ki,
            # Overrides model parameters
            'execution_parameters': {
                'controller_enabled': [True],
                'kp': [kp], # -1.5e-6
                'new_cdp_proportion': [new_cdp_proportion],
                'new_cdp_collateral': [new_cdp_collateral],
                # Functions not serializable
                #'ki': [lambda control_period=3600: 0 / control_period],
            }
        }
        p = multiprocessing.Process(
            target=run_papermill,
            args=(config,)
        )
        p.start() 
