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

def s_update_stability_fee(params, substep, state_history, state, policy_input):
    stability_fee = params['stability_fee'](state['timestep'])
    return 'stability_fee', stability_fee

############################################################################################################################################

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
            # (locked - freed - free - v_bitten) * eth_price = (drawn - wiped - u_bitten) * target_price * liquidation_ratio * liquidation_buffer
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
                # (locked - freed - v_bitten) * eth_price = (drawn + draw - wiped - u_bitten) * target_price * liquidation_ratio * liquidation_buffer
                draw = (locked - freed - v_bitten) * eth_price / (target_price * liquidation_ratio * liquidation_buffer) - (drawn - wiped - u_bitten)
                
                draw = max(draw, 0)
                assert u_1 >= 0, u_1
                assert draw >= 0, draw
                
                if u_1 - draw > 0:
                    cdps.at[index, 'drawn'] = drawn + draw
                    u_1 = u_1 - draw
                else:
                    cdps.at[index, 'drawn'] = drawn + u_1
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
                'dripped': 0.0,
                'v_bitten': 0.0,
                'u_bitten': 0.0,
                'w_bitten': 0.0
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
            # (locked - freed - v_bitten) * eth_price = (drawn - wiped - wipe - u_bitten) * target_price * liquidation_ratio 
            wipe = (drawn - wiped - u_bitten) - (locked - freed - v_bitten) * eth_price / (liquidation_ratio * target_price)
            
            assert u_2 >= 0
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
                # (locked - freed - v_bitten) * eth_price = (drawn - wiped - wipe - u_bitten) * target_price * liquidation_ratio * liquidation_buffer
                wipe = (drawn - wiped - u_bitten) - (locked - freed - v_bitten) * eth_price / (liquidation_ratio * liquidation_buffer * target_price)
                
                assert u_2 >= 0
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
                
                #print(lock)
                #print(locked, freed, drawn, v_bitten, wiped, u_bitten)
                
                #assert lock > 0
                lock = max(lock, 0)
                
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
                'dripped': 0.0,
                'v_bitten': 0.0,
                'u_bitten': 0.0,
                'w_bitten': 0.0
            }, ignore_index=True)
            
    u_1 = cdps['drawn'].sum() - cdps_copy['drawn'].sum()
    u_2 = cdps['wiped'].sum() - cdps_copy['wiped'].sum()
    v_1 = cdps['locked'].sum() - cdps_copy['locked'].sum()
    v_2 = cdps['freed'].sum() - cdps_copy['freed'].sum()
    
    u_1 = max(u_1, 0)
    u_2 = max(u_2, 0)
    v_1 = max(v_1, 0)
    v_2 = max(v_2, 0)
    
    assert u_1 >= 0, u_1
    assert u_2 >= 0, u_2
    assert v_1 >= 0, v_1
    assert v_2 >= 0, v_2
    
    #print(f'CDP count: {len(cdps)}')
        
    return {'cdps': cdps, 'u_1': u_1, 'u_2': u_2, 'v_1': v_1, 'v_2': v_2, 'v_2 + v_3': v_2}

def p_close_cdps(params, substep, state_history, state):    
    cdps = state['cdps']
    average_debt_age = params['average_debt_age']
    cumulative_time = state['cumulative_time']
    
    closed_cdps = cdps.query(f'{cumulative_time} - time >= {average_debt_age}')
    
    v_2 = closed_cdps['locked'].sum() - closed_cdps['freed'].sum() - closed_cdps['v_bitten'].sum()
    u_2 = closed_cdps['drawn'].sum() - closed_cdps['wiped'].sum() - closed_cdps['u_bitten'].sum()
    w_2 = closed_cdps['dripped'].sum()
    
    v_2 = max(v_2, 0)
    u_2 = max(u_2, 0)
    w_2 = max(w_2, 0)
    
    try:
        cdps = cdps.drop(closed_cdps.index)
    except KeyError:
        print('Failed to drop CDPs')
        raise
        
    return {'cdps': cdps, 'v_2': v_2, 'u_2': u_2, 'w_2': w_2}

def p_liquidate_cdps(params, substep, state_history, state):
    eth_price = state['eth_price']
    target_price = state['target_price']
    liquidation_penalty = params['liquidation_penalty']
    liquidation_ratio = params['liquidation_ratio']
    
    cdps = state['cdps']
    cdps_copy = cdps.copy()
    liquidated_cdps = pd.DataFrame()
    if len(cdps) > 0:
        try:
            liquidated_cdps = cdps.query(f'(locked - freed - v_bitten) * {eth_price} < (drawn - wiped - u_bitten) * {target_price} * {liquidation_ratio}')
        except:
            print(state)
            raise
    
    events = []  
    for index, cdp in liquidated_cdps.iterrows():
        locked = cdps.at[index, 'locked']
        freed = cdps.at[index, 'freed']
        drawn = cdps.at[index, 'drawn']
        wiped = cdps.at[index, 'wiped']
        dripped = cdps.at[index, 'dripped']
        
        try:
            # (locked + lock - freed - v_bitten) * eth_price = (drawn - wiped - u_bitten) * (liquidation_ratio * target_price)
            v_bite = ((drawn - wiped) * target_price * (1 + liquidation_penalty)) / eth_price
            assert v_bite >= 0, f'{v_bite} !>= 0 ~ {state}'
            assert v_bite <= (locked - freed), f'Liquidation short of collateral: {v_bite} !<= {locked}'
            free = locked - freed - v_bite
            assert free >= 0, f'{free} !>= {0}'
            assert locked >= freed + free + v_bite
            w_bite = dripped
            assert w_bite > 0
        except AssertionError as err:
            events = [err]
            v_bite = locked - freed
            free = 0
            w_bite = dripped
        
        cdps.at[index, 'v_bitten'] = v_bite
        cdps.at[index, 'freed'] = freed + free
        cdps.at[index, 'u_bitten'] = drawn - wiped
        cdps.at[index, 'w_bitten'] = w_bite
        
    v_2 = cdps['freed'].sum() - cdps_copy['freed'].sum()
    v_3 = cdps['v_bitten'].sum() - cdps_copy['v_bitten'].sum()
    u_3 = cdps['u_bitten'].sum() - cdps_copy['u_bitten'].sum()
    w_3 = cdps['w_bitten'].sum() - cdps_copy['w_bitten'].sum()
    
    v_2 = max(v_2, 0)
    v_3 = max(v_3, 0)
    u_3 = max(u_3, 0)
    w_3 = max(w_3, 0)
    
    try:
        cdps = cdps.drop(liquidated_cdps.index)
    except KeyError:
        print('Failed to drop CDPs')
        raise
    
    return {'events': events, 'cdps': cdps, 'v_2': v_2, 'v_3': v_3, 'u_3': u_3, 'w_3': w_3}

def s_store_cdps(params, substep, state_history, state, policy_input):
    return 'cdps', policy_input['cdps']

def s_store_v_1(params, substep, state_history, state, policy_input):
    return 'v_1', policy_input.get('v_1', 0)

def s_store_u_1(params, substep, state_history, state, policy_input):
    return 'u_1', policy_input.get('u_1', 0)
    
def s_store_w_1(params, substep, state_history, state, policy_input):
    return 'w_1', policy_input['w_1']

def s_store_v_2(params, substep, state_history, state, policy_input):
    return 'v_2', policy_input['v_2']

def s_store_u_2(params, substep, state_history, state, policy_input):
    return 'u_2', policy_input.get('u_2', 0)
    
def s_store_w_2(params, substep, state_history, state, policy_input):
    return 'w_2', policy_input['w_2']

def s_store_v_3(params, substep, state_history, state, policy_input):
    return 'v_3', policy_input['v_3']

def s_store_u_3(params, substep, state_history, state, policy_input):
    return 'u_3', policy_input['u_3']

def s_store_w_3(params, substep, state_history, state, policy_input):
    return 'w_3', policy_input['w_3']

def s_update_eth_collateral(params, substep, state_history, state, policy_input):
    eth_locked = state['eth_locked']
    eth_freed = state['eth_freed']
    eth_bitten = state['eth_bitten']
    
    eth_collateral = max(eth_locked - eth_freed - eth_bitten, 0)
    assert eth_collateral >= 0, f'{eth_collateral} ~ {state}'
    
    return 'eth_collateral', eth_collateral

def s_update_principal_debt(params, substep, state_history, state, policy_input):
    rai_drawn = state['rai_drawn']
    rai_wiped = state['rai_wiped']
    rai_bitten = state['rai_bitten']
    
    principal_debt = rai_drawn - rai_wiped - rai_bitten
    assert principal_debt >= 0, f'{principal_debt} ~ {state}'
    
    return 'principal_debt', principal_debt

def s_update_eth_locked(params, substep, state_history, state, policy_input):
    eth_locked = state['eth_locked']
    v_1 = state['v_1']
    
    assert v_1 >= 0, v_1
    
    return 'eth_locked', eth_locked + v_1

def s_update_eth_freed(params, substep, state_history, state, policy_input):
    eth_freed = state['eth_freed']
    v_2 = state['v_2']
    
    assert v_2 >= 0, v_2
    
    return 'eth_freed', eth_freed + v_2

def s_update_eth_bitten(params, substep, state_history, state, policy_input):
    eth_bitten = state['eth_bitten']
    v_3 = state['v_3']
    
    assert v_3 >= 0, v_3
    
    return 'eth_bitten', eth_bitten + v_3

def s_update_rai_drawn(params, substep, state_history, state, policy_input):
    rai_drawn = state['rai_drawn']
    u_1 = state['u_1']
    
    assert u_1 >= 0, u_1
    
    return 'rai_drawn', rai_drawn + u_1

def s_update_rai_wiped(params, substep, state_history, state, policy_input):
    rai_wiped = state['rai_wiped']
    u_2 = state['u_2']
    
    assert u_2 >= 0, u_2
    
    return 'rai_wiped', rai_wiped + u_2

def s_update_rai_bitten(params, substep, state_history, state, policy_input):
    rai_bitten = state['rai_bitten']
    u_3 = state['u_3']
    
    assert u_3 >= 0, u_3
    
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
    w_3 = state['w_3']
    return 'accrued_interest', previous_accrued_interest - w_3

def s_update_cdp_interest(params, substep, state_history, state, policy_input):
    cdps = state['cdps']
    stability_fee = state['stability_fee']
    target_rate = state['target_rate']
    timedelta = state['timedelta']
    
    def resolve_cdp_interest(cdp):
        principal_debt = cdp['drawn']
        previous_accrued_interest = cdp['dripped']
        cdp['dripped'] = (((1 + stability_fee) * (1 + target_rate))**timedelta - 1) * (principal_debt + previous_accrued_interest)
        return cdp
    
    cdps.apply(resolve_cdp_interest, axis=1)
    
    return 'cdps', cdps
