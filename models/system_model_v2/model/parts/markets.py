import scipy.stats as sts
import numpy as np

import options
from utils import get_feature

def update_market_price(params, substep, state_history, state, policy_input):
    #value = params['market_price'](state['timestep'])    
    p_expected = policy_input['p_expected']
    previous_price = state['market_price']
    feature = get_feature(state)
    
    clearing_price = get_market_price(p_expected, previous_price, feature)
    
    return 'market_price', value

features = ['beta', 'Q', 'v_1', 'v_2 + v_3', 
                    'D_1', 'u_1', 'u_2', 'u_3', 'u_2 + u_3', 
                    'D_2', 'w_1', 'w_2', 'w_3', 'w_2 + w_3',
                    'D']

# Secondary market function
# Zero-intelligence market-clearing price: 
# cf. Gode & Sunder (JPE v 101 n 1, 1993)
order_book = np.array([0,0])
bidvars = ['u_2']
askvars = ['u_1']
bidindex = [features.index(i) for i in bidvars]
askindex = [features.index(i) for i in askvars]

def get_market_price(expected_price, previous_price, feature):
    global order_book
    order_book = order_book + np.array([np.sum(feature[:,bidindex][0]), 
                    np.sum(feature[:,askindex][0])]
    )
    clearing_price = np.random.uniform(
                    min(previous_price, expected_price), 
                    max(previous_price, expected_price)
    )
    book_end = order_book[0] - order_book[1]
    
    if book_end < 0: # excess supply
        order_book = np.array([0, book_end])
    else: # excess demand
        order_book = np.array([book_end, 0])
    
    return clearing_price
