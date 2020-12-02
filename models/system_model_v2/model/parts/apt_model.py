from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from autosklearn.regression import AutoSklearnRegressor
from autosklearn.metrics import mean_squared_error as auto_mean_squared_error
from pprint import pprint
import matplotlib.pyplot as plt
import math, statistics
from functools import partial
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLSResults
from statsmodels.tsa.ar_model import AutoReg
from scipy.optimize import root, show_options, newton, minimize
import numpy as np
import seaborn as sns
import pickle
import time

from .utils import get_feature
from .debt_market import resolve_cdp_positions_unified

def p_resolve_p_expected(params, substep, state_history, state):
    debug = params['debug']

    eth_return = state['eth_return']
    eth_p_mean = params['eth_p_mean']
    mar_p_mean = params['mar_p_mean']
    eth_returns_mean = params['eth_returns_mean']
    p = state['market_price']
    interest_rate = params['interest_rate']
    
    try:
        eth_price = state_history[-1][-1]['eth_price']
    except IndexError as e:
        print(e)
        eth_price = state['eth_price']
                    
    # try:
    #     mar_p_mean = np.mean([x[-1]['market_price'] for x in state_history]) #[1:]
    # except IndexError as e:
    #     print(e)
    #     mar_p_mean = p

    alpha_0 = params['alpha_0']
    alpha_1 = params['alpha_1']
    beta_0 = params['beta_0']
    beta_1 = params['beta_1']
    beta_2 = params['beta_2']
        
    # find root of non-arbitrage condition
    p_expected = (1 / alpha_1) * p * (interest_rate + beta_2 * (eth_p_mean - eth_price * interest_rate)
                                 + beta_1 * (mar_p_mean - p * interest_rate)
                 ) - (alpha_0/alpha_1)
    
    if debug: print(f'p_expected terms: {alpha_1, p, interest_rate, beta_2, eth_p_mean, eth_price, beta_1, mar_p_mean, alpha_0, p_expected}')

    return {'p_expected': p_expected}

def s_store_p_expected(params, substep, state_history, state, policy_input):
    return 'p_expected', policy_input['p_expected']

def p_apt_model_unified(params, substep, state_history, state):
    start_time = time.time()
    debug = params['debug']
    if debug:
        print('##### APT model run #####')
        print(f'Timestep: {state["timestep"]}')

    use_APT_ML_model = params['use_APT_ML_model']
    func = params['root_function']
    bounds = params['bounds']
    optvars = params['optvars']
    features = params['features']

    p_expected = state['p_expected']
    
    if use_APT_ML_model:
        optindex = [features.index(i) for i in optvars]
        feature_0 = get_feature(state_history, features, index=(0 if params['freeze_feature_vector'] else -1))
    else:
        # add regression constant; this shifts index for optimal values
        optindex = [features.index(i) + 1 for i in optvars]
        # Set the index to zero to use the same feature vector for every step
        #feature_0 = get_feature(state_history, features, index=0)
        feature_0 = get_feature(state_history, features, index=(0 if params['freeze_feature_vector'] else -1))
        feature_0 = np.insert(feature_0, 0, 1, axis=1)
    if debug: print(feature_0)
    
    x0 = feature_0[:,optindex][0]

    print('x0: ', x0)
    print('optvars:', optvars)
    print('p_expected: ', p_expected)
    
    try:
        if use_APT_ML_model:
            results = minimize(func, x0, method='Powell', 
                args=(optindex, feature_0, p_expected),
                bounds = bounds,
                options={'disp':True}
            )
            if debug:
                print('Success:', results['success'])
                print('Message:', results['message'])
                print('Function value:', results['fun'])
            x_star = results['x']
        else:
            x_star = newton(func, x0, args=(optindex, feature_0, p_expected))
        # Feasibility check, non-negativity
        negindex = np.where(x_star < 0)[0]
        if len(negindex) > 0:
            if debug: print('negative root found, resetting')
            x_star[negindex] = x0[negindex]
    except RuntimeError as e:
        # For OLS, usually indicates non-convergence after 50 iterations (default)
        # Indicates not feasible to update CDP for this price/feature combination
        # Default to historical values here
        print('Error: {}, default to historical values...'.format(e))
        x_star = x0
    
    optimal_values = dict((var, x_star[i]) for i, var in enumerate(optvars))
    
    if debug:
        print(f'x_star: {x_star}')
        print(f'optimal_values: {optimal_values}')
    
    # EXTERNAL HANDLER: pass optimal values to CDP handler (here, as dict)
    # EXTERNAL HANDLER: receive new initial condition from CDP handler (as numpy array)
    # This is done automatically via state
    # _send_values_to_CDP(optimal_values)
    # feature_0 = _receive_values_from_CDP()
        
    # EXTERNAL HANDLER: pass updated CDP features & expected price to market
    # EXTERNAL HANDLER: receive price from market (possibly with demand shock)
    # _send_feature_to_market(feature_0)
    # _send_expected_price_to_market(p_expected)
    # p = _receive_price_from_market()
    
    v_1 = optimal_values.get('v_1', 0)
    v_2_v_3 = optimal_values.get('v_2 + v_3', 0)
    u_1 = optimal_values.get('u_1', 0)
    u_2 = optimal_values.get('u_2', 0)

    cdp_position_state = resolve_cdp_positions_unified(params, state, {'v_1': v_1, 'v_2 + v_3': v_2_v_3, 'u_1': u_1, 'u_2': u_2})
    
    print("--- %s seconds ---" % (time.time() - start_time))
    
    return {**cdp_position_state, 'optimal_values': optimal_values}

def s_store_optimal_values(params, substep, state_history, state, policy_input):
    return 'optimal_values', policy_input['optimal_values']
