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

def p_trade_rate(params, substep, state_history, state):
    debug = params['debug']

    RAI_balance = state['RAI_balance']
    ETH_balance = state['ETH_balance']
    UNI_supply = state['UNI_supply']

    trader_rai_balance = state['rate_trader_rai_balance']
    trader_usd_balance = state['rate_trader_usd_balance']

    RAI_delta = 0
    ETH_delta = 0
    USD_delta = 0
    UNI_delta = 0

    redemption_price = state['target_price'] * params['trader_market_premium']
    redemption_rate = state['target_rate']
    eth_price = state['eth_price']
    market_price = ETH_balance/RAI_balance * eth_price
    uniswap_fee = params['uniswap_fee']
    liquidation_ratio = params['liquidation_ratio']
    debt_ceiling = params['debt_ceiling']

    gas_price = params['gas_price']
    swap_gas_used = params['swap_gas_used']
    cdp_gas_used = params['cdp_gas_used']

    APY = ((1 + redemption_rate) ** (60*60*24*356) - 1) * 100
    very_negative_rate = redemption_rate < 0 and APY < -params['rate_trader_apy_bound']
    very_positive_rate = redemption_rate > 0 and APY > params['pos_rate_trader_apy_bound']

    #print(f"timestep {state['timestep']}, trader rai balance {state['price_trader_rai_balance']}, usd balance {state['price_trader_usd_balance']}, {market_price=}, {redemption_price=}") 
    trade_price_delta = {'rate_trader_rai_delta': 0, "rate_trader_usd_delta": 0}
    uniswap_state_delta = {'RAI_delta': 0, 'ETH_delta': 0, 'UNI_delta': 0}
    trade_ratio = 1/2

    if very_negative_rate and state['rate_trader_rai_balance'] > 0 and market_price > redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance

        #if a <= 0: raise failure.ArbitrageConditionException(f'{a=}')
        #print(f"{a=:.2f}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")
        RAI_delta = min(state['rate_trader_rai_balance'], a*trade_ratio)
        #RAI_delta = state['rate_trader_rai_balance']/5

        if not RAI_delta >= 0:
            raise failure.ArbitrageConditionException(f"{RAI_balance=},{ETH_balance=},{desired_eth_rai=}")

        # Swap RAI for ETH
        _, ETH_delta = get_input_price(RAI_delta, RAI_balance, ETH_balance, uniswap_fee)
        if not ETH_delta < 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'rate trader selling':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {'rate_trader_rai_delta': -RAI_delta, 'rate_trader_usd_delta': -USD_delta}
        uniswap_state_delta = {'RAI_delta': RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}
       
    elif very_positive_rate and state['rate_trader_usd_balance'] > 0 and market_price < redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance
        #b = (RAI_balance * ETH_balance)/(RAI_balance + a) - ETH_balance

        #if a >= 0: raise failure.ArbitrageConditionException(f'{a=}')

        #print(f"{a=}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")

        #RAI_delta = min(int(state['rate_trader_usd_balance'] / market_price), -a)
        RAI_delta = min(state['rate_trader_usd_balance']/market_price, -a*trade_ratio)

        if not RAI_delta > 0:
            raise failure.ArbitrageConditionException(f'{market_price=:.2f},{redemption_price=:.2f},{RAI_delta=:.2f}')

        USD_delta = ETH_delta * eth_price
        ETH_delta, _ = get_output_price(RAI_delta, ETH_balance, RAI_balance, uniswap_fee)
        if not ETH_delta > 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'rate trader buying':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {"rate_trader_rai_delta": RAI_delta, "rate_trader_usd_delta": -USD_delta}
        uniswap_state_delta = { 'RAI_delta': -RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}

    return {**trade_price_delta, **uniswap_state_delta}

def s_store_rate_trader_usd_balance(params, substep, state_history, state, policy_input):
    return 'rate_trader_usd_balance', state['rate_trader_usd_balance'] + policy_input['rate_trader_usd_delta']

def s_store_rate_trader_rai_balance(params, substep, state_history, state, policy_input):
    return 'rate_trader_rai_balance', state['rate_trader_rai_balance'] + policy_input['rate_trader_rai_delta']

def p_trade_neg_rate(params, substep, state_history, state):
    debug = params['debug']

    RAI_balance = state['RAI_balance']
    ETH_balance = state['ETH_balance']
    UNI_supply = state['UNI_supply']

    trader_rai_balance = state['neg_rate_trader_rai_balance']
    trader_usd_balance = state['neg_rate_trader_usd_balance']

    RAI_delta = 0
    ETH_delta = 0
    USD_delta = 0
    UNI_delta = 0

    redemption_price = state['target_price'] * params['trader_market_premium']
    redemption_rate = state['target_rate']
    eth_price = state['eth_price']
    market_price = ETH_balance/RAI_balance * eth_price
    uniswap_fee = params['uniswap_fee']
    liquidation_ratio = params['liquidation_ratio']
    debt_ceiling = params['debt_ceiling']

    gas_price = params['gas_price']
    swap_gas_used = params['swap_gas_used']
    cdp_gas_used = params['cdp_gas_used']

    APY = ((1 + redemption_rate) ** (60*60*24*356) - 1) * 100
    very_negative_rate = redemption_rate < 0 and APY < -params['neg_rate_trader_apy_bound']

    #print(f"timestep {state['timestep']}, trader rai balance {state['price_trader_rai_balance']}, usd balance {state['price_trader_usd_balance']}, {market_price=}, {redemption_price=}") 
    trade_price_delta = {'neg_rate_trader_rai_delta': 0, "neg_rate_trader_usd_delta": 0}
    uniswap_state_delta = {'RAI_delta': 0, 'ETH_delta': 0, 'UNI_delta': 0}
    trade_ratio = 1/1
    if very_negative_rate and state['neg_rate_trader_rai_balance'] > 0 and market_price > redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance

        #if a <= 0: raise failure.ArbitrageConditionException(f'{a=}')
        #print(f"{a=:.2f}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")
        RAI_delta = min(state['neg_rate_trader_rai_balance'], a*trade_ratio)
        #RAI_delta = state['neg_rate_trader_rai_balance']/5

        if not RAI_delta >= 0:
            raise failure.ArbitrageConditionException(f"{RAI_balance=},{ETH_balance=},{desired_eth_rai=}")

        # Swap RAI for ETH
        _, ETH_delta = get_input_price(RAI_delta, RAI_balance, ETH_balance, uniswap_fee)
        if not ETH_delta < 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'neg rate trader selling':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {'neg_rate_trader_rai_delta': -RAI_delta, 'neg_rate_trader_usd_delta': -USD_delta}
        uniswap_state_delta = {'RAI_delta': RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}
       
    elif very_negative_rate and state['neg_rate_trader_usd_balance'] > 0 and market_price < redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance
        #b = (RAI_balance * ETH_balance)/(RAI_balance + a) - ETH_balance

        #if a >= 0: raise failure.ArbitrageConditionException(f'{a=}')

        #print(f"{a=}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")

        #RAI_delta = min(int(state['rate_trader_usd_balance'] / market_price), -a)
        RAI_delta = min(state['neg_rate_trader_usd_balance']/market_price, -a*trade_ratio)

        if not RAI_delta > 0:
            raise failure.ArbitrageConditionException(f'{market_price=:.2f},{redemption_price=:.2f},{RAI_delta=:.2f}')

        USD_delta = ETH_delta * eth_price
        ETH_delta, _ = get_output_price(RAI_delta, ETH_balance, RAI_balance, uniswap_fee)
        if not ETH_delta > 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'neg rate trader buying':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {"neg_rate_trader_rai_delta": RAI_delta, "neg_rate_trader_usd_delta": -USD_delta}
        uniswap_state_delta = { 'RAI_delta': -RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}

    return {**trade_price_delta, **uniswap_state_delta}

def s_store_neg_rate_trader_usd_balance(params, substep, state_history, state, policy_input):
    return 'neg_rate_trader_usd_balance', state['neg_rate_trader_usd_balance'] + policy_input['neg_rate_trader_usd_delta']

def s_store_neg_rate_trader_rai_balance(params, substep, state_history, state, policy_input):
    return 'neg_rate_trader_rai_balance', state['neg_rate_trader_rai_balance'] + policy_input['neg_rate_trader_rai_delta']

def p_trade_pos_rate(params, substep, state_history, state):
    debug = params['debug']

    RAI_balance = state['RAI_balance']
    ETH_balance = state['ETH_balance']
    UNI_supply = state['UNI_supply']

    trader_rai_balance = state['pos_rate_trader_rai_balance']
    trader_usd_balance = state['pos_rate_trader_usd_balance']

    RAI_delta = 0
    ETH_delta = 0
    USD_delta = 0
    UNI_delta = 0

    redemption_price = state['target_price'] * params['trader_market_premium']
    redemption_rate = state['target_rate']
    eth_price = state['eth_price']
    market_price = ETH_balance/RAI_balance * eth_price
    uniswap_fee = params['uniswap_fee']
    liquidation_ratio = params['liquidation_ratio']
    debt_ceiling = params['debt_ceiling']

    gas_price = params['gas_price']
    swap_gas_used = params['swap_gas_used']
    cdp_gas_used = params['cdp_gas_used']

    APY = ((1 + redemption_rate) ** (60*60*24*356) - 1) * 100
    very_positive_rate = redemption_rate > 0 and APY > params['pos_rate_trader_apy_bound']

    #print(f"timestep {state['timestep']}, trader rai balance {state['price_trader_rai_balance']}, usd balance {state['price_trader_usd_balance']}, {market_price=}, {redemption_price=}") 
    trade_price_delta = {'pos_rate_trader_rai_delta': 0, "pos_rate_trader_usd_delta": 0}
    uniswap_state_delta = {'RAI_delta': 0, 'ETH_delta': 0, 'UNI_delta': 0}

    trade_ratio = 1/2
    if very_positive_rate and state['pos_rate_trader_rai_balance'] > 0 and market_price > redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance

        #if a <= 0: raise failure.ArbitrageConditionException(f'{a=}')
        #print(f"{a=:.2f}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")
        RAI_delta = min(state['pos_rate_trader_rai_balance'], a*trade_ratio)
        #RAI_delta = state['pos_rate_trader_rai_balance']/5

        if not RAI_delta >= 0:
            raise failure.ArbitrageConditionException(f"{RAI_balance=},{ETH_balance=},{desired_eth_rai=}")

        # Swap RAI for ETH
        _, ETH_delta = get_input_price(RAI_delta, RAI_balance, ETH_balance, uniswap_fee)
        if not ETH_delta < 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        #print(f"{'pos rate trader selling':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {'pos_rate_trader_rai_delta': -RAI_delta, 'pos_rate_trader_usd_delta': -USD_delta}
        uniswap_state_delta = {'RAI_delta': RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}
       
    elif very_positive_rate and state['pos_rate_trader_usd_balance'] > 0 and market_price < redemption_price:
        desired_eth_rai = ETH_balance/RAI_balance * (redemption_price/market_price)
        a = math.sqrt(RAI_balance * ETH_balance/desired_eth_rai) - RAI_balance
        #b = (RAI_balance * ETH_balance)/(RAI_balance + a) - ETH_balance

        #if a >= 0: raise failure.ArbitrageConditionException(f'{a=}')

        #print(f"{a=}, rai {RAI_balance:0f}, eth {ETH_balance:0f}, ethusd {eth_price}")

        #RAI_delta = min(int(state['rate_trader_usd_balance'] / market_price), -a)
        RAI_delta = min(state['pos_rate_trader_usd_balance'] / market_price, -a*trade_ratio)

        if not RAI_delta > 0:
            raise failure.ArbitrageConditionException(f'{market_price=:.2f},{redemption_price=:.2f},{RAI_delta=:.2f}')

        #print(f"{'pos rate trader buying':25} {APY=:.2f}, {RAI_delta=:.2f}, {ETH_delta=:.2f}, {market_price=:.2f}, {redemption_price=:.2f}")
        USD_delta = ETH_delta * eth_price
        ETH_delta, _ = get_output_price(RAI_delta, ETH_balance, RAI_balance, uniswap_fee)
        if not ETH_delta > 0: raise failure.ArbitrageConditionException(f'{ETH_delta=}')
        USD_delta = ETH_delta * eth_price
        trade_price_delta = {"pos_rate_trader_rai_delta": RAI_delta, "pos_rate_trader_usd_delta": -USD_delta}
        uniswap_state_delta = { 'RAI_delta': -RAI_delta, 'ETH_delta': ETH_delta, 'UNI_delta': UNI_delta}

    #trade_price_delta = {"price_trader_rai_delta": -RAI_delta, "price_trader_usd_delta": -USD_delta}
    return {**trade_price_delta, **uniswap_state_delta}

def s_store_pos_rate_trader_usd_balance(params, substep, state_history, state, policy_input):
    return 'pos_rate_trader_usd_balance', state['pos_rate_trader_usd_balance'] + policy_input['pos_rate_trader_usd_delta']

def s_store_pos_rate_trader_rai_balance(params, substep, state_history, state, policy_input):
    return 'pos_rate_trader_rai_balance', state['pos_rate_trader_rai_balance'] + policy_input['pos_rate_trader_rai_delta']

if __name__ == "__main__":
    import doctest
    doctest.testmod()
