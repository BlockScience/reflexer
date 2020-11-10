# from .parts.controllers import *
# from .parts.markets import *
from .parts.debt_market import *
from .parts.time import *
from .parts.utils import *

partial_state_update_blocks = [
    {
        'policies': {
            'free_memory': p_free_memory,
        },
        'variables': {}
    },
    {
        'details': '''
            This block observes (or samples from data) the amount of time passed between events
        ''',
        'policies': {
            'time_process': resolve_time_passed
        },
        'variables': {
            'timedelta': store_timedelta,
            'timestamp': update_timestamp,
            'cumulative_time': update_cumulative_time
        }
    },
    {
        'details': '''
            Update debt market state
        ''',
        'policies': {},
        'variables': {
            'eth_collateral': s_update_eth_collateral,
            'principal_debt': s_update_principal_debt,
        }
    },
    {
        'details': '''
            Exogenous ETH price process
        ''',
        'policies': {
            'exogenous_eth_process': p_resolve_eth_price,
        },
        'variables': {
            'eth_price': s_update_eth_price
        }
    },
    {
        'details': '''
            Exogenous u,v activity: liquidate CDPs
        ''',
        'policies': {
            'liquidate_cdps': p_liquidate_cdps
        },
        'variables': {
            'eth_bitten': s_update_eth_bitten,
            'eth_freed': s_update_eth_freed,
            'rai_bitten': s_update_rai_bitten,
            'accrued_interest': s_update_interest_bitten,
            'cdps': s_resolve_cdps,
        }
    },
    {
        'details': '''
            Exogenous u,v activity: open CDPs
        ''',
        'policies': {
            'open_cdps': p_open_cdps,
        },
        'variables': {
            'eth_locked': s_update_eth_locked,
            'rai_drawn': s_update_rai_drawn,
            'cdps': s_resolve_cdps,
        }
    },
    {
        'details': '''
            Exogenous u,v activity: close CDPs
        ''',
        'policies': {
            'close_cdps': p_close_cdps,
        },
        'variables': {
            'eth_freed': s_update_eth_freed,
            'rai_wiped': s_update_rai_wiped,
            'system_revenue': s_update_system_revenue,
            'cdps': s_resolve_cdps,
        }
    },
    {
        'details': '''
            Endogenous w activity
        ''',
        'policies': {},
        'variables': {
            'accrued_interest': s_update_accrued_interest,
            'cdps': s_update_cdp_interest
        }
    },
#     {
#         'details': """
#         This block computes and stores the error terms
#         required to compute the various control actions (including the market action)
#         """,
#         'policies': {'observe':observe_errors},
#         'variables': {
#             'error_star': store_error_star,
#             'error_star_integral': update_error_star_integral,
#             'error_star_derivative': update_error_star_derivative,
#             'error_hat': store_error_hat,
#             'error_hat_integral': update_error_hat_integral,
#             'error_hat_derivative': update_error_hat_derivative,
#         }
#     },
#     {
#         'details': """
#         This block applies the model of the market to update the market price 
#         """,
#         'policies': {},
#         'variables': {
#             'market_price': update_market_price,
#         }
#     },
#     {
#         'details': """
#         This block computes the stability control action 
#         """,
#         'policies': {},
#         'variables': {
#             'target_rate': update_target_rate,
#         }
#     },
#     {
#         'details': """
#         This block updates the target price based on stability control action 
#         """,
#         'policies': {},
#         'variables': {
#             'target_price': update_target_price,
#         }
#     }
]

# partial_state_update_blocks = [
#     {
#         'details': """
#         This block observes (or samples from data) the amount of time passed between events
#         """,
#         'policies': {'time_process':resolve_time_passed},
#         'variables': {
#             'timedelta': store_timedelta,
#             'timestamp': update_timestamp,
#             'blockheight': update_blockheight,
#         }
#     },
#     {   
#         'details': """
#         This block observes (or samples from data) the change to the price implied by the debt price 
#         """,
#         'policies': {
#             'debt_market': resolve_debt_price
#         },
#         'variables': {
#             'debt_price': update_debt_price,
#         }
#     },
#     {
#         'details': """
#         This block computes and stores the error terms
#         required to compute the various control actions (including the market action)
#         """,
#         'policies': {'observe':observe_errors},
#         'variables': {
#             'error_star': store_error_star,
#             'error_star_integral': update_error_star_integral,
#             'error_star_derivative': update_error_star_derivative,
#             'error_hat': store_error_hat,
#             'error_hat_integral': update_error_hat_integral,
#             'error_hat_derivative': update_error_hat_derivative,
#         }
#     },
#     {
#         'details': """
#         This block applies the model of the market to update the market price 
#         """,
#         'policies': {},
#         'variables': {
#             'market_price': update_market_price,
#         }
#     },
#     {
#         'details': """
#         This block computes the stability control action 
#         """,
#         'policies': {},
#         'variables': {
#             'target_rate': update_target_rate,
#         }
#     },
#     {
#         'details': """
#         This block updates the target price based on stability control action 
#         """,
#         'policies': {},
#         'variables': {
#             'target_price': update_target_price,
#         }
#     }
# ]
