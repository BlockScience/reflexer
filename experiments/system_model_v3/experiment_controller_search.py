def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
warnings.filterwarnings("ignore")
import datetime
import itertools
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ray
from ray import tune
import hyperopt as hp
from ray.tune.suggest.hyperopt import HyperOptSearch
from ray.tune.suggest.bayesopt import BayesOptSearch
from ray.tune.suggest import ConcurrencyLimiter

from models.system_model_v3.model.params.init import params
from models.system_model_v3.model.state_variables.init import state_variables
from models.constants import SPY, RAY

from experiments.system_model_v3.run_search import run_experiment
from experiments.system_model_v3.configure import generate_params
from experiments.utils import save_to_HDF5
from experiments.metrics import score

SIMULATION_TIMESTEPS = 24 * 30 * 12
#SIMULATION_TIMESTEPS = 1300
MONTE_CARLO_RUNS = 8

experiment_metrics = f''' '''

# Override parameters
params_override = {
    'controller_enabled': [True],
    'liquidation_ratio': [1.45],
    'interest_rate': [1.03],
    'liquidity_demand_enabled': [True],
    'arbitrageur_considers_liquidation_ratio': [True],
    'liquidity_demand_shock': [False],
    'trader_market_premium': [1.05],
    'price_trader_bound': [0.20],
    'rate_trader_apy_bound': [60]

}
params.update(params_override)

# Experiment details
dir_path = os.path.dirname(os.path.realpath(__file__))
experiment_folder = __file__.split('.py')[0]
#results_id = now.isoformat()

ray.services.get_node_ip_address = lambda: '192.168.1.2'
ray._private.services.get_node_ip_address = lambda: '127.0.0.1'
ray.init()

def run_sims_mean(config):
    p = {
         'kp': [config['kp']],
         'ki': [config['ki']],
         'kd': [0],
         'alpha': [config['alpha'] * RAY]
        }

    these_params = params.copy()
    these_params.update(p)
    pool_balance = state_variables['RAI_balance']
    target_price = state_variables['target_price']
    scores = []
    for capital_pct in [0.125, 1.0, 5.0]: 
        for trader_premium in [1.05, 1.0, 0.95]: 
            these_params["trader_market_premium"] = [trader_premium]
            new_state_variables = state_variables.copy()
            capital_balance = capital_pct * pool_balance
            new_state_variables['price_trader_rai_balance'] = capital_balance / 2
            new_state_variables['rate_trader_rai_balance'] = capital_balance / 2
            new_state_variables['price_trader_usd_balance'] = new_state_variables['price_trader_rai_balance'] / target_price
            new_state_variables['rate_trader_usd_balance'] = new_state_variables['rate_trader_rai_balance'] / target_price

            results_id = datetime.datetime.now().isoformat()
            try:
                run_experiment(results_id, '.', experiment_metrics, #initial_state=new_state_variables,
                               timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=these_params)
            except Exception as e:
                print(e)
                failed_score = float("inf")
                #print(f"{config=}, {capital_pct=}, {failed_score=}")
                return failed_score

            sim_score = score(os.getcwd(), results_id, these_params, MONTE_CARLO_RUNS, SIMULATION_TIMESTEPS)
            #print(f"{pool_balance=}, {target_price=}")
            #print(f"{new_state_variables['rate_trader_rai_balance']=}, {new_state_variables['rate_trader_usd_balance']=}")
            #print(f"{new_state_variables['price_trader_rai_balance']=}, {new_state_variables['price_trader_usd_balance']=}, {capital_pct=}, {sim_score=}")
            scores.append(sim_score)

    mean_score = np.mean(scores)
    #print(f"{new_state_variables['price_trader_rai_balance']=}, {new_state_variables['price_trader_usd_balance']=}, {mean_score=}")
    return mean_score

def objective_mean(config):
    score = run_sims_mean(config)
    print(f"{config=}, {score=}")
    tune.report(iterations=1, score=score)

def objective(config):
    score = run_sims(config)
    print(f"{config=}, {score=}")
    tune.report(iterations=1, score=score)

def run_sims(config):
    # Hyperparameters
    p = {
         'kp': [1e-8],
         'ki': [config['ki']],
         'kd': [0],
         'alpha': [config['alpha'] * RAY]
        }

    these_params = params.copy()
    these_params.update(p)
    results_id = datetime.datetime.now().isoformat()
    try:
        run_experiment(results_id, '.', experiment_metrics,
                       timesteps=SIMULATION_TIMESTEPS, runs=MONTE_CARLO_RUNS, params=these_params)
    except:
        score = float("inf")
        print(f"{config=}, {score=}")
        return score

    score = score(os.getcwd(), results_id, these_params, MONTE_CARLO_RUNS, SIMULATION_TIMESTEPS)
    print(f"{config=}, {score=}")
    return score

if __name__ == "__main__":

    # Full PID
    config = {"kp": tune.uniform(1e-13, 1e-7),
             "ki": tune.uniform(1e-13, 1e-9),
             "kd": tune.uniform(1e-13, 1e-6),
             "alpha": tune.uniform(0.99999, 1)
            }

    # PosP, Neg I
    config = {"kp": tune.uniform(1e-7, 5e-7),
             "ki": tune.uniform(-9e-11, -1e-12),
             #"kd": tune.grid_search([0]),
             "alpha": tune.uniform(0.999, 1)
            }

    """
    config = {"kp": (1e-10, 1e-7),
             "ki": (-1e-7, -1e-10),
             #"kd": tune.grid_search([0]),
             "alpha": (0, 1)
            }
    """

    kp_sweep = np.linspace(config['kp'].lower, config['kp'].upper, 5)
    ki_sweep = np.linspace(config['ki'].lower, config['ki'].upper, 5)
    #kd_sweep = np.linspace(config['kd'].lower, config['kd'].upper, 10)
    alpha_sweep = np.linspace(config['alpha'].lower, config['alpha'].upper, 5)


    #Grid search
    exponents = np.linspace(-12, -4, 9)
    scales = [1, 3, 5, 7, 9]
    kp_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

    exponents = np.linspace(-12, -4, 9)
    scales = [-1, -3, -5, -7, -9]
    ki_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

    alpha_sweep = [0.999, 0.9999, 0.99999, 0.999999, 0.9999999]


    #assert len(kp_sweep) == len(ki_sweep) == len(alpha_sweep)
    #assert len(ki_sweep) == len(alpha_sweep)
    cartesian = itertools.product(kp_sweep, ki_sweep, alpha_sweep)

    initial_points = []
    for x in cartesian:
        point = {}
        point['kp'] = x[0]
        point['ki'] = x[1]
        #point['kd'] = x[2]
        point['alpha'] = x[2]

        if abs(point['ki']) > point['kp']/3600:
            continue
        initial_points.append(point)

    print(f"{len(initial_points)} initial points")

    for v in config.values():
        if isinstance(v, tuple):
            assert v[0] < v[1]
        else:
            assert v.lower < v.upper

    algo = HyperOptSearch(#config,
                          n_initial_points=30,
                          metric="score",
                          gamma=0.25,
                          points_to_evaluate=initial_points,
                          mode="min")

    """
    algo = BayesOptSearch(config,
                          random_search_steps=30,
                          random_state=43,
                          patience=1000,
                          metric="score",
                          mode="min",
                          skip_duplicate=True,
                          points_to_evaluate=initial_points,
                          utility_kwargs={"kind": "ucb", "kappa": 2.576, "kappa_decay": 1.0, "kappa_decay_delay": 0, "xi": 0.0})
    """

    #algo.optimizer._prime_queue(1000)
    algo = ConcurrencyLimiter(algo, max_concurrent=64)

    analysis = tune.run(
                    objective_mean,
                    config=config,
                    search_alg=algo,
                    #num_samples=3000,
                    num_samples=len(initial_points),
                    metric="score", 
                    mode="min",
                    verbose=1,
                    resources_per_trial={"cpu": 2},
                    stop={"training_iteration": 1}
                    )

    print("Best hyperparameters found were: ", analysis.best_config)

    dfs = analysis.trial_dataframes
    ax = None  # This plots everything on the same plot
    for d in dfs.values():
        ax = d.score.plot(ax=ax, legend=False)

    plt.show()

    #df = analysis.results_df
