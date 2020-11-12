import datetime as dt
import pandas as pd
 
eth_collateral = 1000.0
eth_price = 386.71

liquidation_ratio = 1.5 # 150%
liquidation_buffer = 2
collateral_value = eth_collateral * eth_price
target_price = 2.0
principal_debt = collateral_value / (target_price * liquidation_ratio * liquidation_buffer)

cdps = pd.DataFrame()
cdps = cdps.append({
    'time': 0,
    'locked': eth_collateral,
    'drawn': principal_debt,
    'wiped': 0.0,
    'freed': 0.0,
    'dripped': 0.0
}, ignore_index=True)

state_variables = {
    'events': [],
    'error_star': (0.0), #price units
    'error_hat': (0.0), #price units
    'old_error_star': (0.0), #price units
    'old_error_hat': (0.0), #price units
    'error_star_integral': (0.0), #price units x seconds
    'error_hat_integral': (0.0), #price units x seconds
    'error_star_derivative': (0.0), #price units per second
    'error_hat_derivative': (0.0), #price units per second
    #'target_rate': (0.0), #price units per second
    #'target_price': (2.0), #price units
    'market_price': target_price, #price units
    #'debt_price': (2.0), #price units
    'blockheight': 0, # block offset (init 0 simplicity)
    # # Env. process states
    # 'seconds_passed': int(0), 
    # 'price_move': 1.0,
    # CDP model states
    'timedelta': 0, # seconds
    'cumulative_time': 0, # seconds
    'timestamp': dt.datetime.strptime('12/18/17', '%m/%d/%y'), # datetime
    'cdps': cdps,
    # Loaded from exogenous parameter
    'eth_price': eth_price, # dollars
    # v
    'eth_collateral': eth_collateral, # Q
    'eth_locked': eth_collateral, # v1
    'eth_freed': 0, # v2
    'eth_bitten': 0, # v3 "liquidated"
    # u
    'principal_debt': principal_debt, # D1
    'rai_drawn': principal_debt, # u1 "minted"
    'rai_wiped': 0, # u2 "burned" in repayment
    'rai_bitten': 0, # u3 "burned" in liquidation
    # w
    'accrued_interest': 0, # D2
    'system_revenue': 0, # R
    'stability_fee': 0.015 / (30 * 24 * 3600), # per second interest rate (1.5% per month)
    'interest_dripped': 0, # w1 interest collected
    'interest_wiped': 0, # w2, interest repaid - in practice acrues to MKR holders, because interest is actually acrued by burning MKR
    'interest_bitten': 0, # w3
    'target_price': target_price, # dollars == redemption price
    'target_rate': 0 # per second interest rate (X% per month) == redemption rate
}