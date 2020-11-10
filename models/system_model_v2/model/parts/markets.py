import scipy.stats as sts
import numpy as np

import options


def resolve_debt_price(params, substep, state_history, state):
    """
    driving process
    """
    
    if params[options.DebtPriceSource.__name__] == options.DebtPriceSource.EXTERNAL.value:
        price_move = params['price_move'](state['timestep'])
    elif params[options.DebtPriceSource.__name__] == options.DebtPriceSource.DEBT_MARKET_MODEL.value:
        price_move = params['price_move'](state['timestep'])
    else:
        base_var = params['debt_market_std']
        variance = float(base_var*state['timedelta']/3600.0) #converting seconds to hours
        price_move = sts.norm.rvs(loc=0, scale=variance)
        
    if params[options.MarketPriceSource.__name__] == options.MarketPriceSource.EXTERNAL.value or params[options.DebtPriceSource.__name__] == options.DebtPriceSource.DISABLED.value:
        price_move = 0

    return {'price_move': price_move}

def update_debt_price(params, substep, state_history, state, policy_input):

    price_move = policy_input['price_move']
    value = state['debt_price'] + price_move
    key = 'debt_price'
    delta = params['delta_output'](key, state['timestep'])
    
    return key, value + delta

def update_market_price(params, substep, state_history, state, policy_input):
    if params[options.MarketPriceSource.__name__] == options.MarketPriceSource.EXTERNAL.value:
        value = state['market_price'] + params['price_move'](state['timestep'])
    else:
        hat_error = state['error_hat']
        hat_integral = state['error_hat_integral']
        hat_derivative = state['error_hat_derivative']
        hat_dp = params['kp-hat'] * hat_error + params['ki-hat'](state['timedelta']) * hat_integral + params['kd-hat'](state['timedelta']) * hat_derivative

        star_error = state['error_star']
        star_integral = state['error_star_integral']
        star_derivative = state['error_star_derivative']
        star_dp = params['kp-star'] * star_error + params['ki-star'](state['timedelta']) * star_integral + params['kd-star'](state['timedelta']) * star_derivative

        market_price = params['k0'] + params['k-autoreg-1']*state['market_price'] + star_dp + hat_dp

        if market_price < 0:
            value = 0
        else:
            value = market_price

    key = 'market_price'
    delta = params['delta_output'](key, state['timestep'])
    
    return key, value + delta
