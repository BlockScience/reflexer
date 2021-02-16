from cadcad_machine_search.visualizations import plot_goal_ternary

# df = dataframe with KPI values stored as columns, with runs as rows
# control_params = column names in df containing control parameter values for each run

kpis = {'volatility_simulation'        : lambda df: df['volatility_ratio_simulation'],
        'volatility_window_mean'            : lambda df: df['volatility_ratio_window'].mean(),
        'market_price_max'             : lambda df: df['market_price'].max(),
        'market_price_min'             : lambda df: df['market_price'].min(),
        'redemption_price_max'         : lambda df: df['redemption_price'].max(),
        'redemption_price_min'         : lambda df: df['redemption_price'].min(),
        'rai_balance_uniswap_min'      : lambda df: df['rai_balance'].min(),
        'cdp_collateral_balance_min'   : lambda df: df['cdp_collateral'].min(),
        'price_change_percentile_mean' : lambda df: df['ninetieth_percentile_price_change_for_failed_runs'].mean()
       }
       
goals = {}

goals = {
         'low_volatility' : lambda metrics: -0.5 * ( metrics['volatility_simulation'] +
                            metrics['volatility_window_mean'] ),
         'high_stability'  : lambda df: -(1/6) * ( metrics['market_price_max'] + 
                            1 / metrics['market_price_min'] + metrics['redemption_price_max'] +
                            1 / metrics['redemption_price_min'] + 1 / metrics['rai_balance_uniswap_min'] +
                            1 / metrics['cdp_collateral_balance_min'] ),
         'liquidity'  : lambda metrics: metrics['price_change_percentile_mean'],
         'combined'   : lambda goals: goals[0] + goals[1] + goals[2]
       }
       
plot_goal_ternary(df, kpis, goals, control_params)
