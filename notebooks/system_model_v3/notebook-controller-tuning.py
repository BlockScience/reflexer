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

# %%
# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Debt Market Model
#
# The purpose of this notebook is to configure and simulate the full CDP and APT system model, using the historical Ethereum price as a driver, under different PI controller settings - enabled, disabled, `kp` and `ki`.

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

# Display cadCAD version for easy debugging
# %pip show cadCAD

# %%
# Import all shared dependencies and setup
from shared import *

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import plotly.io as pio
# pio.renderers.default = "png"

# %% [markdown]
# # Model Configuration

# %%
# Import the historical MakerDAO market data CSV file
from models.system_model_v3.model.params.init import env_process_df
env_process_df

# %%
from models.system_model_v3.model.state_variables.init import state_variables

state_variables.update({})

# %%
env_process_df.plot(y='Open')

# %%
import itertools

# exponents = list(range(-7, -5, 2))
# scales = list(range(-9, -1, 1))
# kp_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

# exponents = list(range(-7, -5, 2))
# scales = list(range(1, 9, 1))
# ki_sweep = [scale * 10**exponent for scale in scales for exponent in exponents]

kp_sweep = [1e-7]
ki_sweep = [-1e-7]

controller_sweep = list(itertools.product(kp_sweep, ki_sweep))
controller_sweep

# %%
from models.system_model_v3.model.params.init import params

# Update the default parameter values
params_update = {
    'controller_enabled': [True],
    'kp': [x[0] for x in controller_sweep], # proportional term for the stability controller: units 1/USD
    'ki': [x[1] for x in controller_sweep], # integral term for the stability controller: units 1/(USD*seconds)
    'liquidation_ratio': [1.5],
    'interest_rate': [1.03]
}

params.update(params_update)

# %%
# # %pip install https://github.com/danlessa/cadCAD/archive/danlessa_devel.zip --force-reinstall
# # %pip install cadCAD --force-reinstall
# # %pip install /Users/bscholtz/workspace/radCAD/dist/radcad-0.4.1.tar.gz

# %% [markdown]
# # Simulation Execution

# %%
# Set the number of simulation timesteps, with a maximum of `len(debt_market_df) - 1`
# SIMULATION_TIMESTEPS = len(env_process_df) - 1
SIMULATION_TIMESTEPS = 24 * 30

# %%
# Create a wrapper for the model simulation, and update the existing parameters and initial state
system_simulation = ConfigWrapper(system_model_v3, T=range(SIMULATION_TIMESTEPS), M=params, initial_state=state_variables)


# %%
del configs[:] # Clear any prior configs
system_simulation.append() # Append the simulation config to the cadCAD `configs` list
(simulation_result, _tensor_field, _sessions) = run(drop_midsteps=False) # Run the simulation

# %%
simulation_result

# %% [markdown]
# # Simulation Analysis

# %%
# Add new columns to dataframe
simulation_result = simulation_result.assign(eth_collateral_value = simulation_result.eth_collateral * simulation_result.eth_price)
simulation_result['collateralization_ratio'] = (simulation_result.eth_collateral * simulation_result.eth_price) / (simulation_result.principal_debt * simulation_result.target_price)

# Update dataframe display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)

simulation_result

# %% [markdown]
# ## Save simulation

# %%
# import datetime
# now = datetime.datetime.now()

# # Save the simulation result to a pickle file, for backup - this will be overwritten on the next simulation
simulation_result.to_pickle(f'./exports/system_model_v3/results.pickle')

# %%
import dill
import datetime
import subprocess


label = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
now = datetime.datetime.now()

# store in hdf5 file format 
store_file = './exports/system_model_v3/results.hdf5'
storedata = pd.HDFStore(store_file) 

# data
store_key = f'raw_results_system_model_v3_{str(label)}_{now.year}_{now.month}_{now.day}T{str(now.timestamp()).replace(".", "_")}'
storedata.put(store_key, simulation_result) 

# including metadata
metadata = {'date': now.isoformat(), 'params': dill.dumps(params_update) }
  
# getting attributes
storedata.get_storer(store_key).attrs.metadata = metadata 
  
# closing the storedata 
storedata.close() 
  
# getting data 
with pd.HDFStore(store_file) as storedata:
    data = storedata[store_key]
    metadata = storedata.get_storer(store_key).attrs.metadata

# %% [markdown]
# # Simulation Analysis

# %%
# Load the simulation result from a pickle file, specifying past results when necessary
# simulation_result = pd.read_pickle(f'exports/system_model_v3/results.pickle')

# Drop the simulation midsteps - the substeps that aren't used for generating plots
df = drop_dataframe_midsteps(simulation_result)
df

# %%
df['target_price'] = df['target_price'] * 1.5

# %% [markdown]
# ## Select simulation

# %%
# Select the first simulation and subset, this is only relevant when running parameter sweeps or Monte Carlo Runs
# The following plots are configured for single simulation results
# df = df.query('simulation == 0 and subset == 0')


# %%
import plotly.express as px

# %%
fig = px.line(df, x="timestamp", y=["market_price", "market_price_twap", "target_price"], facet_col="subset", facet_col_wrap=2, height=1000)
fig.show()

# %%
## Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['RAI_balance'], name="Uniswap RAI balance"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['principal_debt'], name="CDP system principal debt"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['ETH_balance'], name="Uniswap ETH balance"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['eth_collateral'], name="CDP system ETH collateral"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="Liquidity in CDPs and secondary market"
)

# Set x-axis title
fig.update_xaxes(title_text="Timestamp")

# Set y-axes titles
fig.update_yaxes(title_text="RAI ($)", secondary_y=False)
fig.update_yaxes(title_text="ETH (Ether)", secondary_y=True)

fig.update_layout(
    autosize=False,
    width=1000,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
)

fig.show()

# %%
df.plot(x='timestamp', y=['collateralization_ratio'], title='Collateralization Ratio')

# %%
# df = df.query("subset == 0")

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['target_price'], name="Target price"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['market_price_twap'], name="Market price TWAP"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['eth_price'], name="ETH price"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="Market and Target Price vs. ETH Price"
)

# Set x-axis title
fig.update_xaxes(title_text="Timestamp")

# Set y-axes titles
fig.update_yaxes(title_text="Market and target price ($)", secondary_y=False)
fig.update_yaxes(title_text="ETH price ($)", secondary_y=True)

fig.update_layout(
    autosize=False,
    width=1000,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
)

fig.show()

# %%
# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])
# Add traces
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['target_price'], name="Redemption Price"),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['market_price_twap'], name="Market Price TWAP"),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['target_rate'], name="Redemption Rate"),
    secondary_y=True,
)
# Add figure title
fig.update_layout(
    title_text="Market Price, Redemption Price and Redemption Rate"
)
# Set x-axis title
fig.update_xaxes(title_text="Date")
# Set y-axes titles
fig.update_yaxes(title_text="Price (USD)", secondary_y=False)
fig.update_yaxes(title_text="Redemption Rate (1n = 1e-9)", secondary_y=True)

fig.update_layout(
    autosize=False,
    width=1000,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
)

fig.show()

# %%
df.plot(x='timestamp', y=['market_price', 'expected_market_price'], title='Expected Market Price')

# %%
