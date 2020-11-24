import numpy as np

def p_free_memory(params, substep, state_history, state):
    if state['timestep'] > 0:
        for key in params['free_memory_states']:
            substates = state_history[-1]
            for substate in substates:
                substate[key] = None
    return {}

def s_collect_events(params, substep, state_history, state, policy_input):
    return 'events', state['events'] + policy_input.get('events', [])

def get_feature(state):
    feature = [[
        state['stability_fee'] * 365 * 24 * 3600, # beta
        state['eth_collateral'], # Q
        state['v_1'], # v_1
        state['v_2'] + state['v_3'], # v_2 + v_3
        state['principal_debt'], # D_1
        state['u_1'], # u_1
        state['u_2'], # u_2
        state['u_3'], # u_3
        state['u_2'] + state['u_3'], # u_2 + u_3
        state['accrued_interest'], # D_2
        state['w_1'], # w_1
        state['w_2'], # w_2
        state['w_3'], # w_3
        state['w_2'] + state['w_3'], # w_2 + w_3
        state['principal_debt'] + state['accrued_interest'], # D
    ]]
    
    return np.insert(feature, 0, 1, axis=1)
