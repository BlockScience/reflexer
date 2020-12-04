import scipy.stats as sts
import numpy as np

import options
from .utils import get_feature

def update_market_price(params, substep, state_history, state, policy_input):
    p_debt_expected = state['p_debt_expected']
    previous_price = state['market_price']
    
    features = params['features']
    feature = get_feature(state_history, features)
    
    clearing_price = get_market_price(p_debt_expected, previous_price, features, feature)
    
    return 'market_price', clearing_price

# Secondary market function
# Zero-intelligence market-clearing price: 
# cf. Gode & Sunder (JPE v 101 n 1, 1993)
order_book = np.array([0,0])

def get_market_price(expected_price, previous_price, features, feature):
    global order_book
    
    bidvars = ['u_2']
    askvars = ['u_1']
    bidindex = [features.index(i) for i in bidvars]
    askindex = [features.index(i) for i in askvars]
    
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
