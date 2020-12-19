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
#     display_name: Python 3.8.6 64-bit ('venv')
#     metadata:
#       interpreter:
#         hash: bff42e0006f465fd6c2f40e27aef204df5f2a1176d04ad4566af69187a27d52d
#     name: python3
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

# %%
# Force reload of project modules, sometimes necessary for Jupyter kernel
# %load_ext autoreload
# %autoreload 2

# %%
# Display cadCAD version for easy debugging
# %pip show cadCAD

# %%
# Import all shared dependencies and setup
from shared import *

# %%
# Import notebook specific dependencies
import numpy as np
import datetime as dt
import pandas as pd
import pickle
import math
import ast

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import plotly.io as pio
# pio.renderers.default = "png"

# %% [markdown]
# # Historical MakerDAO Dai debt market activity

# %%
# Import the historical MakerDAO market data CSV file
debt_market_df = pd.read_csv('models/market_model/data/debt_market_df.csv', index_col='date', parse_dates=True)
debt_market_df


# %%
# Create a new column for `seconds_passed`, setting to 1 day in seconds - the sampling period available for historical data
debt_market_df.insert(0, 'seconds_passed', 24 * 3600)

# %%
# Plot the full set of historical data over time
debt_market_df.plot()

# %% [markdown]
# # APT Model Setup

# %%
# The full feature vector available for the APT model
features = ['beta', 'Q', 'v_1', 'v_2 + v_3', 
                    'D_1', 'u_1', 'u_2', 'u_3', 'u_2 + u_3', 
                    'D_2', 'w_1', 'w_2', 'w_3', 'w_2 + w_3',
                    'D']

# The feature vector subset used for the APT ML model
features_ml = ['beta', 'Q', 'v_1', 'v_2 + v_3', 'u_1', 'u_2', 'u_3', 'w_1', 'w_2', 'w_3', 'D']

# The unobservable events, or optimal values, returned from the root-finding algorithm
optvars = ['u_1', 'u_2', 'v_1', 'v_2 + v_3']

# %% [markdown]
# ## Root-finding function
#
# Load the APT model from a Pickle file, and configure the root-finding algorithm to be optimized using Scipy's `minimize` function and Powell's method.

# %%
# NB: Pickle files must be downloaded seperately and copied into `models/pickes/` directory
model = pickle.load(open('models/pickles/apt_debt_model_2020-11-28.pickle', 'rb'))

ml_data_list = []
global tol
tol = 1e-2
global curr_error, best_error, best_val
global strikes
strikes = 0
best_error = 1e10

def glf_continue_callback(xopt):
    print('entered callback')
    global curr_error, best_error, best_val, strikes, tol
    if curr_error > tol: # keep searching
        print('bigger than tol, keep searching')
        return False
    else:
        if curr_error > best_error: # add strike
            strikes += 1
            if strikes < 3: # continue trying
                print('bigger than prev best, add strike')
                return False
            else: # move on, not working
                strikes = 0
                print('3rd strike, stop')
                return True
        else: # better outcome, continue
            best_error = curr_error
            best_val = xopt
            strikes = 0
            print('New best, reset strikes')
            return False

# Global minimizer function
def glf(x, to_opt, data, constant, timestep):
    global curr_error
    for i,y in enumerate(x):
        data[:,to_opt[i]] = y
    err = model.predict(data)[0] - constant
    curr_error = abs(err)

    return curr_error

# %% [markdown]
# # Model Configuration

# %%
# Select the start date from historical data to use as the model initial state

# Select the start date, chosen for a gradually rising ETH price, and reasonable pool of CDP collateral and debt
start_date = '2018-04-01' # Rising ETH price

# Build a feature vector from the historical dataset at the start_date, to be used as the model initial state
historical_initial_state = {k: debt_market_df.loc[start_date][k] for k in features}
historical_initial_state

# %%
# Pre-process the historical data

# Create a dataframe for the ETH price
eth_price_df = pd.DataFrame(debt_market_df['rho_star'])
# Calculate the mean ETH price
eth_price_mean = np.mean(eth_price_df.to_numpy().flatten())

# Create a dataframe for the market price
market_price_df = pd.DataFrame(debt_market_df['p'])
# Calculate the mean market price
market_price_mean = np.mean(market_price_df.to_numpy().flatten())

# Calculate the ETH returns and gross returns, for the equation to find the root of non-arbitrage condition
eth_returns = ((eth_price_df - eth_price_df.shift(1)) / eth_price_df.shift(1)).to_numpy().flatten()
eth_gross_returns = (eth_price_df / eth_price_df.shift(1)).to_numpy().flatten()

# Calculate the mean ETH returns
eth_returns_mean = np.mean(eth_returns[1:])

eth_price_mean, eth_returns_mean, market_price_mean


# %%
# Set the initial ETH price state
eth_price = eth_price_df.loc[start_date][0]
# Set the initial market price state
market_price = debt_market_df.loc[start_date]['p']
# Set the initial target price, in Dollars
target_price = 1.0

# Configure the liquidation ratio parameter
liquidation_ratio = 1.5 # 150%
# Configure the liquidation buffer parameter: the multiplier for the liquidation ratio, that users apply as a buffer
liquidation_buffer = 2.0

# Configure the initial stability fee parameter, as a scaled version of the historical data beta at the start date
stability_fee = (historical_initial_state['beta'] * 30 / 365) / (30 * 24 * 3600)

# %%
# Decompose the debt market collateral initial states
eth_collateral = historical_initial_state['Q']
eth_locked = debt_market_df.loc[:start_date]['v_1'].sum()
eth_freed = debt_market_df.loc[:start_date]['v_2 + v_3'].sum() / 2
eth_bitten = debt_market_df.loc[:start_date]['v_2 + v_3'].sum() / 2

print(f'''
{eth_collateral}
{eth_locked}
{eth_freed}
{eth_bitten}
''')

# Check that the relationships between ETH locked, freed, and bitten are conserved
assert math.isclose(eth_collateral, eth_locked - eth_freed - eth_bitten, abs_tol=1e-6)

# Decompose the debt market principal debt initial states
principal_debt = historical_initial_state['D_1']
rai_drawn = debt_market_df.loc[:start_date]['u_1'].sum()
rai_wiped = debt_market_df.loc[:start_date]['u_2'].sum()
rai_bitten = debt_market_df.loc[:start_date]['u_3'].sum()

print(f'''
{principal_debt}
{rai_drawn}
{rai_wiped}
{rai_bitten}
''')

# Check that the relationships between debt drawn, wiped, and bitten are conserved
assert math.isclose(principal_debt, rai_drawn - rai_wiped - rai_bitten, abs_tol=1e-6)

# Calculate and print the initial collateralization ratio (should be approx. 3)
print(f'Collateralization ratio: {eth_collateral * eth_price / principal_debt * target_price}')

# %%
# Based on CDP collateral statistics, calculate the total number of initial CDPs to be created
median_cdp_collateral = 2500 # dollars
mean_cdp_collateral = 50 # dollars
genesis_cdp_count = int(eth_collateral / mean_cdp_collateral)
genesis_cdp_count


# %%
# Create a pool of initial CDPs
cdp_list = []
for i in range(genesis_cdp_count):
    cdp_list.append({
        'open': 1, # Is the CDP open or closed? True/False == 1/0 for integer/float series
        'time': 0, # How long the CDP has been open for
        # Divide the initial state of ETH collateral and principal debt among the initial CDPs
        'locked': eth_collateral / genesis_cdp_count,
        'drawn': principal_debt / genesis_cdp_count,
        'wiped': 0.0, # Principal debt wiped
        'freed': 0.0, # ETH collateral freed
        'w_wiped': 0.0, # Accrued interest wiped
        'v_bitten': 0.0, # ETH collateral bitten (liquidated)
        'u_bitten': 0.0, # Principal debt bitten
        'w_bitten': 0.0, # Accrued interest bitten
        'dripped': 0.0 # Total interest accrued
    })

cdps = pd.DataFrame(cdp_list)
cdps

# %% [markdown]
# ## Initial State

# %%
initial_state = {
    'cdps': cdps, # A dataframe of CDPs (both open and closed)
    'timestamp': dt.datetime.strptime(start_date, '%Y-%m-%d'), # type: datetime; start time
    
    # Exogenous states
    'eth_price': eth_price, # unit: dollars; updated from historical data as exogenous parameter
    
    # CDP states
    # v - ETH collateral states
    'eth_collateral': eth_collateral, # "Q"; total ETH collateral in the CDP system i.e. locked - freed - bitten
    'eth_locked': eth_locked, # total ETH locked into CDPs; the cumulative sum of "v_1" activity
    'eth_freed': eth_freed, # total ETH freed from CDPs; the cumulative sum of "v_2" activity
    'eth_bitten': eth_bitten, # total ETH bitten/liquidated from CDPs; the cumulative sum of "v_3" activity
    'v_1': historical_initial_state['v_1'], # discrete "lock" event, in ETH
    'v_2': historical_initial_state['v_2 + v_3'] / 2, # discrete "free" event, in ETH
    'v_3': historical_initial_state['v_2 + v_3'] / 2, # discrete "bite" event, in ETH
    
    # u - principal debt states
    'principal_debt': principal_debt, # "D_1"; the total debt in the CDP system i.e. drawn - wiped - bitten
    'rai_drawn': rai_drawn, # total RAI debt minted from CDPs; the cumulative sum of "u_1" activity
    'rai_wiped': rai_wiped, # total RAI debt wiped/burned from CDPs; the cumulative sum of "u_2" activity
    'rai_bitten': rai_bitten, # total RAI liquidated from CDPs; the cumulative sum of "u_3" activity
    'u_1': historical_initial_state['u_1'], # discrete "draw" event, in RAI
    'u_2': historical_initial_state['u_2'], # discrete "wipe" event, in RAI
    'u_3': historical_initial_state['u_3'], # discrete "bite" event, in RAI
    
    # w - accrued interest states
    'accrued_interest': historical_initial_state['D_2'], # "D_2"; the total interest accrued in the system i.e. current D_2 + w_1 - w_2 - w_3
    'w_1': historical_initial_state['w_1'], # discrete "drip" event, in RAI
    'w_2': historical_initial_state['w_2'], # discrete "shut"/"wipe" event, in RAI
    'w_3': historical_initial_state['w_3'], # discrete "bite" event, in RAI
    
    # System states
    'stability_fee': stability_fee, # interest rate used to calculate the accrued interest
    'market_price': market_price, # unit: dollars; the secondary market clearing price
    'target_price': target_price, # unit: dollars; equivalent to redemption price
    'target_rate': 0 / (30 * 24 * 3600), # per second interest rate (X% per month), updated by controller
    
    # APT model states
    'p_expected': target_price, # root of non-arbitrage condition
    'p_debt_expected': target_price, # predicted "debt" price, the intrinsic value of RAI according to the debt market activity and state
}

# Override initial state with historical initial state, for ML model starting condition
initial_state.update(historical_initial_state)

# %% [markdown]
# ## Parameters

# %%
# Set dataframe to start from start date
debt_market_df = debt_market_df.loc[start_date:]

parameters = {
    # CDP parameters
    'new_cdp_collateral': [median_cdp_collateral], # The average CDP collateral for opening a CDP
    'liquidation_buffer': [liquidation_buffer], # multiplier applied to CDP collateral by users
    
    # System parameters
    'stability_fee': [lambda timestep, df=debt_market_df: stability_fee], # per second interest rate (x% per month)
    'liquidation_ratio': [liquidation_ratio], # e.g. 150%
    'liquidation_penalty': [0], # percentage added on top of collateral needed to liquidate CDP
    
    # Exogenous states, loaded as parameter at every timestep - these are lambda functions, and have to be called
    'eth_price': [lambda timestep, df=debt_market_df: df.iloc[timestep].rho_star],
    'seconds_passed': [lambda timestep, df=debt_market_df: df.iloc[timestep].seconds_passed],
    
    # APT model
    'root_function': [glf],
    'callback': [glf_continue_callback],
    'model': [model],
    'features': [features_ml],
    'optvars': [optvars],
    'bounds': [[(xmin,debt_market_df[optvars].max()[i]) 
        for i,xmin in enumerate(debt_market_df[optvars].min())
    ]],
    'eth_price_mean': [eth_price_mean],
    'eth_returns_mean': [eth_returns_mean],
    'market_price_mean': [market_price_mean],

    # Controller parameters
    'controller_enabled': [True],
    'kp': [5e-7], # proportional term for the stability controller: units 1/USD
    'ki': [lambda control_period=3600: -1e-7 / control_period], # integral term for the stability controller: units 1/(USD * seconds)
}

# %% [markdown]
# # Simulation Execution

# %%
# Set the number of simulation timesteps, with a maximum of `len(debt_market_df) - 1`
SIMULATION_TIMESTEPS = 10 # len(debt_market_df) - 1

# %%
# Create a wrapper for the model simulation, and update the existing parameters and initial state
system_simulation = ConfigWrapper(system_model_v2, T=range(SIMULATION_TIMESTEPS), M=parameters, initial_state=initial_state)


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

simulation_result

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
df

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
df.plot(x='timestamp', y=['p_expected', 'p_debt_expected'], title='Expected Market Price and Debt Price')


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
plt.plot(err_m_t)


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

# %%

# std_mkt_without = res_without_controller[‘market_price’].rolling(7).std()
# std_mkt_with = res_with_controller[‘market_price’].rolling(7).std()
# df =pd.DataFrame(dict(
#     series=np.concatenate(([“With Controller”]*len(std_mkt_with), [“Without Controller”]*len(std_mkt_without))),
#     data  =np.concatenate((std_mkt_with,std_mkt_without))
# ))

# fig = df.hist(x=“data”, color=“series”, nbins=25, barmode=“overlay”,
#         labels={
#             ‘count’ : “Count”,
#             ‘data’ : “Std Dev”,
#             ‘series’ : “Simulation”
#         },
#         title=“Histogram, Standard Deviations of Market Price”)
# fig.show()
