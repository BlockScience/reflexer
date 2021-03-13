import math
import numpy as np
import time
import logging
import pandas as pd
import statistics

from .utils import approx_greater_equal_zero, assert_log, approx_eq
from .debt_market import open_cdp_draw, open_cdp_lock, draw_to_liquidation_ratio, is_cdp_above_liquidation_ratio
from .uniswap import get_output_price, get_input_price
import models.system_model_v3.model.parts.failure_modes as failure


def p_trade_price(params, substep, state_history, state):
    debug = params['debug']

    RAI_balance = state['RAI_balance']
    ETH_balance = state['ETH_balance']
    UNI_supply = state['UNI_supply']

    trader_rai_balance = state['price_trader_rai_balance']
    trader_usd_balance = state['price_trader_usd_balance']
    

    RAI_delta = 0
    ETH_delta = 0
    USD_delta = 0
    UNI_delta = 0

    redemption_price = state['target_price'] * params['trader_market_premium']
    eth_price = state['eth_price']
    market_price = ETH_balance/RAI_balance * eth_price
    uniswap_fee = params['uniswap_fee']
    liquidation_ratio = params['liquidation_ratio']
    debt_ceiling = params['debt_ceiling']

    gas_price = params['gas_price']
    swap_gas_used = params['swap_gas_used']
    cdp_gas_used = params['cdp_gas_used']

    expensive_RAI_on_secondary_market = \
        redemption_price * (1 + params['price_trader_bound']) < (1 - uniswap_fee) * market_price
    cheap_RAI_on_secondary_market = \
        redemption_price * (1 - params['price_trader_bound']) > (1 - uniswap_fee) * market_price

    #print(f"{market_price:.2f}, calced market price {ETH_balance*eth_price/RAI_balance}")
    #print(f"timestep {state['timestep']}, trader rai balance {state['price_trader_rai_balance']}, usd balance {state['price_trader_usd_balance']}, {market_price=}, {redemption_price=}") 
    trade_price_delta = {'price_trader_rai_delta': 0, "price_trader_usd_delta": 0}
    uniswap_state_delta = {'RAI_delta': 0, 'ETH_delta': 0, 'UNI_delta': 0}

    if expensive_RAI_on_secondary_market and state['price_trader_rai_balance'] > 0:

        # sell to redemption
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance
        #b = (RAI_balance * ETH_balance)/(RAI_balance + a) - ETH_balance

        if a <= 0: raise failure.ArbitrageConditionException(f'{a=}')
        #print(f"{a=:.2f}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")
        RAI_delta = min(state['price_trader_rai_balance'], a)

        if not RAI_delta >= 0:
            raise failure.ArbitrageConditionException(f"{RAI_balance=},{ETH_balance=},{desired_eth_rai=}")

        # Swap RAI for ETH
        _, ETH_delta = get_input_price(RAI_delta, RAI_balance, ETH_balance, uniswap_fee)
        if not ETH_delta < 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'price trader selling':25} {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {'price_trader_rai_delta': -RAI_delta, 'price_trader_usd_delta': -USD_delta}
        uniswap_state_delta = {'RAI_delta': RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}
       
    elif cheap_RAI_on_secondary_market and state['price_trader_usd_balance'] > 0:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance
        #b = (RAI_balance * ETH_balance)/(RAI_balance + a) - ETH_balance

        if a >= 0: raise failure.ArbitrageConditionException(f'{a=}')

        #print(f"{a=}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")

        RAI_delta = min(int(state['price_trader_usd_balance'] / market_price), -a)

        if not RAI_delta > 0:
            raise failure.ArbitrageConditionException(f'{market_price=:.2f},{redemption_price=:.2f},{RAI_delta=:.2f}')

        #print(f"{'price trader buying':25} {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        ETH_delta, _ = get_output_price(RAI_delta, ETH_balance, RAI_balance, uniswap_fee)
        if not ETH_delta > 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {"price_trader_rai_delta": RAI_delta, "price_trader_usd_delta": -USD_delta}
        uniswap_state_delta = { 'RAI_delta': -RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}

    #trade_price_delta = {"price_trader_rai_delta": -RAI_delta, "price_trader_usd_delta": -USD_delta}
    return {**trade_price_delta, **uniswap_state_delta}

def s_store_price_trader_usd_balance(params, substep, state_history, state, policy_input):
    return 'price_trader_usd_balance', state['price_trader_usd_balance'] + policy_input['price_trader_usd_delta']

def s_store_price_trader_rai_balance(params, substep, state_history, state, policy_input):
    return 'price_trader_rai_balance', state['price_trader_rai_balance'] + policy_input['price_trader_rai_delta']

if __name__ == "__main__":
    import doctest
    doctest.testmod()
