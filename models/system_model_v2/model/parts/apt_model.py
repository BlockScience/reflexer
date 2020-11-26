import pandas as pd
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
from scipy.optimize import root, show_options, newton
import numpy as np
import seaborn as sns
import pickle

from .utils import get_feature

features = ['beta', 'Q', 'v_1', 'v_2 + v_3', 
                    'D_1', 'u_1', 'u_2', 'u_3', 'u_2 + u_3', 
                    'D_2', 'w_1', 'w_2', 'w_3', 'w_2 + w_3',
                    'D']

def p_apt_model(params, substep, state_history, state):
    func = params['G_OLS']
    
    feature_0 = get_feature(state_history, index=0)
    #feature_0 = get_feature(state_history)
    
    interest_rate = params['interest_rate']
    
    eth_price = state['eth_price']
    try:
        eth_p_mean = np.mean([x[-1]['eth_price'] for x in state_history[1:]])
    except IndexError as e:
        print(e)
        eth_p_mean = state['eth_price']

    #eth_returns = ((eth_price - eth_price.shift(1))/eth_price).to_numpy().flatten()
    eth_return = state['eth_return']
    try:
        eth_returns = [x[-1]['eth_return'] for x in state_history[1:]]
        eth_returns_mean = np.mean(eth_returns)
    except IndexError as e:
        print(e)
        eth_returns_mean = eth_return
    
    p = state['market_price']
    
    try:
        mar_p_mean = np.mean([x[-1]['market_price'] for x in state_history[1:]])
    except IndexError as e:
        print(e)
        mar_p_mean = p
    
    # assign CDP levers in response to disequilibrium
    # remember: unexpected realized ETH price increase *lowers* expected return!
    rising_eth = eth_return < eth_returns_mean
    if rising_eth:
        # price of ETH has risen
        # mint new RAI ('u_1') & sell on secondary market, or
        # reduce collateral value ('v_2')
        optvars = ['u_1', 'v_2 + v_3']
    else:
        # price of ETH has fallen
        # repay RAI ('u_2') & buy on secondary market, or
        # increase collateral value ('v_1')
        optvars = ['u_2', 'v_1']
        
    alpha_0 = params['alpha_0']
    alpha_1 = params['alpha_1']
    beta_0 = params['beta_0']
    beta_1 = params['beta_1']
    beta_2 = params['beta_2']
        
    # find root of non-arbitrage condition
    p_expected = (1/alpha_1) * p * (interest_rate + beta_2 * (eth_p_mean - eth_price*interest_rate)
                                 + beta_1 * (mar_p_mean - p*interest_rate)
                 ) - (alpha_0/alpha_1)
    
    optindex = [features.index(i) for i in optvars]
    
    x0 = feature_0[:,optindex][0]

    #print('x0: ', x0)
    #print('optvars:', optvars)
    #print('p_expected: ', p_expected)
    
    try:
        x_star = newton(func, x0, args=(optindex, feature_0, p_expected))
        #print('xstar: ' ,x_star)
        # Feasibility check, non-negativity
        if any(x_star[x_star < 0]):
            x_star = x0
    except RuntimeError as e:
        # For OLS, usually indicates non-convergence after 50 iterations (default)
        # Indicates not feasible to update CDP for this price/feature combination
        # Default to historical values here
        print('Error: {}, default to historical values...'.format(e))
        x_star = x_0
    
    optimal_values = dict((var, x_star[i]) for i, var in enumerate(optvars))
    
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
    
    #print(optimal_values)
    
    v_1 = optimal_values.get('v_1', 0)
    v_2_v_3 = optimal_values.get('v_2 + v_3', 0)
    u_1 = optimal_values.get('u_1', 0)
    u_2 = optimal_values.get('u_2', 0)

    cdp_position_state = resolve_cdp_positions(params, state, {'rising_eth': rising_eth, 'v_1': v_1, 'v_2 + v_3': v_2_v_3, 'u_1': u_1, 'u_2': u_2})
    
    return {'p_expected': p_expected, **cdp_position_state}
    
def s_store_p_expected(params, substep, state_history, state, policy_input):
    return 'p_expected', policy_input['p_expected']
