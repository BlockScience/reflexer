# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python (Reflexer)
#     language: python
#     name: python-reflexer
# ---

# %% [markdown]
# # Experiment Analysis: Controller parameter stability search
# Perform shocks of ETH price to test controller parameter stability, without stochastic processes.
#
# * See `experiments/system_model_v3/experiment_shocks.py`

# %% [markdown]
# # Setup and Dependencies

# %%
# Set project root folder, to enable importing project files from subdirectories
from pathlib import Path
import os

path = Path().resolve()
root_path = str(path).split('notebooks')[0]
os.chdir(root_path)

# Force reload of project modules, sometimes necessary for Jupyter kernel
# %load_ext autoreload
# %autoreload 2

# Display framework versions for easy debugging
# %pip show cadCAD
# %pip show radcad

# %%
# Import all shared dependencies and setup
from shared import *

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import plotly.io as pio
# pio.renderers.default = "png"
from pprint import pprint

# %%
# Update dataframe display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)

# %% [markdown]
# # Load Dataset

# %%
processed_results = 'experiments/system_model_v3/experiment_monte_carlo/processed_results.hdf5'

# %%
df = pd.read_hdf(processed_results, key='processed_results')
df

# %% [markdown]
# Get experiment exceptions, tracebacks, and simulation metadata for further analysis:

# %% [markdown]
# # Process KPIs

# %%
df_kpis = df.copy()

# %%
df_kpis['target_price_scaled'] = df_kpis[['target_price', 'liquidation_ratio', 'rescale_target_price']] \
    .apply(lambda x: (x['target_price'] * x['liquidation_ratio']) if x['rescale_target_price'] else x['target_price'], axis=1)
df_kpis['target_price_scaled']

# %% [markdown]
# ## Stability

# %% [markdown]
# **Stability** threshold of system: defined as the maximum value for relative frequency of simulation runs that are unstable. Unstable is measured as fraction of runs where:
#   - market price runs to infinity/zero (e.g. upper bound 10xPI; lower bound 0.10xPI if initial price is PI);
#   - redemption price runs to infinity/zero (e.g. upper bound 10xPI; lower bound 0.10xPI if initial price is PI);
#   - Uniswap liquidity (RAI reserve) runs to zero;
#   - CDP position (total ETH collateral) runs to infinity/zero.

# %%
initial_target_price = df_kpis['target_price'].iloc[0]
initial_target_price

# %%
df_kpis[['market_price', 'target_price_scaled', 'RAI_balance', 'eth_collateral']].describe()

# %%
df_stability = df_kpis.groupby(['subset', 'run'])

df_stability = df_stability.agg({
    'market_price': ['min', 'max'],
    'target_price_scaled': ['min', 'max'],
    'RAI_balance': ['min', 'max'],
    'eth_collateral': ['min', 'max'],
})
df_stability.columns = [
    'market_price_min', 'market_price_max',
    'target_price_min', 'target_price_max',
    'RAI_balance_min', 'RAI_balance_max',
    'eth_collateral_min', 'eth_collateral_max'
]
df_stability = df_stability.reset_index()

df_stability['stability_market_price'] = df_stability \
    .apply(lambda x: x['market_price_min'] >= 0.1*initial_target_price and x['market_price_max'] <= 10*initial_target_price, axis=1)

df_stability['stability_target_price'] = df_stability \
    .apply(lambda x: x['target_price_min'] >= 0.1*initial_target_price and x['target_price_max'] <= 10*initial_target_price, axis=1)

# TODO: discuss threshold
df_stability['stability_uniswap_liquidity'] = df_stability \
    .apply(lambda x: x['RAI_balance_min'] >= 100e3, axis=1)

# TODO: discuss threshold
df_stability['stability_cdp_system'] = df_stability \
    .apply(lambda x: x['eth_collateral_min'] >= 20e3 and x['eth_collateral_max'] <= 160000, axis=1)

df_stability['kpi_stability'] = df_stability \
    .apply(lambda x: ( \
        x.stability_cdp_system == True and \
        x.stability_uniswap_liquidity == True and \
        x.stability_market_price == True and \
        x.stability_target_price == True) \
        , axis=1)

df_stability.query('kpi_stability == True')

# %% [markdown]
# ## Volatility

# %% [markdown]
# **Volatility** threshold of market price: defined as the maximum value for the **standard deviation** computed. Defined relative to ETH price volatility. Definition: ratio of RAI price volatility / ETH price volatility is not to exceed 0.5.
#   - over simulation period;
#   - as moving average with 10-day window.

# %%
df_volatility_grouped = df_kpis.groupby(['subset', 'run'])

df_volatility_grouped = df_volatility_grouped.agg({'market_price': ['std'], 'eth_price': ['std']})
df_volatility_grouped.columns = ['market_price_std', 'eth_price_std']
df_volatility_grouped = df_volatility_grouped.reset_index()

df_volatility_grouped['volatility_ratio_simulation'] = \
    df_volatility_grouped[['market_price_std', 'eth_price_std']] \
    .apply(lambda x: x['market_price_std'] / x['eth_price_std'], axis=1)

df_volatility_grouped['kpi_volatility_simulation'] = df_volatility_grouped.apply(lambda x: x['volatility_ratio_simulation'] <= 0.5, axis=1)

df_volatility_grouped

# %%
df_volatility_series = pd.DataFrame()
group = df_kpis.groupby(['subset', 'run'])

df_volatility_series['market_price_moving_average_std'] = group['market_price'].rolling(24*10, 1).std()
df_volatility_series['eth_price_moving_average_std'] = group['eth_price'].rolling(24*10, 1).std()
df_volatility_series.query('subset == 0 and run == 1')

# %%
df_volatility_series['volatility_ratio_window'] = df_volatility_series.apply(lambda x: x['market_price_moving_average_std'] / x['eth_price_moving_average_std'], axis=1)
df_volatility_series.query('subset == 0 and run == 1')

# %%
df_volatility_series['kpi_volatility_window_series'] = df_volatility_series.apply(lambda x: x['volatility_ratio_window'] != x['volatility_ratio_window'] or x['volatility_ratio_window'] <= 0.5, axis=1)
df_volatility_series['kpi_volatility_window_mean'] = df_volatility_series.groupby(['subset', 'run'])['kpi_volatility_window_series'].transform(lambda x: x.mean())
df_volatility_series

# %%
df_volatility_series['kpi_volatility_window_mean'].describe()

# %%
df_volatility_series['kpi_volatility_window'] = df_volatility_series.groupby(['subset', 'run'])['kpi_volatility_window_mean'].transform(lambda x: x > 0.98)
df_volatility_series

# %%
df_volatility_series.query('kpi_volatility_window == False')

# %%
df_volatility_series['kpi_volatility_window'].value_counts()

# %% [markdown]
# ## Merge KPI dataframes

# %%
df_kpis = pd.merge(df_volatility_grouped, df_volatility_series, on=['run','subset'], how='inner')
df_kpis = df_kpis.drop(['volatility_ratio_window', 'kpi_volatility_window_mean', 'kpi_volatility_window_series', 'market_price_moving_average_std', 'eth_price_moving_average_std'], axis=1)
df_kpis = pd.merge(df_kpis, df_stability, on=['run','subset'], how='inner')
df_kpis = df_kpis.groupby(['subset', 'run']).first()

# %%
df_kpis['kpi_volatility'] = df_kpis.apply(lambda x: x['kpi_volatility_simulation'] and x['kpi_volatility_window'], axis=1)

# %%
df_kpis.query('kpi_volatility == False')

# %%
df_kpis.query('kpi_stability == False')

# %% [markdown]
# ## Liquidity

# %% [markdown]
# **Liquidity** threshold of secondary market: defined as the maximum slippage value below which the controller is allowed to operate.
# * __NB__: Threshold value will be determined by experimental outcomes, e.g. sample mean of the Monte Carlo outcomes of the slippage value when the system becomes unstable. Would like variance/std deviation of the Monte Carlo slippage series to be small (tight estimate), but can report both mean and variance as part of recommendations

# %%
critical_liquidity_threshold = None

# %%
df_liquidity = df[['subset', 'run', 'timestep', 'market_slippage']].copy()
df_liquidity = pd.merge(df_liquidity, df_kpis, how='inner', on=['subset', 'run'])
df_liquidity['market_slippage_abs'] = df_liquidity['market_slippage'].transform(lambda x: abs(x))
df_liquidity

# %%
df_liquidity.query('subset == 0')['market_slippage_abs'].describe([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.90])

# %%
df_liquidity['market_slippage_percentile'] = df_liquidity.groupby(['subset', 'run'])['market_slippage'].transform(lambda x: x.quantile(.90))
df_liquidity

# %%
# TODO: in this subset none fail both, so for testing we'll select one
df_liquidity_failed = df_liquidity.query('kpi_stability == False')
df_liquidity_failed['market_slippage_percentile_mean'] = df_liquidity_failed.groupby(['subset'])['market_slippage_percentile'].transform(lambda x: x.mean())

# %%
critical_liquidity_threshold = df_liquidity_failed['market_slippage_percentile_mean'].mean()
critical_liquidity_threshold

# %%
df_liquidity_grouped = df_liquidity.groupby(['subset', 'run']).mean()
df_liquidity_grouped = df_liquidity_grouped.reset_index()
df_liquidity_grouped['kpi_liquidity'] = df_liquidity_grouped.apply(lambda x: x['market_slippage_percentile'] <= critical_liquidity_threshold, axis=1)
df_liquidity_grouped

# %%
df_kpis = df_liquidity_grouped[['subset', 'run', 'kpi_stability', 'kpi_volatility', 'kpi_liquidity']]
df_kpis = df_kpis.groupby(['subset', 'run']).first()

# %%
df_kpis.query('kpi_stability == True and kpi_volatility == True and kpi_liquidity == True')

# %% [markdown]
# ## Save KPI Results

# %%
df_kpis.to_pickle('experiments/system_model_v3/kpi_dataset.pickle')

# %% [markdown]
# # Sensitivity Analysis

# %%
df_kpis = pd.read_pickle('experiments/system_model_v3/kpi_dataset.pickle')

# %%
from cadcad_machine_search.visualizations import kpi_sensitivity_plot

# df = dataframe with KPI values stored as columns, with runs as rows
# control_params = column names in df containing control parameter values for each run

VOLATILITY_THRESHOLD = 0.5
MAXIMUM_PRICE = 31.4
MINIMUM_PRICE = 0.314
MINIMUM_RAI_BALANCE = 0
MINIMUM_COLLATERAL_BALANCE = 0

kpis = {
    'volatility_simulation'        : lambda df: df['volatility_ratio_simulation'],
    'volatility_window_mean'       : lambda df: df['volatility_ratio_window'].mean(),
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

# %% [markdown]
# # Simulation Parameter Subset Overview

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='market_price', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='market_slippage', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='liquidity_demand', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='RAI_balance', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='ETH_balance', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='principal_debt', color='subset')

# %%
df_kpis.query('run == 1').plot(x='timestamp', y='eth_collateral', color='subset')

# %% [markdown]
# # Control Parameters

# %%
from radcad.core import generate_parameter_sweep

param_sweep = generate_parameter_sweep(params)

# %%
df_control_parameters = df[['subset', 'kp', 'ki']]

df_control_parameters = df_control_parameters.drop_duplicates(subset=['kp', 'ki'])
df_control_parameters

# %% [markdown]
# # Simulation Analysis

# %%
df.query('subset == 0')[['timestamp', 'eth_price', 'run']].plot(
    title="ETH price shocks (positive and negative step and impulse; one shock type for each run)",
    x='timestamp',
    y='eth_price', 
    color='run'
)

# %%
fig = px.line(
    df.query('run == 1'),
    title="Price response for all control parameter subsets, first run",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price_scaled"], 
    facet_col="ki", 
    facet_row="kp", 
    height=1000
)
fig.show()

# %% [markdown]
# Get the initial target price to test stability conditions:

# %%
initial_target_price = df['target_price'].iloc[0]
initial_target_price

# %% [markdown]
# Find all controller constant subsets where the price goes to zero:

# %%
df_market_price_zero = df.query("market_price <= 0.1*@initial_target_price")
df_market_price_zero[['subset', 'kp', 'ki']].drop_duplicates(subset=['kp', 'ki'])

# %% [markdown]
# Find all controller constant subsets where the price goes to infinity:

# %%
df_market_price_infinity = df.query("market_price > 10*@initial_target_price")
df_market_price_infinity[['subset', 'kp', 'ki']].drop_duplicates(subset=['kp', 'ki'])

# %% [markdown]
# Create dataframe of stable simulation scenarios.
#
# Stability is defined as:
# 1. The market price and scaled target price remaining within 0.1x and 10x the starting price, for all timesteps

# %%
df['stable_price'] = False
df.loc[df.eval("""
0.1*@initial_target_price < market_price <= 10*@initial_target_price and 0.1*@initial_target_price < target_price_scaled <= 10*@initial_target_price
"""), 'stable_price'] = True
df_stable_price = df.groupby("subset").filter(lambda x: all(x.query('timestep > 24*2')['stable_price'])) #  and x['timestep'].max() == SIMULATION_TIMESTEPS
df_stable_price['subset'].unique()

# %%
fig = px.line(
    df_stable_price.query('run == 1'),
    title="Base case: Stable ETH price response",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price"],
    facet_col="kp",
    facet_row="ki",
    facet_col_wrap=2,
    height=1000
)
# fig.for_each_annotation(lambda a: a.update(text = f"kp={param_sweep[int(a.text.split('=')[-1])]['kp']} ki={param_sweep[int(a.text.split('=')[-1])]['ki']}"))
fig.show()

# %%
fig = px.line(
    df_stable_price.query('run == 2'),
    title="ETH price 30% step response",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price_scaled"],
    facet_col="kp",
    facet_row="ki",
    facet_col_wrap=2,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price.query('run == 3'),
    title="ETH price 30% impulse response",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price_scaled"],
    facet_col="kp",
    facet_row="ki",
    facet_col_wrap=2,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price.query('run == 4'),
    title="ETH price negative 30% step response",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price_scaled"],
    facet_col="kp",
    facet_row="ki",
    facet_col_wrap=2,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price.query('run == 5'),
    title="ETH price negative 30% impulse response",
    x="timestamp",
    y=["market_price", "market_price_twap", "target_price_scaled"],
    facet_col="kp",
    facet_row="ki",
    facet_col_wrap=2,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price, 
    title="Reflexer principal debt",
    x="timestamp", 
    y=["principal_debt"], 
    color='run', 
    facet_col="subset", 
    facet_col_wrap=5,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price, 
    title="Secondary market RAI balance",
    x="timestamp", 
    y=["RAI_balance"], 
    color='run', 
    facet_col="subset", 
    facet_col_wrap=5,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price, 
    title="Reflexer ETH collateral",
    x="timestamp", 
    y=["eth_collateral"], 
    color='run', 
    facet_col="subset", 
    facet_col_wrap=5,
    height=1000
)
fig.show()

# %%
fig = px.line(
    df_stable_price, 
    title="Secondary market ETH balance",
    x="timestamp", 
    y=["ETH_balance"], 
    color='run', 
    facet_col="subset", 
    facet_col_wrap=5,
    height=1000
)
fig.show()

# %%
df_stable_price.plot(
    x='timestamp', 
    y=['collateralization_ratio'], 
    title='Collateralization ratio', 
    facet_col="subset",
    facet_col_wrap=5,
    height=1000
)
