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
    
    feature_0 = get_feature(state)
    
    interest_rate = params['interest_rate']
    
    eth_price = state['eth_price']
    try:
        eth_p_mean = np.mean(state_history[1:][-1][-1]['eth_price'])
    except IndexError as e:
        print(e)
        eth_p_mean = state['eth_price']

    #eth_returns = ((eth_price - eth_price.shift(1))/eth_price).to_numpy().flatten()
    eth_return = state['eth_return']
    try:
        eth_returns = state_history[1:][-1][-1]['eth_return']
        eth_returns_mean = np.mean(eth_returns)
    except IndexError as e:
        print(e)
        eth_returns_mean = eth_return
    
    p = state['market_price']
    
    try:
        mar_p_mean = np.mean(state_history[1:][-1][-1]['market_price'])
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
    
    print(optimal_values)
    
    v_1 = optimal_values.get('v_1', 0)
    u_1 = optimal_values.get('u_1', 0)
    u_2 = optimal_values.get('u_2', 0)
    v_2_v_3 = optimal_values.get('v_2 + v_3', 0)

    cdp_position_state = resolve_cdp_positions(params, state, {'rising_eth': rising_eth, 'v_1': v_1, 'u_1': u_1, 'u_2': u_2, 'v_2 + v_3': v_2_v_3})
    
    return {'p_expected': p_expected, **cdp_position_state}
    
def s_store_p_expected(params, substep, state_history, state, policy_input):
    return 'p_expected', policy_input['p_expected']

def s_store_cdps(params, substep, state_history, state, policy_input):
    return 'cdps', policy_input['cdps']

def resolve_cdp_positions(params, state, policy_input):
    eth_price = state['eth_price']
    target_price = state['target_price']
    liquidation_ratio = params['liquidation_ratio']
    liquidation_buffer = params['liquidation_buffer']
    
    cdps = state['cdps']
    cdps_copy = cdps.copy()
    cdps = cdps.sort_values(by=['time'], ascending=True) # Youngest to oldest
    cdps_above_liquidation_buffer = cdps.query(f'(locked - freed - v_bitten) * {eth_price} > (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio} * {liquidation_buffer}')
    cdps_below_liquidation_ratio = cdps.query(f'(locked - freed - v_bitten) * {eth_price} < (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio}')
    cdps_below_liquidation_buffer = cdps.query(f'(locked - freed - v_bitten) * {eth_price} < (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio} * {liquidation_buffer}')
    
    rising_eth = policy_input['rising_eth']
    
    v_2 = policy_input['v_2 + v_3'] # Free, no v_3 liquidations
    u_1 = policy_input['u_1'] # Draw
    u_2 = policy_input['u_2'] # Wipe
    v_1 = policy_input['v_1'] # Lock
    
    if rising_eth: # Rising ETH
        '''
        If ETH price rises, then (u_1, v_2+v_3) = (draw, free). Start with frees, rebalance by taking out excess collateral until back to liquidation ratio + buffer. (No liquidation, no 'bites')
        1. If run out of positions, then excess free. Distribute over all CDPs?
        2. If run out of frees, then go to draws. Rebalance by minting new RAI and reducing to liquidation ratio + buffer
        3. If run out of positions, then excess draws _could_ be applied to new positions opened with locks
        '''
        
        for index, cdp in cdps_above_liquidation_buffer.iterrows():
            locked = cdps.at[index, 'locked']
            freed = cdps.at[index, 'freed']
            v_bitten = cdps.at[index, 'v_bitten']
            drawn = cdps.at[index, 'drawn']
            wiped = cdps.at[index, 'wiped']
            u_bitten = cdps.at[index, 'u_bitten']
            # (locked - freed - free - v_bitten) * eth_price / (drawn - wiped - u_bitten) * target_price = liquidation_ratio * liquidation_buffer
            free = ((locked - freed - v_bitten) * eth_price - liquidation_ratio * liquidation_buffer * (drawn - wiped - u_bitten) * target_price) / eth_price
            
            assert free > 0
            if locked <= freed + free + v_bitten:
                continue
            
            if v_2 - free > 0:
                cdps.at[index, 'freed'] = freed + free
                v_2 = v_2 - free
            else:
                cdps.at[index, 'freed'] = freed + v_2
                v_2 = 0
                break
        
        # If excess frees, distribute over all CDPs
        if v_2 > 0:
            cdp_count = len(cdps)
            free_distributed = v_2 / cdp_count
            
            assert free_distributed > 0
            
            for index, cdp in cdps.iterrows():
                locked = cdps.at[index, 'locked']
                freed = cdps.at[index, 'freed']
                v_bitten = cdps.at[index, 'v_bitten']
                drawn = cdps.at[index, 'drawn']
                wiped = cdps.at[index, 'wiped']
                u_bitten = cdps.at[index, 'u_bitten']
                
                if locked <= freed + free_distributed + v_bitten:
                    continue
                
                cdps.at[index, 'freed'] = freed + free_distributed
        
        # If run out of frees, go to draws
        cdps_above_liquidation_buffer = cdps.query(f'(locked - freed - v_bitten) * {eth_price} > (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio} * {liquidation_buffer}')
        if u_1 > 0:
            for index, cdp in cdps_above_liquidation_buffer.iterrows():
                locked = cdps.at[index, 'locked']
                freed = cdps.at[index, 'freed']
                v_bitten = cdps.at[index, 'v_bitten']
                drawn = cdps.at[index, 'drawn']
                wiped = cdps.at[index, 'wiped']
                u_bitten = cdps.at[index, 'u_bitten']
                # (locked - freed - v_bitten) * eth_price / (drawn + draw - wiped - u_bitten) * target_price = liquidation_ratio * liquidation_buffer
                draw = ((locked - freed - v_bitten) * eth_price / liquidation_ratio * liquidation_buffer - (drawn - wiped - u_bitten) * target_price) / target_price
                
                assert draw > 0
                
                if u_1 - draw > 0:
                    cdps.at[index, 'draw'] = drawn + draw
                    u_1 = u_1 - draw
                else:
                    cdps.at[index, 'draw'] = drawn + u_1
                    u_1 = 0
                    break
        
        # If run out of positions, excess draws applied to new positions opened with locks
        if u_1 > 0:
            cumulative_time = state['cumulative_time']
            v_1 = u_1 * target_price * liquidation_ratio / eth_price
            cdps = cdps.append({
                'time': cumulative_time,
                'locked': v_1,
                'drawn': u_1,
                'wiped': 0.0,
                'freed': 0.0,
                'dripped': 0.0
            }, ignore_index=True)
        
    else: # Falling ETH
        '''
        If ETH price falls, then (u_2, v_1) = (wipe, lock). Start with wipes, rebalance by paying off those obligations that are below liquidation ratio. Position order is always youngest to oldest.
        1. If run out of positions, then excess wipe? Excess RAI left over => buffer up different positions until wipe runs out, up to data-derived buffer above liquidation ratio (from data, 3x vs. 1.5 min). 
        2. If run out of wipe, then go to locks: rebalance by adding collateral
        3. If run out of positions, then open new positions with excess lock
        '''
        
        # Wipe to reach liquidation ratio
        for index, cdp in cdps_below_liquidation_ratio.iterrows():
            locked = cdps.at[index, 'locked']
            freed = cdps.at[index, 'freed']
            v_bitten = cdps.at[index, 'v_bitten']
            drawn = cdps.at[index, 'drawn']
            wiped = cdps.at[index, 'wiped']
            u_bitten = cdps.at[index, 'u_bitten']
            # (locked - freed - v_bitten) * eth_price / (drawn - wiped - wipe - u_bitten) * target_price = liquidation_ratio 
            wipe = (drawn - wiped - u_bitten) - (locked - freed - v_bitten) * eth_price / (liquidation_ratio * target_price)
            
            assert wipe >= 0
            if drawn <= wiped + wipe + u_bitten:
                continue
            
            if u_2 - wipe > 0:
                cdps.at[index, 'wiped'] = wiped + wipe
                u_2 = u_2 - wipe
            else:
                cdps.at[index, 'wiped'] = wiped + u_2
                u_2 = 0
                break
        
        # Wipe to reach liquidation buffer
        if u_2 > 0:
            cdps_below_liquidation_buffer = cdps.query(f'(locked - freed - v_bitten) * {eth_price} < (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio} * {liquidation_buffer}')
            for index, cdp in cdps_below_liquidation_buffer.iterrows():
                locked = cdps.at[index, 'locked']
                freed = cdps.at[index, 'freed']
                drawn = cdps.at[index, 'drawn']
                v_bitten = cdps.at[index, 'v_bitten']
                wiped = cdps.at[index, 'wiped']
                u_bitten = cdps.at[index, 'u_bitten']
                # (locked - freed - v_bitten) * eth_price / (drawn - wiped - wipe - u_bitten) * target_price = liquidation_ratio * liquidation_buffer
                wipe = (drawn - wiped - u_bitten) - (locked - freed - v_bitten) * eth_price / (liquidation_ratio * liquidation_buffer * target_price)
                
                assert wipe >= 0
                if drawn <= wiped + wipe + u_bitten:
                    continue
                
                if u_2 - wipe > 0:
                    cdps.at[index, 'wiped'] = wiped + wipe
                    u_2 = u_2 - wipe
                else:
                    cdps.at[index, 'wiped'] = wiped + u_2
                    u_2 = 0
                    break
                 
        # Lock collateral
        if v_1 > 0:
            cdps_below_liquidation_buffer = cdps.query(f'(locked - freed - v_bitten) * {eth_price} < (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio} * {liquidation_buffer}')
            for index, cdp in cdps_below_liquidation_buffer.iterrows():
                locked = cdps.at[index, 'locked']
                freed = cdps.at[index, 'freed']
                drawn = cdps.at[index, 'drawn']
                v_bitten = cdps.at[index, 'v_bitten']
                wiped = cdps.at[index, 'wiped']
                u_bitten = cdps.at[index, 'u_bitten']
                # (locked + lock - freed - v_bitten) * eth_price = (drawn - wiped - u_bitten) * (liquidation_ratio * target_price)
                lock = ((drawn - wiped - u_bitten) * target_price * liquidation_ratio - (locked - freed - v_bitten) * eth_price) / eth_price
                
                assert lock > 0
                
                if v_1 - lock > 0:
                    cdps.at[index, 'locked'] = locked + lock
                    v_1 = v_1 - lock
                else:
                    cdps.at[index, 'locked'] = locked + v_1
                    v_1 = 0
                    break
        
        # Open new CDPs with remaining collateral
        if v_1 > 0:
            cumulative_time = state['cumulative_time']
            u_1 = v_1 * eth_price / (target_price * liquidation_ratio)
            cdps = cdps.append({
                'time': cumulative_time,
                'locked': v_1,
                'drawn': u_1,
                'wiped': 0.0,
                'freed': 0.0,
                'dripped': 0.0
            }, ignore_index=True)
            
    u_1 = cdps['drawn'].sum() - cdps_copy['drawn'].sum()
    u_2 = cdps['wiped'].sum() - cdps_copy['wiped'].sum()
    v_2 = cdps['freed'].sum() - cdps_copy['freed'].sum()
    
    print(len(cdps))
        
    return {'cdps': cdps, 'u_1': u_1, 'u_2': u_2, 'v_2': v_2, 'v_2 + v_3': v_2}
