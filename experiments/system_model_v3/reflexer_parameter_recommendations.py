import datetime
from decimal import Decimal

# Constants
RAY=10**27

# Parameters
liquidation_ratio = Decimal('1.45') * RAY

## Control Parameters (experiment subset 12)
kp = int(2.000000e-07 * RAY)
ki = int(-5.000000e-09 * RAY)
control_period = int(14400 * RAY)
alpha = 999000000000000000000000000 # .999 scaled by RAY

## TWAP
window_size = int(16*3600 * RAY)
max_window_size = int(24*3600 * RAY)
granularity = int(4 * RAY)

# Liquidity Threshold
critical_liquidity_threshold = 0.029613389133736193 # market slippage 90th percentile mean for failed simulations (based on stability and volatility KPIs)

configuration = f'''
# Parameter Recommendations {datetime.datetime.now().isoformat()}
(scaled by {RAY=})

liquidation_ratio={str(liquidation_ratio)}

## Control Parameters
{kp=}
{ki=}
{control_period=}
{alpha=} (leak; .999 scaled by RAY)

## TWAP
{window_size=}
{max_window_size=}
{granularity=}

# Liquidity Threshold
Market slippage 90th percentile mean for failed simulations (based on stability KPIs)
* {critical_liquidity_threshold=}
'''

print(configuration)
