def p_free_memory(params, substep, state_history, state):
    if state['timestep'] > 0:
        for key in ['cdps']:
            substates = state_history[-1]
            for substate in substates:
                substate[key] = None
    return {}
