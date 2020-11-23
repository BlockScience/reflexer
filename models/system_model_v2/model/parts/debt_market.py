import scipy.stats as sts
import pandas as pd

############################################################################################################################################

def p_resolve_eth_price(params, substep, state_history, state):
    #base_var = params['eth_market_std']
    #variance = float(base_var * state['timedelta'] / 3600.0)
    #random_state = params['random_state']
    #delta_eth_price = sts.norm.rvs(loc=0, scale=variance, random_state=random_state)
    eth_price = params['eth_price'](state['timestep'])
    delta_eth_price = eth_price - state_history[-1][-1]['eth_price']
    
    return {'delta_eth_price': delta_eth_price}

def s_update_eth_price(params, substep, state_history, state, policy_input):
    eth_price = state['eth_price']
    delta_eth_price = policy_input['delta_eth_price']

    return 'eth_price', eth_price + delta_eth_price

def s_update_eth_return(params, substep, state_history, state, policy_input):
    eth_price = state['eth_price']
    delta_eth_price = policy_input['delta_eth_price']
    
    return 'eth_return', delta_eth_price / eth_price

def s_update_eth_gross_return(params, substep, state_history, state, policy_input):
    eth_price = state['eth_price']
    eth_gross_return = eth_price / state_history[-1][-1]['eth_price']
    
    return 'eth_gross_return', eth_gross_return

############################################################################################################################################

def s_update_stability_fee(params, substep, state_history, state, policy_input):
    stability_fee = params['stability_fee'](state['timestep'])
    return 'stability_fee', stability_fee

def p_open_cdps(params, substep, state_history, state):
#     base_var = 100
#     variance = float(base_var * state['timedelta'] / 3600.0)
#     random_state = params['random_state']
#     rvs = sts.norm.rvs(loc=0, scale=variance, random_state=random_state)
#     v1 = max(rvs, 0) # total Eth value of new CDP
    
#     # cdps = state['cdps']

#     liquidation_ratio = params['liquidation_ratio']
#     collateral_value = v1 * state['eth_price']
#     target_price = state['target_price']
#     u1 = collateral_value / (target_price * liquidation_ratio)
    
#     cumulative_time = state['cumulative_time']
#     # Daily activity
#     if cumulative_time % 1 == 0:
#         return {'v_1': v1, 'u_1': u1}
#     else:
#         return {'v_1': 0, 'u_1': 0}

    #v_1 = params['v_1'](state['timestep'])
    #u_1 = params['u_1'](state['timestep'])
    v_1 = params['v_1'](state, state_history)
    u_1 = params['u_1'](state['timestep'])
    
    return {'v_1': v_1, 'u_1': u_1}

def p_close_cdps(params, substep, state_history, state):    
    cdps = state['cdps']
    average_debt_age = params['average_debt_age']
    cumulative_time = state['cumulative_time']
    
    closed_cdps = cdps.query(f'{cumulative_time} - time >= {average_debt_age}')
    v_2 = closed_cdps['locked'].sum()
    u_2 = closed_cdps['drawn'].sum()
    w_2 = closed_cdps['dripped'].sum()
    
    return {'closed_cdps': closed_cdps, 'v_2': v_2, 'u_2': u_2, 'w_2': w_2}

def p_liquidate_cdps(params, substep, state_history, state):
    eth_price = state['eth_price']
    target_price = state['target_price']
    liquidation_penalty = params['liquidation_penalty']
    liquidation_ratio = params['liquidation_ratio']
    
    cdps = state['cdps']
    liquidated_cdps = pd.DataFrame()
    if len(cdps) > 0:
        try:
            liquidated_cdps = cdps.query(f'locked * {eth_price} < drawn * {target_price} * {liquidation_ratio}')
        except:
            print(state)
            raise
    
    events = []
    if len(liquidated_cdps.index) > 0:
        try:
            u_3 = liquidated_cdps['drawn'].sum()
            v_3 = (u_3 * target_price * (1 + liquidation_penalty)) / eth_price
            eth_locked = liquidated_cdps['locked'].sum()
            assert v_3 >= 0, f'{v_3} !>= 0 ~ {state}'
            assert v_3 <= eth_locked, f'Liquidation short of collateral: {v_3} !<= {eth_locked}'
            # Assume remaining collateral freed
            v_2 = eth_locked - v_3
            assert v_2 >= 0, f'{v_2} !>= {0}'
            w_3 = liquidated_cdps['dripped'].sum()
            assert w_3 > 0
        except AssertionError as err:
            events = [err]
            v_3 = liquidated_cdps['locked'].sum()
            u_2 = liquidated_cdps['drawn'].sum()
            v_2 = 0
            w_3 = liquidated_cdps['dripped'].sum()
    else:
        v_3 = 0
        u_3 = 0
        v_2 = 0
        w_3 = 0
    
    return {'events': events, 'liquidated_cdps': liquidated_cdps, 'v_3': v_3, 'u_3': u_3, 'v_2': v_2, 'w_3': w_3}

def s_store_v_1(params, substep, state_history, state, policy_input):
    return 'v_1', policy_input['v_1']

def s_store_u_1(params, substep, state_history, state, policy_input):
    return 'u_1', policy_input['u_1']
    
def s_store_w_1(params, substep, state_history, state, policy_input):
    return 'w_1', policy_input['w_1']

def s_store_v_2(params, substep, state_history, state, policy_input):
    return 'v_2', policy_input['v_2']

def s_store_u_2(params, substep, state_history, state, policy_input):
    return 'u_2', policy_input['u_3']
    
def s_store_w_2(params, substep, state_history, state, policy_input):
    return 'w_2', policy_input['w_2']

def s_store_v_3(params, substep, state_history, state, policy_input):
    return 'v_3', policy_input['v_3']

def s_store_u_3(params, substep, state_history, state, policy_input):
    return 'u_3', policy_input['u_3']

def s_store_w_3(params, substep, state_history, state, policy_input):
    return 'w_3', policy_input['w_3']

def s_resolve_cdps(params, substep, state_history, state, policy_input):
    v_1 = policy_input.get('v_1', 0)
    u_1 = policy_input.get('u_1', 0)
    
    cdps = state['cdps']
    
    liquidated_cdps = policy_input['liquidated_cdps'].index if 'liquidated_cdps' in policy_input else pd.Index([])
    closed_cdps = policy_input['closed_cdps'].index if 'closed_cdps' in policy_input else pd.Index([])

    drop_index = liquidated_cdps.union(closed_cdps)
    try:
        cdps = cdps.drop(drop_index)
    except KeyError:
        print('Failed to drop CDPs')
        raise

    cdp_top_up_buffer = params['cdp_top_up_buffer']
    eth_price = state['eth_price']
    target_price = state['target_price']
    
    def top_up_cdp(cdp, top_up_collateral):
        locked = cdp['locked']
        drawn = cdp['drawn']
        top_up = locked * eth_price < drawn * target_price * cdp_top_up_buffer
        if top_up:
            cdp['locked'] = locked + top_up_collateral
        return cdp
            
    if v_1 > 0:
        cumulative_time = state['cumulative_time']
        total_top_ups = cdps.query(f'locked * {eth_price} < drawn * {target_price} * {cdp_top_up_buffer}').shape[0]
        if total_top_ups > 0:
            top_up_collateral = (v_1 * 0.5) / total_top_ups
            v_1 = v_1 * 0.5
            cdps = cdps.apply(lambda cdp: top_up_cdp(cdp, top_up_collateral), axis=1)
        cdps = cdps.append({
            'time': cumulative_time,
            'locked': v_1,
            'drawn': u_1,
            'wiped': 0.0,
            'freed': 0.0,
            'dripped': 0.0
        }, ignore_index=True)
    
    return 'cdps', cdps

def s_update_eth_collateral(params, substep, state_history, state, policy_input):
    eth_locked = state['eth_locked']
    eth_freed = state['eth_freed']
    eth_bitten = state['eth_bitten']
    
    eth_collateral = eth_locked - eth_freed - eth_bitten
    assert eth_collateral >= 0
    
    return 'eth_collateral', eth_collateral

def s_update_principal_debt(params, substep, state_history, state, policy_input):
    rai_drawn = state['rai_drawn']
    rai_wiped = state['rai_wiped']
    rai_bitten = state['rai_bitten']
    
    principal_debt = rai_drawn - rai_wiped - rai_bitten
    assert principal_debt >= 0
    
    return 'principal_debt', principal_debt

def s_update_eth_locked(params, substep, state_history, state, policy_input):
    eth_locked = state['eth_locked']
    v_1 = policy_input['v_1']
    
    assert v_1 >= 0
    
    return 'eth_locked', eth_locked + v_1

def s_update_eth_freed(params, substep, state_history, state, policy_input):
    eth_freed = state['eth_freed']
    v_2 = policy_input['v_2']
    
    assert v_2 >= 0
    
    return 'eth_freed', eth_freed + v_2

def s_update_eth_bitten(params, substep, state_history, state, policy_input):
    eth_bitten = state['eth_bitten']
    v_3 = policy_input['v_3']
    
    assert v_3 >= 0
    
    return 'eth_bitten', eth_bitten + v_3

def s_update_rai_drawn(params, substep, state_history, state, policy_input):
    rai_drawn = state['rai_drawn']
    u_1 = policy_input['u_1']
    
    assert u_1 >= 0
    
    return 'rai_drawn', rai_drawn + u_1

def s_update_rai_wiped(params, substep, state_history, state, policy_input):
    rai_wiped = state['rai_wiped']
    u_2 = policy_input['u_2']
    
    assert u_2 >= 0
    
    return 'rai_wiped', rai_wiped + u_2

def s_update_rai_bitten(params, substep, state_history, state, policy_input):
    rai_bitten = state['rai_bitten']
    u_3 = policy_input['u_3']
    
    assert u_3 >= 0
    
    return 'rai_bitten', rai_bitten + u_3
    
def s_update_system_revenue(params, substep, state_history, state, policy_input):
    system_revenue = state['system_revenue']
    w_2 = policy_input.get('w_2', 0)
    return 'system_revenue', system_revenue + w_2

def s_update_accrued_interest(params, substep, state_history, state, policy_input):
    previous_accrued_interest = state['accrued_interest']
    principal_debt = state['principal_debt']
    
    stability_fee = state['stability_fee']
    target_rate = state['target_rate']
    timedelta = state['timedelta']
    
    accrued_interest = (((1 + stability_fee)*(1 + target_rate))**timedelta - 1) * (principal_debt + previous_accrued_interest)
    return 'accrued_interest', previous_accrued_interest + accrued_interest

def s_update_interest_bitten(params, substep, state_history, state, policy_input):
    previous_accrued_interest = state['accrued_interest']
    w_3 = policy_input.get('w_3', 0)
    return 'accrued_interest', previous_accrued_interest - w_3

def s_update_cdp_interest(params, substep, state_history, state, policy_input):
    cdps = state['cdps']
    stability_fee = state['stability_fee']
    target_rate = state['target_rate']
    timedelta = state['timedelta']
    
    def resolve_cdp_interest(cdp):
        principal_debt = cdp['drawn']
        previous_accrued_interest = cdp['dripped']
        cdp['dripped'] = (((1 + stability_fee)*(1 + target_rate))**timedelta - 1) * (principal_debt + previous_accrued_interest)
        return cdp
    
    cdps.apply(resolve_cdp_interest, axis=1)
    
    return 'cdps', cdps
