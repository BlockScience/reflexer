from cadcad_machine_search.visualizations import kpi_sensitivity_plot

# df = dataframe with KPI values stored as columns, with runs as rows
# control_params = column names in df containing control parameter values for each run

VOLATILITY_THRESHOLD = 0.5
MAXIMUM_PRICE = 31.4
MINIMUM_PRICE = 0.314
MINIMUM_RAI_BALANCE = 0
MINIMUM_COLLATERAL_BALANCE = 0

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
         'low_volatility'  : lambda metrics: ( metrics['volatility_simulation'] < VOLATILITY_THRESHOLD ) and
                            ( metrics['volatility_window_mean'] < VOLATILITY_THRESHOLD ),
         'high_stability'  : lambda metrics: ( metrics['market_price_max'] < MAXIMUM_PRICE ) and 
                            ( metrics['market_price_min'] > MINIMUM_PRICE ) and 
                            ( metrics['redemption_price_max'] < MAXIMUM_PRICE ) and 
                            ( metrics['redemption_price_min'] > MINIMUM_PRICE ) and
                            ( metrics['rai_balance_uniswap_min'] > MINIMUM_RAI_BALANCE) and
                            ( metrics['cdp_collateral_balance_min'] > MINIMUM_COLLATERAL_BALANCE )
}

for goal in goals:
    kpi_sensitivity_plot(df, goals[goal], control_params)
     
