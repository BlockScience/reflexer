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
# # Debt Market Model - Overview
#
# The purpose of this notebook is to configure and simulate the full CDP and APT system model, using the historical Ethereum price as a driver, under different PI controller settings - enabled, disabled, `kp` and `ki`.
#
# ## Simulation
#
# The model is run using 100 timesteps, without any monte carlo runs. The model runs in the follow steps:
#
# 1. Calculate the amount of time passed between events
# 2. Resolve expected price and store in state
# 3. Calculate APT model optimal values and cdp position state
# 4. Compute and store the error terms
# 5. Exogenous u,v activity: liquidate CDPs
# 6. Endogenous w activity of accrued interested and cdps interest
# 7. Compute the stability control action target rate
# 8. Update the target price based on stability control action 
# 9. Rebalance CDPs using wipes and frees 
# 10. Resolve expected price and store in state
# 11. Aggregate states
# 12. Update debt market state
# 13. Exogenous ETH price process
#
#
# Please visit the [Glossary](./GLOSSARY.md) for specific term and component definitions.
# %%
# %pip show scikit-optimize

# %%
# #!pip install scikit-optimize

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

# %% [markdown]
# # Historical MakerDAO Dai debt market activity

# %%
# Import the historical MakerDAO market data CSV file
from models.system_model_v2.model.state_variables.historical_state import debt_market_df
debt_market_df.head(2)


# %%
debt_market_df.tail(2)

# %%
# Plot the full set of historical data over time
debt_market_df.plot()

# %% [markdown]
# # Model Configuration

# %%
from models.system_model_v2.model.state_variables.init import state_variables

state_variables.update({})

# %%
from models.system_model_v2.model.params.init import params

# Update the default parameter values
params_update = {
    'controller_enabled': [True],
    'kp': [5e-7], # proportional term for the stability controller: units 1/USD
    'ki': [lambda control_period=3600: -1e-7 / control_period], # integral term for the stability controller: units 1/(USD*seconds)
}

params.update(params_update)

# %% [markdown]
# # Simulation Execution

# %%
# Set the number of simulation timesteps, with a maximum of `len(debt_market_df) - 1`
SIMULATION_TIMESTEPS = 10 # len(debt_market_df) - 1

# %%
# Create a wrapper for the model simulation, and update the existing parameters and initial state
system_simulation = ConfigWrapper(system_model_v2, T=range(SIMULATION_TIMESTEPS), M=params, initial_state=state_variables)


# %%
del configs[:] # Clear any prior configs
system_simulation.append() # Append the simulation config to the cadCAD `configs` list
(simulation_result, _tensor_field, _sessions) = run(drop_midsteps=False) # Run the simulation

# %% [markdown]
# # Simulation Analysis

# %%
# Add new columns to dataframe
simulation_result = simulation_result.assign(eth_collateral_value = simulation_result.eth_collateral * simulation_result.eth_price)
simulation_result['collateralization_ratio'] = (simulation_result.eth_collateral * simulation_result.eth_price) / (simulation_result.principal_debt * simulation_result.target_price)

# Update dataframe display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)

simulation_result.head(5)

# %% [markdown]
# ## Save simulation

# %%
# Save the simulation result to a pickle file, for backup - this will be overwritten on the next simulation
simulation_result.to_pickle(f'./exports/system_model_v2/results.pickle')

# %% [markdown]
# # Simulation Analysis

# %%
# Load the simulation result from a pickle file, specifying past results when necessary
simulation_result = pd.read_pickle(f'exports/system_model_v2/results.pickle')

# Drop the simulation midsteps - the substeps that aren't used for generating plots
df = drop_dataframe_midsteps(simulation_result)
df.head(5)

# %% [markdown]
# ## Select simulation

# %%
# Select the first simulation and subset, this is only relevant when running parameter sweeps or Monte Carlo Runs
# The following plots are configured for single simulation results
df = df.query('simulation == 0 and subset == 0')


# %%
df.plot(x='timestamp', y=['eth_price'], title='Historical ETH price')


# %%
df.plot(x='timestamp', y=['eth_return'], title='Historical ETH return')


# %%
df.plot(x='timestamp', y=['target_price', 'market_price'], title='Target Price vs. Market Price')


# %%
df.plot(x='timestamp', y=['expected_market_price', 'expected_debt_price'], title='Expected Market Price and Debt Price')


# %%
df.plot(x='timestamp', y=['target_rate'], title='Controller Target Rate')


# %%
df['locked - freed - bitten'] = df['eth_locked'] - df['eth_freed'] - df['eth_bitten']
df.plot(y=['eth_collateral', 'locked - freed - bitten'], title='Debt Market Locked ETH Collateral')


# %%
df.plot(x='timestamp', y=['eth_collateral_value'], title='Debt Market Locked ETH Collateral Value ($)')


# %%
df.plot(x='timestamp', y=['eth_locked', 'eth_freed', 'eth_bitten'], title='Debt Market ETH State')


# %%
df.plot(x='timestamp', y=['v_1', 'v_2', 'v_3'], title='Debt Market ETH Lock, Free, Bite Activity')

# %%
df['apt_v_1'] = df['optimal_values'].map(lambda v: v.get('v_1', 0))
df['apt_v_2'] = df['optimal_values'].map(lambda v: v.get('v_2 + v_3', 0))

df.plot(x='timestamp', y=['apt_v_1', 'apt_v_2'], title='Debt Market ETH APT Lock, Free Activity')


# %%
df['drawn - wiped - bitten'] = df['rai_drawn'] - df['rai_wiped'] - df['rai_bitten']
df.plot(x='timestamp', y=['principal_debt', 'drawn - wiped - bitten'], title='Debt Market RAI State')


# %%
df.plot(x='timestamp', y=['rai_drawn', 'rai_wiped', 'rai_bitten'], title='Debt Market RAI State')


# %%
df.plot(x='timestamp', y=['u_1', 'u_2', 'u_3'], title='Debt Market RAI Draw, Wipe, Bite Activity')


# %%
df['sum_apt_u_1'] = df['optimal_values'].map(lambda v: v.get('u_1', 0))
df['sum_apt_u_2'] = df['optimal_values'].map(lambda v: v.get('u_2', 0))

df.plot(x='timestamp', y=['sum_apt_u_1', 'sum_apt_u_2'], title='Debt Market RAI APT Lock, Free Activity')

# %%
df['diff_u_1_u_2'] = df['sum_apt_u_1'] - df['sum_apt_u_2']
df['diff_u_1_u_2'] = df['diff_u_1_u_2'].cumsum()

df.plot(x='timestamp', y=['diff_u_1_u_2'])

# %% [markdown]
# ## Accrued interest and system revenue

# %%
df.plot(x='timestamp', y=['w_1', 'w_2', 'w_3'], title='Accrued Interest Activity')


# %%
df.plot(x='timestamp', y=['accrued_interest'], title='Accrued Interest')


# %%
df.plot(x='timestamp', y=['system_revenue'], title='System Revenue')


# %%
df.plot(x='timestamp', y=['collateralization_ratio'], title='Collateralization Ratio')


# %%
# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['target_price'], name="Target price"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['market_price'], name="Market price"),
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
    height=800,
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
    go.Scatter(x=df['timestamp'], y=df['market_price'], name="Market Price"),
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
    height=800,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
)

fig.show()

# %% [markdown]
# ## Simulation statistics

# %%
std_mkt = df['market_price'].rolling(7).std()
std_mkt.plot()


# %%
np.std(df['market_price'])


# %%
err_m_t = df['market_price'] - df['target_price']
err_m_t.plot()


# %%
np.sqrt(abs(df['market_price'] - df['target_price']).mean())


# %%
np.corrcoef(df['market_price'],df['eth_price'])


# %%
np.corrcoef(df['market_price'],df['target_price'])


# %%
np.corrcoef(df['market_price'],df['target_rate'])


# %%
df['market_price_rolling'] = df['market_price'].rolling(7).std()
fig = px.histogram(df, x="market_price_rolling", nbins=25)

fig.update_layout(
    title="7-Day Rolling Standard Deviation Histogram, Market Price (Controller On)",
    xaxis_title="Standard Deviation",
    yaxis_title="Frequency",
)

fig.show()

# %% [markdown]
# ## Conclusion
# This current working notebook is an integration test. In contrast to the v1 model, the stabilizing effect of a positive Kp and negative Ki term combined. Towards the end of the notebook we wanted to test whether the controller was reducing volatility, but the plots we chose didn't give any strong conclusions yet.
#
