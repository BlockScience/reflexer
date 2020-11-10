import scipy.stats as sts
import datetime as dt
import numpy as np

import options


# def resolve_time_passed(params, substep, state_history, state):
#     """
#     Time passes 
#     """
    
#     if params[options.DebtPriceSource.__name__] == options.DebtPriceSource.DEBT_MARKET_MODEL.value:
#         seconds = max(params['minumum_control_period'](state['timestep']), params['seconds_passed'](state['timestep']))
#     else:
#         offset = params['minumum_control_period'](state['timestep'])
#         expected_lag = params['expected_control_delay'](state['timestep'])
#         seconds = int(sts.expon.rvs(loc=offset, scale=expected_lag, random_state=np.random.RandomState(seed=int(f'{state["run"]}' + f'{state["timestep"]}'))))

#     return {'seconds_passed': seconds}

def resolve_time_passed(params, substep, state_history, state):
    seconds = params['seconds_passed'](state['timestep'])
    
    return {'seconds_passed': seconds}

def store_timedelta(params, substep, state_history, state, policy_input):

    value = policy_input['seconds_passed']
    key = 'timedelta'

    return key,value

def update_timestamp(params, substep, state_history, state, policy_input):

    seconds = policy_input['seconds_passed']
    value = state['timestamp'] + dt.timedelta(seconds = int(seconds))
    key = 'timestamp'

    return key,value

def update_blockheight(params, substep, state_history, state, policy_input):

    seconds = policy_input['seconds_passed']
    blocks = int(seconds/params['expected_blocktime'])
    value = state['blockheight']+ blocks
    key = 'blockheight'

    return key,value

def update_cumulative_time(params, substep, state_history, state, policy_input):
    seconds = policy_input['seconds_passed']
    
    return 'cumulative_time', state['cumulative_time'] + seconds
