import models.system_model_v3.model.parts.failure_modes as failure
from typing import Tuple
from numba import njit


def update_RAI_balance(params, substep, state_history, state, policy_input):
    RAI_balance = state['RAI_balance']
    RAI_delta = policy_input['RAI_delta']
    updated_RAI_balance = RAI_balance + RAI_delta
    if not updated_RAI_balance > 0:
        raise failure.NegativeBalanceException(
            f'Balancer RAI {RAI_balance=} {RAI_delta=}')
    return "RAI_balance", updated_RAI_balance


def update_ETH_balance(params, substep, state_history, state, policy_input):
    ETH_balance = state['ETH_balance']
    ETH_delta = policy_input['ETH_delta']
    updated_ETH_balance = ETH_balance + ETH_delta
    if not updated_ETH_balance > 0:
        raise failure.NegativeBalanceException(
            f'Balancer ETH {ETH_balance=} {ETH_delta=}')
    return "ETH_balance", updated_ETH_balance


def update_BAL_supply(params, substep, state_history, state, policy_input):
    BAL_supply = state['BAL_supply']
    BAL_delta = policy_input['BAL_delta']
    updated_BAL_supply = BAL_supply + BAL_delta
    if not updated_BAL_supply > 0:
        raise failure.NegativeBalanceException(
            f'Balancer BAL {BAL_supply=} {BAL_delta=}')
    return "BAL_supply", updated_BAL_supply

# Balancer functions
# See https://github.com/runtimeverification/verified-smart-contracts/blob/balancer/balancer/x-y-k.pdf for original v1 specification

@njit
def add_liquidity(R: float,
                  S: float,
                  V: float,
                  dV: float,
                  dR) -> Tuple[float, float, float]:
    '''
    #TODO

    Arguments
        R: Reserve tokens balance
        S: Supply tokens balance
        V: Voucher tokens balance (eg. pool token)
        dV: Voucher balance change (if V <= 0)
        dR: Reserve balance change (if V > 0)

    Returns:
        dR - reserve balance change
        dS - supply balance change
        dV - voucher balance change


    Reference:
    https://github.com/TokenEngineeringCommunity/BalancerPools_Model/blob/886b55321957449d6cbf3afafdf57b9e64a8cadb/model/parts/balancer_math.py#L108
    '''
    if V <= 0:
        dS = dV
        dV = dV
    else:
        reserve_change_fraction = dR / R
        dS = reserve_change_fraction * S
        dV = reserve_change_fraction * V
    return (dR, dS, dV)

@njit
def remove_liquidity(R: float,
                     S: float,
                     V: float,
                     dV: float) -> Tuple[float, float, float]:
    '''
    #TODO
    Arguments
        R: Reserve tokens balance
        S: Supply tokens balance
        V: Voucher tokens balance (eg. pool token)
        dV: Voucher balance change

    Returns:
        dR - reserve balance change
        dS - supply balance change
        dV - voucher balance change
    '''
    voucher_change_fraction = dV / V
    dR = voucher_change_fraction * R
    dS = voucher_change_fraction * S
    dV = voucher_change_fraction * V
    return (dR, dS, dV)


@njit
def get_input_price(dx: float,
                    x: float,
                    y: float,
                    trade_fee: float = 0.01,
                    w_x: float = 0.5,
                    w_y: float = 0.5) -> Tuple[float, float]:
    '''
    Retrieves how much the pool balance changes
    when dx tokens are sold.

    Arguments:
        dx - How much X tokens to be sold
        x - Input token balance
        y - Output token balance
        trade_fee -
        w_x -
        w_y -

    Math: 
    dy = y * (1 - [x / (x + dx * (1 - rho))] ** (w_x / w_y))

    Returns:
        Pool balance change: (dx, -dy)

    https://github.com/TokenEngineeringCommunity/BalancerPools_Model/blob/886b55321957449d6cbf3afafdf57b9e64a8cadb/model/parts/balancer_math.py#L52
    '''
    gamma = (1 - trade_fee)
    y_balance_change = x
    y_balance_change /= (x + dx * gamma)
    y_balance_change = y_balance_change ** (w_x / w_y)
    dy = y * (1 - y_balance_change)
    return (dx, -dy)


@njit
def get_output_price(dy: float,
                     x: float,
                     y: float,
                     trade_fee: float = 0.01,
                     w_x: float = 0.5,
                     w_y: float = 0.5) -> Tuple[float, float]:
    '''
    Retrieves how much the pool balance changes
    for when dy tokens are bought.

    Arguments:
        dy - How much Y tokens to be bought
        x - Input token balance
        y - Output token balance
        trade_fee -
        w_x -
        w_y -

    Math: 
    dx = x * ([y / (y - dy)] ** (w_y / w_x) - 1) / (1 - rho)

    Returns:
        Pool balance change: (dx, -dy)

    https://github.com/TokenEngineeringCommunity/BalancerPools_Model/blob/886b55321957449d6cbf3afafdf57b9e64a8cadb/model/parts/balancer_math.py#L52
    '''
    y_term = (y / (y - dy)) ** (w_y / w_x)
    dx_without_fee = x * (y_term - 1)
    dx = dx_without_fee / (1 - trade_fee)
    return (dx, -dy)