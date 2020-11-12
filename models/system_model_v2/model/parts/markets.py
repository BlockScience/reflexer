import scipy.stats as sts
import numpy as np

import options


def update_market_price(params, substep, state_history, state, policy_input):
    value = params['market_price'](state['timestep'])    
    return 'market_price', value
