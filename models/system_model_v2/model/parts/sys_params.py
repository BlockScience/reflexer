import numpy as np

import options as options
from constants import SPY, RAY

#assume
halflife = SPY / 52 #weeklong halflife
alpha = int(np.power(.5, float(1 / halflife)) * RAY)

# Enabled or disable APT tests - these tests bypass the APT ML model, for quick model validation
enable_apt_tests = False

apt_tests = [
        {
            # Enable or disable a specific test
            'enable': True,
            # Configure the test parameters
            'params': {
                # Optimal values to override the APT model suggestions
                'optimal_values': {
                    'v_1': lambda timestep=0: 1000,
                    'v_2 + v_3': lambda timestep=0: 500,
                    'u_1': lambda timestep=0: 100,
                    'u_2': lambda timestep=0: 50
                }
            }
        },
        # {
        #     'enable': False,
        #     'params': {
        #         'optimal_values': {
        #             'v_1': lambda timestep=0, df=simulation_results_df: \
        #                 simulation_results_df.iloc[timestep]['optimal_values'].get('v_1', historical_initial_state['v_1']),
        #             'v_2 + v_3': lambda timestep=0, df=simulation_results_df: \
        #                 simulation_results_df.iloc[timestep]['optimal_values'].get('v_2 + v_3', historical_initial_state['v_2 + v_3']),
        #             'u_1': lambda timestep=0, df=simulation_results_df: \
        #                 simulation_results_df.iloc[timestep]['optimal_values'].get('u_1', historical_initial_state['u_1']),
        #             'u_2': lambda timestep=0, df=simulation_results_df: \
        #                 simulation_results_df.iloc[timestep]['optimal_values'].get('u_2', historical_initial_state['u_2'])
        #         }
        #     }
        # },
        # {
        #     'enable': False,
        #     'params': {
        #         'optimal_values': {
        #             'v_1': lambda timestep=0: historical_initial_state['v_1'],
        #             'v_2 + v_3': lambda timestep=0: historical_initial_state['v_2 + v_3'],
        #             'u_1': lambda timestep=0: historical_initial_state['u_1'],
        #             'u_2': lambda timestep=0: historical_initial_state['u_2']
        #         }
        #     }
        # },
        # {
        #     'enable': False,
        #     'params': {
        #         'optimal_values': {
        #             'v_1': lambda timestep=0: 500,
        #             'v_2 + v_3': lambda timestep=0: 1000,
        #             'u_1': lambda timestep=0: 50,
        #             'u_2': lambda timestep=0: 100
        #         }
        #     }
        # }
]

params = {
    'test': apt_tests if enable_apt_tests else [{'enable': False}],
    'debug': [True], # Print debug messages (see APT model)
    'raise_on_assert': [False], # See assert_log() in utils.py
    'free_memory_states': [['cdps', 'events']],
    'expected_blocktime': [15], #seconds
    'minumum_control_period': [lambda _timestep: 3600], #seconds
    'expected_control_delay': [lambda _timestep: 1200], #seconds
    'derivative_smoothing': [1], #unitless
    'debt_market_std':[.001], #defined price units per hour
    'kp': [-1.5e-6], #proportional term for the stability controller: units 1/USD
    'ki': [lambda control_period=3600: 0 / control_period], #integral term for the stability controller: units 1/(USD*seconds)
    'kp-star': [-0.5866], #proportional term for the market process: unitless
    'ki-star': [lambda control_period=3600: 0.0032 / control_period], #integral term for the market process to target price: units 1/seconds 
    'kd-star': [lambda control_period=3600: 0.4858 * control_period], #derivative term for the market process to target price: units seconds
    'kp-hat': [0.6923], #proportional term for the market process to the debt price: unitless
    'ki-hat': [lambda control_period=3600: 0.0841 / control_period], #integral term for the market process to the debt price: units 1/seconds
    'kd-hat': [lambda control_period=3600: -0.3155 * control_period], #derivative term for the market process to the debt price: units seconds
    'k0': [0.2055], #intercept for the market model: unit USD
    'k-autoreg-1': [0.7922], #autoregressive term for the market model: unitless
    'alpha': [alpha], #in 1/RAY
    'error_term': [lambda target, measured: target - measured],
    options.DebtPriceSource.__name__: [options.DebtPriceSource.DEFAULT.value],
    options.IntegralType.__name__: [options.IntegralType.LEAKY.value],
    options.MarketPriceSource.__name__: [options.MarketPriceSource.DEFAULT.value],
    'controller_enabled': [True],
    'delta_output': [lambda state, timestep: 0],
    #'market_price': [lambda timestep: 2.0],
    # APT model
    'use_APT_ML_model': [True],
    'freeze_feature_vector': [False], # Use the same initial state as the feature vector for each timestep
    'interest_rate': [1.0], # Real-world expected interest rate, for determining profitable arbitrage opportunities
    # APT OLS model
    'alpha_0': [0],
    'alpha_1': [1],
    'beta_0': [1.0003953223600617],
    'beta_1': [0.6756295152422528],
    'beta_2': [3.86810578185312e-06],
    # CDP parameters
    'new_cdp_proportion': [0.5], # Proportion of v_1 or u_1 (collateral locked or debt drawn) used to create new CDPs 
    'new_cdp_collateral': [1000], # The average CDP collateral for opening a CDP
    'liquidation_buffer': [2.0], # multiplier applied to CDP collateral by users
    # Average CDP duration == 3 months: https://www.placeholder.vc/blog/2019/3/1/maker-network-report
    # The tuning of this parameter is probably off the average, because we don't have the CDP size distribution matched yet,
    # so although the individual CDPs could have an average debt age of 3 months, the larger CDPs likely had a longer debt age.
    'average_debt_age': [3 * (30 * 24 * 3600)], # delta t (seconds)
}
