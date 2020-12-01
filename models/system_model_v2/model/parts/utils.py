import numpy as np

# features = ['beta', 'Q', 'v_1', 'v_2 + v_3', 
#                     'D_1', 'u_1', 'u_2', 'u_3', 'u_2 + u_3', 
#                     'D_2', 'w_1', 'w_2', 'w_3', 'w_2 + w_3',
#                     'D']

def p_free_memory(params, substep, state_history, state):
    if state['timestep'] > 0:
        for key in params['free_memory_states']:
            try:
                # Clear states older than 2nd last
                substates = state_history[-2]
                for substate in substates:
                    substate[key] = None
            except IndexError as e:
                print(e)
                continue
    return {}

def s_collect_events(params, substep, state_history, state, policy_input):
    return 'events', state['events'] + policy_input.get('events', [])

def get_feature(state_history, features, index=-1):
    # Update the state with the optimal values from the last timestep for the APT model
    state = state_history[index][-1].copy()
    state.update(state['optimal_values'])
    
    feature_dict = {
        'beta': state['stability_fee'] * 365 * 24 * 3600, # beta - yearly interest rate
        'Q': state['eth_collateral'], # Q
        'v_1': state['v_1'], # v_1
        # Liquidations are calculated and performed outside of the APT model, and could result in v_3, but within the APT model we only generate v_2
        'v_2 + v_3': state['v_2'] + state['v_3'], # state['optimal_values'].get('v2 + v3', state['v_2'] + state['v_3']), # v_2 + v_3
        'D_1': state['principal_debt'], # D_1
        'u_1': state['u_1'], # u_1
        'u_2': state['u_2'], # u_2
        'u_3': state['u_3'], # u_3
        'u_2 + u_3': state['u_2'] + state['u_3'], # u_2 + u_3
        'D_2': state['accrued_interest'], # D_2
        'w_1': state['w_1'], # w_1
        'w_2': state['w_2'], # w_2
        'w_3': state['w_3'], # w_3
        'w_2 + w_3': state['w_2'] + state['w_3'], # w_2 + w_3
        'D': state['principal_debt'] + state['accrued_interest'], # D
    }
    
    feature = [feature_dict[k] for k in features]
            
    return np.reshape(feature, (-1, len(features))).copy()
