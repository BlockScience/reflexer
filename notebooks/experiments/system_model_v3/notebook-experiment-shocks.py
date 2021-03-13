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
# # Load Results

# %% [markdown]
# Using the experiment logs, select the experiment of interest from the specific HDF5 store file (these datasets are very large, and won't be committed to repo):

# %%
experiment_results = 'experiments/system_model_v3/experiment_controller_sweep/experiment_results.hdf5'
#experiment_results = 'experiments/system_model_v3/experiment_shocks/experiment_results.hdf5'#

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
experiment_results_key = 'results_2021-03-13T05:04:26.436122' # Or select last result: experiment_results_keys[-1]
experiment_timestamp = experiment_results_key.strip('results_')
exceptions_key = 'exceptions_' + experiment_timestamp
experiment_timestamp

# %%
df_raw = pd.read_hdf(experiment_results, experiment_results_key)
df_raw.tail()

# %% [markdown]
# Get experiment exceptions, tracebacks, and simulation metadata for further analysis:

# %%
exceptions_df = pd.read_hdf(experiment_results, exceptions_key)
exceptions_df.head()

# %%
# Print the first 5 exceptions - indicating failed simulations
pprint(list(exceptions_df['exception'])[:5])

# %% [markdown]
# # Post Process Results

# %%
from experiments.system_model_v3.post_process import post_process_results

#from experiments.system_model_v3.experiment_shocks import params, SIMULATION_TIMESTEPS
from experiments.system_model_v3.experiment_controller_sweep import params, SIMULATION_TIMESTEPS


# %% [markdown]
# Remove substeps, add `set_params` to dataframe, and add post-processing columns:

# %%
df = post_process_results(df_raw, params, set_params=['ki', 'kp', 'liquidation_ratio'])
df

# %%
# %%capture
# Save the processed results to the same HDF5 store file
df.to_hdf(experiment_results, key=f'processed_results_{experiment_timestamp}')

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
    y=["market_price", "market_price_twap", "target_price"], 
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
0.1*@initial_target_price < market_price <= 10*@initial_target_price and 0.1*@initial_target_price < target_price <= 10*@initial_target_price
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
    y=["market_price", "market_price_twap", "target_price"],
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
    y=["market_price", "market_price_twap", "target_price"],
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
    y=["market_price", "market_price_twap", "target_price"],
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
    y=["market_price", "market_price_twap", "target_price"],
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
