def p_free_memory(params, substep, state_history, state):
    if state['timestep'] > 0:
        for key in params['free_memory_states']:
            substates = state_history[-1]
            for substate in substates:
                substate[key] = None
    return {}

def s_collect_events(params, substep, state_history, state, policy_input):
    return 'events', state['events'] + policy_input.get('events', [])
