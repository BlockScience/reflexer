import os
import math
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from sklearn.preprocessing import StandardScaler

from experiments.system_model_v3.post_process_search import post_process_results


def beta_degree_diff(beta1, beta2, unit=1):
    """
    >>> '%.2f' % beta_degree_diff(0, 1)
    '45.00'
    
    >>> '%.2f' % beta_degree_diff(0.2, 0.3)
    '5.39'

    """
    # cos alpha = 1 / h
    # c = (1 + b1**2) ** 0.5
    hyp1 = (unit + beta1**2) ** 0.5
    degree1 = math.degrees(math.asin(unit/hyp1))

    hyp2 = (unit + beta2**2) ** 0.5
    degree2 = math.degrees(math.asin(unit/hyp2))

    return abs(degree1 - degree2)


def score(experiment_folder, results_id, params, n_runs, timesteps):
    score = 0

    experiment_results = os.path.join(experiment_folder, 'experiment_results.hdf5')
    experiment_results_key = 'results_' + results_id
    df_raw = pd.read_hdf(experiment_results, experiment_results_key)
    df = post_process_results(df_raw, params, set_params=['kp', 'ki', 'kd', 'alpha'])

    # get initial prices and set APY
    initial_target_price = df['target_price'].iloc[0]
    initial_eth_price = df['eth_price'].iloc[0]
    df['apy'] = ((1 + df['target_rate']) ** (60*60*24*356) - 1) * 100

    # get last timesetp
    last_timestep = df['timestep'].iloc[-1]

    cv_ratios = []
    for i in range(1, n_runs + 1):
        target_sd = df.query("run == @i")['target_price'].std()
        target_mean = df.query("run == @i")['target_price'].mean()
        eth_sd = df.query("run == @i")['eth_price'].std()
        eth_mean = df.query("run == @i")['eth_price'].mean()

        target_cv = target_sd / target_mean
        eth_cv = eth_sd / eth_mean
        cv_ratios.append(target_cv/eth_cv)

    mean_cv_ratios = np.mean(cv_ratios)
    #print(f"{mean_cv_ratios=}")
    score += min(2, mean_cv_ratios)

    # how many didn't finish successfully
    n_finished = len(df.query("timestep == @last_timestep"))
    n_unfinished = n_runs - n_finished
    unfinished_pct = n_unfinished/n_runs
    
    #print(f"{unfinished_pct=}")
    score += 4 * (unfinished_pct)

    '''
    # stable final prices
    stable_final_price = df.query("timestep == @last_timestep & abs(target_price - @initial_target_price)/@initial_target_price < abs(eth_price-@initial_eth_price)/@initial_eth_price")
    stable_final_price_pct = len(stable_final_price) / MONTE_CARLO_RUNS
    score += 2 * (1. - stable_final_price_pct)
    '''

    degree_diffs = []
    for i in range(1, n_runs+1):
        scaler = StandardScaler()
        df_reg = df.query(f'run == @i')

        try:
            eth_price_scaled = scaler.fit_transform(df_reg['eth_price'].values.reshape(-1,1))
            target_price_scaled = scaler.fit_transform(df_reg['target_price'].values.reshape(-1,1))

            data = pd.DataFrame()
            data['eth_price_scaled'] = eth_price_scaled.flatten()
            data['target_price_scaled'] = target_price_scaled.flatten()
            data['timestep'] = df_reg['timestep']
            data.columns = ['eth_price_scaled', 'target_price_scaled', 'timestep']

            eth_result = sm.ols(formula="eth_price_scaled ~ timestep", data=data).fit()
            target_result = sm.ols(formula="target_price_scaled ~ timestep", data=data).fit()
            eth_coeff = eth_result.params[1]
            target_coeff = target_result.params[1]
            degree_diff = beta_degree_diff(eth_coeff, target_coeff)
            degree_diffs.append(min(1, degree_diff/10))
        except:
            degree_diffs.append(1)

    mean_degree_diffs = np.mean(degree_diffs)
    #print(f"{mean_degree_diffs=}")
    score += 2 * mean_degree_diffs

    stable_final_price = df.query("timestep == @last_timestep & abs(target_price - @initial_target_price)/@initial_target_price < abs(eth_price-@initial_eth_price)/@initial_eth_price")
    stable_final_price_pct = len(stable_final_price) / n_runs
    #print(f"{stable_final_price_pct=}")
    score += 2 * (1. - stable_final_price_pct)

    # Stable rates
    apy_too_high = (df['apy'].abs() > 99).sum()
    #apy_too_low = (df['apy'].abs() < 10).sum()
    #undesirable_apy_pct = (apy_too_high +  apy_too_low) / len(df)
    too_high_apy_pct = apy_too_high/len(df)

    #print(f"{too_high_apy_pct=}")
    score += 4 * too_high_apy_pct

    # stable intermediate prices
    unstable_inter_prices = df.query("""
    0.5*@initial_target_price > market_price or market_price >= 2*@initial_target_price or 0.5*@initial_target_price > target_price or target_price >= 2*@initial_target_price
    """)

    unstable_inter_prices_pct = len(unstable_inter_prices)/len(df)
    score += 4 * (unstable_inter_prices_pct)
    #print(f"{unstable_inter_prices_pct=}")

    df['squared_error'] = (df['market_price'] - df['target_price']) ** 2
    mse = df['squared_error'].mean()
    #print(f"{mse=}")
    score += min(100, 20 * mse)

    
    return score

if __name__ == "__main__":
    import doctest
    doctest.testmod()
