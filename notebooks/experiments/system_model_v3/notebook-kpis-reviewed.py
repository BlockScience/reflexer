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

# %%
# %load_ext autotime
# danlessa was here

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
# danlessa was here
import pandas as pd
from pandarallel import pandarallel
pandarallel.initialize(progress_bar=False)

# %%
# Import all shared dependencies and setup
#from shared import *

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import plotly.io as pio
#pio.renderers.default = "png"
from pprint import pprint

# %%
# Update dataframe display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)
pd.options.plotting.backend = "plotly"

# %% [markdown]
# # Load Dataset

# %%
processed_results = 'experiments/system_model_v3/experiment_monte_carlo/processed_results.hdf5'

# %%
df = pd.read_hdf(processed_results, key='results')
df

# %% [markdown]
# # Process KPIs

# %%
df_kpis = df.copy()

# %%
# danlessa was here 2.5s -> 0.9s
cols = ['target_price', 'liquidation_ratio', 'rescale_target_price']
f = lambda x: (x['target_price'] * x['liquidation_ratio']) if x['rescale_target_price'] else x['target_price']
df_kpis['target_price_scaled'] = df_kpis[cols].parallel_apply(f, axis=1)
df_kpis['target_price_scaled'].head(10)

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
df_kpis[['market_price', 'target_price_scaled', 'RAI_balance', 'eth_collateral']].describe([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.90])

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
    .apply(lambda x: x['RAI_balance_min'] >= 500e3, axis=1)

# TODO: discuss threshold
df_stability['stability_cdp_system'] = df_stability \
    .apply(lambda x: x['eth_collateral_min'] >= 20e3, axis=1)

df_stability['kpi_stability'] = df_stability \
    .apply(lambda x: ( \
        x.stability_cdp_system == True and \
        x.stability_uniswap_liquidity == True and \
        x.stability_market_price == True and \
        x.stability_target_price == True) \
        , axis=1)

df_stability.query('kpi_stability == True').head(5)

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

df_volatility_grouped.head(5)

# %%
df_volatility_series = pd.DataFrame()
group = df_kpis.groupby(['subset', 'run'])

df_volatility_series['market_price_moving_average_std'] = group['market_price'].rolling(24*10, 1).std()
df_volatility_series['eth_price_moving_average_std'] = group['eth_price'].rolling(24*10, 1).std()
df_volatility_series.query('subset == 0 and run == 1').head(5)

# %%
# danlessa was here 2.2s -> 1.2s
f = lambda x: x['market_price_moving_average_std'] / x['eth_price_moving_average_std']
df_volatility_series['volatility_ratio_window'] = df_volatility_series.parallel_apply(f, axis=1)
df_volatility_series.query('subset == 0 and run == 1').head(5)

# %%
# danlessa was here. 2.8s -> 1.3s
f = lambda x: x['volatility_ratio_window'] != x['volatility_ratio_window'] or x['volatility_ratio_window'] <= 0.5
df_volatility_series['volatility_window_series'] = df_volatility_series.parallel_apply(f, axis=1)
df_volatility_series['volatility_window_mean'] = (df_volatility_series.groupby(['subset', 'run'])
                                                                           ['volatility_window_series']
                                                                          .transform(lambda x: x.mean()))
df_volatility_series.head(5)

# %%
df_volatility_series['volatility_window_mean'].describe()

# %%
df_volatility_series['kpi_volatility_window'] = df_volatility_series.groupby(['subset', 'run'])['volatility_window_mean'].transform(lambda x: x > 0.98)
df_volatility_series

# %%
df_volatility_series.query('kpi_volatility_window == False')

# %%
df_volatility_series['kpi_volatility_window'].value_counts()

# %% [markdown]
# ## Merge KPI dataframes

# %%
# danlessa was here. 0.2s -> 80ms
cols_to_drop = {'volatility_ratio_window',
                'volatility_window_series',
                'market_price_moving_average_std',
                'eth_price_moving_average_std',
                'index'}

index_cols = ['run','subset']
dfs_to_join = [df_volatility_grouped, df_volatility_series, df_stability]

for i, df_to_join in enumerate(dfs_to_join):
    _df = df_to_join.reset_index()
    remaining_cols = list(set(_df.columns) - cols_to_drop)
    _df = (_df.reset_index()
              .loc[:, remaining_cols]
              .groupby(index_cols)
              .first()
          )
    dfs_to_join[i] = _df


df_kpis = (dfs_to_join[0].join(dfs_to_join[1], how='inner')
                         .join(dfs_to_join[2], how='inner')
          )

# %%
df_kpis['kpi_volatility'] = df_kpis.apply(lambda x: x['kpi_volatility_simulation'] and x['kpi_volatility_window'], axis=1)

# %%
df_kpis.query('kpi_volatility == False and kpi_stability == False')

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
# %%capture
df_liquidity_failed = df_liquidity.query('kpi_volatility == False and kpi_stability == False')
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
print(f'''
{round(df_kpis.query('kpi_stability == True and kpi_volatility == True and kpi_liquidity == True').count().iloc[0]*100/df_kpis.count().iloc[0])}% successful KPIs
''')

# %% [markdown]
# ## Save KPI Results

# %%
df_kpis.to_pickle('experiments/system_model_v3/experiment_monte_carlo/kpi_dataset.pickle')

# %%
df_kpis = pd.read_pickle('experiments/system_model_v3/experiment_monte_carlo/kpi_dataset.pickle')

# %% [markdown]
# # Sensitivity Analysis

# %%
df.head(5)

# %%
df_kpis.head(5)

# %%
df_sensitivity = pd.merge(df, df_kpis, on=['run','subset'], how='inner')
df_sensitivity

# %%
df_sensitivity = df_sensitivity.reset_index()

# %%
# Controller on / off
# Rescale and arb. considers lr; both true or false
# liquidity_demand_shock 10 /50 %

# %%
control_params = [
    'ki',
    'kp',
    'control_period',
]

# %%
from cadcad_machine_search.visualizations import kpi_sensitivity_plot

# df = dataframe with KPI values stored as columns, with runs as rows
# control_params = column names in df containing control parameter values for each run

# kpis = {
#     'volatility_simulation'        : lambda df: df['volatility_ratio_simulation'],
#     'volatility_window_mean'       : lambda df: df['volatility_window_mean'],
#     'market_price_max'             : lambda df: df['market_price'].max(),
#     'market_price_min'             : lambda df: df['market_price'].min(),
#     'redemption_price_max'         : lambda df: df['target_price_scaled'].max(),
#     'redemption_price_min'         : lambda df: df['target_price_scaled'].min(),
#     'rai_balance_uniswap_min'      : lambda df: df['RAI_balance'].min(),
#     'cdp_collateral_balance_min'   : lambda df: df['eth_collateral'].min(),
#     'price_change_percentile_mean' : lambda df: critical_liquidity_threshold
# }

goals = {
    'low_volatility'  : lambda metrics: metrics['kpi_volatility'],
    'high_stability'  : lambda metrics: metrics['kpi_stability'],
    'liquidity_threshold': lambda metrics: metrics['kpi_liquidity'],
}

#     'controller_enabled',
#     'liquidity_demand_shock',
#     'arbitrageur_considers_liquidation_ratio',
#     'rescale_target_price'

kpi_sensitivity_plot(df_sensitivity, goals['low_volatility'], control_params)

# for scenario in df_sensitivity['controller_enabled'].unique():
#     df = df_sensitivity.query(f'controller_enabled == {scenario}')
#     for goal in goals:
#         kpi_sensitivity_plot(df, goals[goal], control_params)

# for scenario in df_sensitivity['liquidity_demand_shock'].unique():
#     df = df_sensitivity.query(f'liquidity_demand_shock == {scenario}')
#     for goal in goals:
#         kpi_sensitivity_plot(df, goals[goal], control_params)

# TODO:
# for scenario in df_sensitivity['controller_enabled'].unique():
#     df = df_sensitivity.query(f'controller_enabled == {scenario}')
#     for goal in goals:
#         kpi_sensitivity_plot(df, goals[goal], control_params)

# %%
from cadcad_machine_search.visualizations import plot_goal_ternary

# df = dataframe with KPI values stored as columns, with runs as rows
# control_params = column names in df containing control parameter values for each run

kpis = {
    'volatility_simulation'        : lambda df: df['volatility_ratio_simulation'],
    'volatility_window_mean'            : lambda df: df['volatility_ratio_window'].mean(),
    'market_price_max'             : lambda df: df['market_price'].max(),
    'market_price_min'             : lambda df: df['market_price'].min(),
    'redemption_price_max'         : lambda df: df['target_price_scaled'].max(),
    'redemption_price_min'         : lambda df: df['target_price_scaled'].min(),
    'rai_balance_uniswap_min'      : lambda df: df['RAI_balance'].min(),
    'cdp_collateral_balance_min'   : lambda df: df['eth_collateral'].min(),
    'price_change_percentile_mean' : lambda df: critical_liquidity_threshold
}

goals = {
    'low_volatility' : lambda metrics: -0.5 * ( metrics['volatility_simulation'] +
                    metrics['price_change_percentile_mean'] ),
    'high_stability'  : lambda metrics: -(1/6) * ( metrics['market_price_max'] + 
                    1 / metrics['market_price_min'] + metrics['redemption_price_max'] +
                    1 / metrics['redemption_price_min'] + 1 / metrics['rai_balance_uniswap_min'] +
                    1 / metrics['cdp_collateral_balance_min'] ),
    'liquidity'  : lambda metrics: -metrics['price_change_percentile_mean'],
    'combined'   : lambda goals: goals[0] + goals[1] + goals[2]
}


for scenario in df_sensitivity['controller_enabled'].unique():
    df = df_sensitivity.query(f'controller_enabled == {scenario}')
    plot_goal_ternary(df, kpis, goals, control_params)

for scenario in df_sensitivity['liquidity_demand_shock'].unique():
    df = df_sensitivity.query(f'liquidity_demand_shock == {scenario}')
    plot_goal_ternary(df, kpis, goals, control_params)   

# TODO:
# for scenario in df_sensitivity['controller_enabled'].unique():
#     df = df_sensitivity.query(f'controller_enabled == {scenario}')
#     for goal in goals:
#         kpi_sensitivity_plot(df, goals[goal], control_params)

# TODO: save both for presentation

# %%
# TODO:
# Kp, Ki, control period
# Alpha

# All pass:
# Minimum volatility (values)
# Minimum liquidity (values)

# %%
# TODO: Timeseries 

# %%
# TODO: Experiment execution metrics

# Runtime (final + sanity checking)
# Number of exp.
# Number of parameters per exp.
# MC runs
# Timesteps * runs * subsets
