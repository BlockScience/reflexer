import scipy.stats as sts
import pandas as pd

############################################################################################################################################

def p_resolve_eth_price(params, substep, state_history, state):
    base_var = params['eth_market_std']
    variance = float(base_var * state['timedelta'] / 3600.0)
    random_state = params['random_state']
    delta_eth_price = sts.norm.rvs(loc=0, scale=variance, random_state=random_state)
    
    return {'delta_eth_price': delta_eth_price}

def s_update_eth_price(params, substep, state_history, state, policy_input):
    #eth_price = state['eth_price']
    #delta_eth_price = policy_input['delta_eth_price']
    eth_price = params['eth_price'](state['timestep'])
    delta_eth_price = 0
    
    return 'eth_price', eth_price + delta_eth_price

# def s_update_redemption_price(params, substep, state_history, state, policy_input):
#     eth_collateral = state['eth_collateral']
#     eth_price = state['eth_price']
#     collateral_value = eth_collateral * eth_price
#     principal_debt = state['principal_debt']
    
#     target_price = collateral_value / principal_debt
#     assert target_price >= 0, f'{target_price} !>= 0 ~ {collateral_value}, {principal_debt}, {state}'
    
#     return 'target_price', target_price

############################################################################################################################################

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
#         return {'delta_v1': v1, 'delta_u1': u1}
#     else:
#         return {'delta_v1': 0, 'delta_u1': 0}

    delta_v1 = params['delta_v1'](state['timestep'])
    delta_u1 = params['delta_u1'](state['timestep'])
    
    return {'delta_v1': delta_v1, 'delta_u1': delta_u1}

def p_close_cdps(params, substep, state_history, state):    
    cdps = state['cdps']
    average_debt_age = params['average_debt_age']
    cumulative_time = state['cumulative_time']
    
    closed_cdps = cdps.query(f'{cumulative_time} - time >= {average_debt_age}')
    delta_v2 = closed_cdps['locked'].sum()
    delta_u2 = closed_cdps['drawn'].sum()
    delta_w2 = closed_cdps['dripped'].sum()
    
    return {'closed_cdps': closed_cdps, 'delta_v2': delta_v2, 'delta_u2': delta_u2, 'delta_w2': delta_w2}

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
    
    if len(liquidated_cdps.index) > 0:
        try:
            delta_u3 = liquidated_cdps['drawn'].sum()
            delta_v3 = (delta_u3 * target_price * (1 + liquidation_penalty)) / eth_price
            eth_locked = liquidated_cdps['locked'].sum()
            assert delta_v3 >= 0, f'{delta_v3} !>= 0 ~ {state}'
            assert delta_v3 <= eth_locked, f'{delta_v3} !<= {eth_locked}'
            # Assume remaining collateral freed
            delta_v2 = eth_locked - delta_v3
            assert delta_v2 >= 0, f'{delta_v2} !>= {0}'
            delta_w3 = liquidated_cdps['dripped'].sum()
            assert delta_w3 > 0
        except AssertionError as err:
            print(f'Liquidation short of collateral: {err}')
            delta_v3 = liquidated_cdps['locked'].sum()
            delta_u3 = liquidated_cdps['drawn'].sum()
            delta_v2 = 0
            delta_w3 = liquidated_cdps['dripped'].sum()
    else:
        delta_v3 = 0
        delta_u3 = 0
        delta_v2 = 0
        delta_w3 = 0
    
    return {'liquidated_cdps': liquidated_cdps, 'delta_v3': delta_v3, 'delta_u3': delta_u3, 'delta_v2': delta_v2, 'delta_w3': delta_w3}

def s_resolve_cdps(params, substep, state_history, state, policy_input):
    delta_v1 = policy_input.get('delta_v1', 0)
    delta_u1 = policy_input.get('delta_u1', 0)
    
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
            
    if delta_v1 > 0:
        cumulative_time = state['cumulative_time']
        total_top_ups = cdps.query(f'locked * {eth_price} < drawn * {target_price} * {cdp_top_up_buffer}').shape[0]
        if total_top_ups > 0:
            top_up_collateral = (delta_v1 * 0.5) / total_top_ups
            delta_v1 = delta_v1 * 0.5
            cdps = cdps.apply(lambda cdp: top_up_cdp(cdp, top_up_collateral), axis=1)
        cdps = cdps.append({
            'time': cumulative_time,
            'locked': delta_v1,
            'drawn': delta_u1,
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
    delta_v1 = policy_input['delta_v1']
    
    assert delta_v1 >= 0
    
    return 'eth_locked', eth_locked + delta_v1

def s_update_eth_freed(params, substep, state_history, state, policy_input):
    eth_freed = state['eth_freed']
    delta_v2 = policy_input['delta_v2']
    
    assert delta_v2 >= 0
    
    return 'eth_freed', eth_freed + delta_v2

def s_update_eth_bitten(params, substep, state_history, state, policy_input):
    eth_bitten = state['eth_bitten']
    delta_v3 = policy_input['delta_v3']
    
    assert delta_v3 >= 0
    
    return 'eth_bitten', eth_bitten + delta_v3

def s_update_rai_drawn(params, substep, state_history, state, policy_input):
    rai_drawn = state['rai_drawn']
    delta_u1 = policy_input['delta_u1']
    
    assert delta_u1 >= 0
    
    return 'rai_drawn', rai_drawn + delta_u1

def s_update_rai_wiped(params, substep, state_history, state, policy_input):
    rai_wiped = state['rai_wiped']
    delta_u2 = policy_input['delta_u2']
    
    assert delta_u2 >= 0
    
    return 'rai_wiped', rai_wiped + delta_u2

def s_update_rai_bitten(params, substep, state_history, state, policy_input):
    rai_bitten = state['rai_bitten']
    delta_u3 = policy_input['delta_u3']
    
    assert delta_u3 >= 0
    
    return 'rai_bitten', rai_bitten + delta_u3
    
def s_update_system_revenue(params, substep, state_history, state, policy_input):
    system_revenue = state['system_revenue']
    delta_w2 = policy_input.get('delta_w2', 0)
    return 'system_revenue', system_revenue + delta_w2

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
    delta_w3 = policy_input.get('delta_w3', 0)
    return 'accrued_interest', previous_accrued_interest - delta_w3

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
