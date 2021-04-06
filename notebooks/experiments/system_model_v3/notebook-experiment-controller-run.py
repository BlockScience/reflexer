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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Experiment Analysis
#

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
import plotly.io as pio
pio.renderers.default = "png"
png_renderer = pio.renderers["png"]
png_renderer.width = 1000
png_renderer.height = 600
from pprint import pprint

# %%
# Update dataframe display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)

# %% [markdown]
# # Load Results

# %% [markdown]
# Using the experiment logs, select the experiment of interest from the specific HDF5 store file (these datasets are very large, and won't be committed to repo):

# %%
experiment_results = 'experiments/system_model_v3/experiment_controller_run/experiment_results.hdf5'
experiment_results2 = 'experiments/system_model_v3/experiment_controller_run/experiment_results_search.hdf5'

# %%
#tmp
experiment_results_keys = []
with pd.HDFStore(experiment_results2) as store:
    experiment_results_keys = list(filter(lambda x: "results" in x, store.keys()))
    exceptions_keys = list(filter(lambda x: "exceptions" in x, store.keys()))
experiment_results_keys


# %%
# tmp

res_ts2 = '2021-03-30T13:09:02.653017'
experiment_results_key2 = 'results_' + res_ts2 # Or select last result: experiment_results_keys[-1]
experiment_timestamp2 = experiment_results_key2.strip('results_')
exceptions_key2 = 'exceptions_' + experiment_timestamp2
experiment_timestamp2

# %%
experiment_results_keys = []
with pd.HDFStore(experiment_results) as store:
    experiment_results_keys = list(filter(lambda x: "results" in x, store.keys()))
    exceptions_keys = list(filter(lambda x: "exceptions" in x, store.keys()))

# %%
# A list of all experiment result keys
experiment_results_keys

# %%
# A list of all experiment result exception keys
exceptions_keys

# %%
# Copy a results_ key from the above keys to select the experiment
res_ts = '2021-03-30T13:10:07.059152'
experiment_results_key = 'results_' + res_ts # Or select last result: experiment_results_keys[-1]
experiment_timestamp = experiment_results_key.strip('results_')
exceptions_key = 'exceptions_' + experiment_timestamp
experiment_timestamp

# %%
df_raw = pd.read_hdf(experiment_results, experiment_results_key)
df_raw2 = pd.read_hdf(experiment_results2, experiment_results_key2)
exc_raw = pd.read_hdf(experiment_results, exceptions_key)
exc_raw2 = pd.read_hdf(experiment_results2, exceptions_key2)

# %% [markdown]
# Get experiment exceptions, tracebacks, and simulation metadata for further analysis:

# %%
exc_raw.head(1000)

# %% [markdown]
# # Post Process Results

# %%
from experiments.system_model_v3.post_process_search import post_process_results

#from experiments.system_model_v3.experiment_controller_run import params
from models.system_model_v3.model.params.init import params


# %% [markdown]
# Remove substeps, add `set_params` to dataframe, and add post-processing columns:

# %%
df = post_process_results(df_raw, params, set_params=['kp', 'ki', 'kd', 'alpha'])
#df
df2 = post_process_results(df_raw2, params, set_params=['kp', 'ki', 'kd', 'alpha'])
#df

# %%
df['target_rate'].head(34).tail(3)

# %%
df2['target_rate'].head(34).tail(3)

# %%
h = df.head(31)
h2 = df2.head(31)
print(h.compare(h2))

# %%
df['run'].head(10)

# %%
# %%capture
# Save the processed results to the same HDF5 store file
df.to_hdf(experiment_results, key=f'processed_results_{experiment_timestamp}')

# %% [markdown]
# # Control Parameters

# %%

# %%
df_control_parameters = df[['subset', 'kp', 'ki', 'kd']]

df_control_parameters = df_control_parameters.drop_duplicates(subset=['kp', 'ki', 'kd'])
#df_control_parameters

# %% [markdown]
# # Simulation Analysis

# %% [markdown]
# Get the initial target price to test stability conditions:

# %%
initial_target_price = df['target_price'].iloc[0]
initial_target_price
df['apy'] = ((1 + df['target_rate']) ** (60*60*24*356) - 1) * 100

# %% [markdown]
# Find all controller constant subsets where the price goes to zero:

# %%
df_market_price_zero = df.query("market_price <= 0.1*@initial_target_price")
df_market_price_zero[['subset', 'kp', 'ki', 'kd']].drop_duplicates(subset=['kp', 'ki', 'kd'])

# %% [markdown]
# Find all controller constant subsets where the price goes to infinity:

# %%
df_market_price_infinity = df.query("market_price > 10*@initial_target_price")
df_market_price_infinity[['subset', 'kp', 'ki', 'kd']].drop_duplicates(subset=['kp', 'ki', 'kd'])

# %% [markdown]
# Create dataframe of stable simulation scenarios.
#
# Stability is defined as:
# 1. The market price and scaled target price remaining within 0.1x and 10x the starting price, for all timesteps

# %%
initial_target_price = df['target_price'].iloc[0]
initial_eth_price = df['eth_price'].iloc[0]
last_timestep = df['timestep'].iloc[-1]

# %%
from experiments.metrics import score
SIMULATION_TIMESTEPS = 24 * 30 * 12
MONTE_CARLO_RUNS = 8

# %%
score = score('experiments/system_model_v3/experiment_controller_run', res_ts, params, MONTE_CARLO_RUNS, SIMULATION_TIMESTEPS)

# %%
score

# %%
"""
mean_cv_ratios=50.682489103510136
unfinished_pct=0.0
mean_degree_diffs=0.5037777258900092
stable_final_price_pct=0.0
too_high_apy_pct=0.017994858611825194
unstable_inter_prices_pct=0.6915167095115681
mse=1.595231229563733
"""

# %%
params

# %%

# %%

# %%

# %%

# %%

# %%

# %%
'''
df.query(f'subset == 0 & run == 1')[['timestamp', 'eth_price', 'run']].plot(
        title=f"Run i ETH",
        x='timestamp',
        y='eth_price', 
        color='run'
)
'''
for i in range(1, 9):
    fig = px.line(
        df.query(f'subset == 0 &run == {i}')[['timestamp', 'eth_price', 'run']],
        title=f"Run {i}",
        x="timestamp",
        y=["eth_price"]
    )
    fig.show()
    fig = px.line(
        df_stable_price.query(f'run == {i}'),
        title=f"Run {i}",
        x="timestamp",
        y=["market_price", "market_price_twap", "target_price"],
        facet_col="kp",
        facet_row="kd",
        facet_col_wrap=2,
        height=1000
    )
    # fig.for_each_annotation(lambda a: a.update(text = f"kp={param_sweep[int(a.text.split('=')[-1])]['kp']} ki={param_sweep[int(a.text.split('=')[-1])]['ki']}"))
    fig.show()
    fig = px.line(
        df_stable_price.query(f'run == {i}'),
        title=f"Run {i} rates",
        x="timestamp",
        y=["apy"],
        facet_col="kp",
        facet_row="kd",
        facet_col_wrap=2,
        height=1000
    )
    # fig.for_each_annotation(lambda a: a.update(text = f"kp={param_sweep[int(a.text.split('=')[-1])]['kp']} ki={param_sweep[int(a.text.split('=')[-1])]['ki']}"))
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
