# Experiment Summary

Primary control parameters:
1. alpha (anti-windup)
2. Kp
3. Ki
4. control_period

Secondary control parameters:
1. liquidation_ratio
2. liquidity_threshold

TWAP parameters:
1. window_size; default 15 hours
2. max_window_size; fixed 21 hours
3. granularity; default 5

KPIs / metrics:
* liquidity_threshold: (metric + deliverable) reserves of RAI in Uniswap (as fraction of total supply)

Misc. parameters:
* debt_ceiling setter
