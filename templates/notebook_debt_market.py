# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Debt Market Model
# 
# ## **Out of date.** See `simulations/` directory for specific simulation notebooks and results analysis notebooks.
# %% [markdown]
# $$
# \Delta{t} = t_{k+1} - t_{k}\\
# {Q}_{k+1} = {Q}_k + v_1 - v_2 - v_3\\
# {D_1}_{k+1} = {D_1}_k + u_1 - u_2 - u_3\\
# w_3 = u_3 \cdot \frac{w_2}{u_2}\\
# w_1 = [(1+\beta_k)^{\Delta{t}}-1]({D_1}_k+{D_2}_k)\\
# {D_2}_{k+1} = {D_2}_k + w_1 - w_2 - w_3\\
# {R}_{k+1} = {R}_k + w_2\\
# $$
# %% [markdown]
# <center>
# <img src="./diagrams/debt_dynamics.png"
#      alt="Debt dynamics"
#      style="width: 60%" />
# </center>
# 
# <center>
# <img src="./diagrams/apt_model.png"
#      alt="APT model"
#      style="width: 60%" />
# </center>
# %% [markdown]
# ## First phase
# * Debt market state -> ETH price changes (exogenous) -> exogenous u,v -> endogenous w -> mutates system state
# 
# ## Second phase
# * APT model, arbitragers act -> u,v activity (to remove diversifiable risk) -> results in change to both debt market and secondary market -> stability controller updates redemption rate and price
# %% [markdown]
# ## Current Model
# 
# 1. Historically driven ETH price, locks, and draws (eventually to be driven by APT model)
# 2. Endogenous liquidation and closing of CDPs
# 3. Debt market state
# %% [markdown]
# # Notes
# %% [markdown]
# ## Resources
# * https://github.com/BlockScience/reflexer/blob/next-steps/next_steps.MD
# * https://community-development.makerdao.com/en/learn/vaults/liquidation/
# %% [markdown]
# * Close CDPs along debt age distribution around 3 months
# * How many CDPs are opened daily?
# * How are CDPs closed?
# * Assumption: opened vs. topped up CDP e.g. ETH price drops, v1 + u1 increase
#   * Rate of change of ETH price, make better assumption about new CDP vs top up
#   * Break down daily v1/u1 data into multiple CDPs/top ups based on assumption
#   * Extreme events -> indicates top up of existing CDP (one that's fallen below certain liquidation ratio)
#   
# * Large to small CDP liquidation: 50/50 - 2000/1000 at start of 2019
# * 1000 to 2000 active CDPs
# * 300% average collat ratio
# 
# See [Maker network report](https://www.placeholder.vc/blog/2019/3/1/maker-network-report)
# 
# > Towards the end of 2018,collateralization   spiked   to   nearly   400%, perhaps  due  to  heightened  risk-aversion  on the  part  of  CDP  holders,but  has  recently declined  back  to  ~270%,  slightly  under  the system’s average of ~300%.
# 
# > As  shown  in  Figure  2A, the average non-empty  CDP  declined  from  above $60Kdaiin  debtat  the  start  of  2018  to  just  over $30Kat  the  start  of  2019.Meanwhile,  the medianCDPby debtgrew from under $500in  debtat  the  start  of  the  year,  reaching around $4Kin   August,before   declining sharply to around$500by early February.
# 
# > The  significant delta between  mean and  mediandebts highlights thepower  law distribution acrossCDPs. While small CDPs dominate  by number—with  over  80%  of CDPsdrawingless  than $10K  of  dai—they representjust  over 3%  oftotal debt  in  the system.  On  the  other  end  of  the  spectrum, about 90CDPs (less  than  4%by  number) individually have  more  than $100Kin  dai outstanding,  representing nearly  84%  of  all debt  in  the  system.
# 
# > Such concentrationin     debtcan     be problematicfor dai supply.For example, four of the six periodsof dai contractiondiscussed in the previous section were associated with CDPs that  had  over$500K  in  debtbeing liquidated. For  example,  CDP  614 hadover 4.3  million in  debt at  liquidation  on  March 18th, accountingfor much of the contraction in outstanding     dai at     the     time. More dramatically,  the  liquidation  of CDPs  3228 and   3164,on   November   20thand   25threspectively,amounted  to  a  contraction  of over $10.7M in dai, making these two CDPs the primary culprits of thelargest contraction in   daisupplyof2018(i.e.   mid-to-late November as showninFigure 1B).


# %%
%pip show cadCAD


# %%
from shared import *


# %%
import numpy as np
import datetime as dt
import pandas as pd

import plotly.io as pio
pio.renderers.default = "png"

# %% [markdown]
# # Historic MakerDAO Dai debt market activity

# %%
debt_market_df = pd.read_csv('models/market_model/data/debt_market_df.csv', index_col='date', parse_dates=True)
debt_market_df


# %%
debt_market_df.insert(0, 'seconds_passed', 24 * 3600)
debt_market_df['cumulative_v_1'] = debt_market_df['v_1'].cumsum()

# %%
debt_market_df.plot()

# %% [markdown]
# # APT Model Setup

# %%
features = ['beta', 'Q', 'v_1', 'v_2 + v_3', 
                    'D_1', 'u_1', 'u_2', 'u_3', 'u_2 + u_3', 
                    'D_2', 'w_1', 'w_2', 'w_3', 'w_2 + w_3',
                    'D']

features_ml = ['beta', 'Q', 'v_1', 'v_2 + v_3', 'u_1', 'u_2', 'u_3', 'w_1', 'w_2', 'w_3', 'D']
optvars = ['u_1', 'u_2', 'v_1', 'v_2 + v_3']

# start_date = '2018-11-05' # Dropping ETH price
# start_date = '2018-05-06' # Dropping ETH price
start_date = '2018-04-01' # Rising ETH price

historical_initial_state = {k: debt_market_df.loc[start_date][k] for k in features}
historical_initial_state

# %% [markdown]
# ## Root function

# %%
import pickle

model = pickle.load(open('models/pickles/apt_debt_model_2020-11-28.pickle', 'rb'))

# ML debt model root function
def G(x, to_opt, data, constant):
    for i,y in enumerate(x):
        data[:,to_opt[i]] = y
    err = model.predict(data)[0] - constant
    return err

dpres = pickle.load(open('models/pickles/debt_market_OLS_model.pickle', 'rb'))

def G_OLS(x, to_opt, data, constant):
    for i,y in enumerate(x):
        data[:,to_opt[i]] = y
    err = dpres.predict(data)[0] - constant
    #print(f'G_OLS err: {err}')
    return err

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
        #print(x)
        data[:,to_opt[i]] = y
    err = model.predict(data)[0] - constant
    curr_error = abs(err)

    # df: pd.DataFrame = pd.read_pickle('exports/ml_data.pickle')
    # ml_data = pd.DataFrame([{'x': x, 'to_opt': to_opt, 'data': data, 'constant': constant, 'err': err}])
    # ml_data['timestep'] = timestep
    # try:
    #     ml_data['iteration'] = df.iloc[-1]['iteration'] + 1
    # except IndexError:
    #     ml_data['iteration'] = 0
    # df.append(ml_data, ignore_index=True).to_pickle('exports/ml_data.pickle')

    #print(err)
    return curr_error

# %% [markdown]
# # Model Configuration

# %%
eth_price = pd.DataFrame(debt_market_df['rho_star'])
eth_p_mean = np.mean(eth_price.to_numpy().flatten())

mar_price = pd.DataFrame(debt_market_df['p'])
mar_p_mean = np.mean(mar_price.to_numpy().flatten())

eth_returns = ((eth_price - eth_price.shift(1))/eth_price.shift(1)).to_numpy().flatten()
eth_gross_returns = (eth_price / eth_price.shift(1)).to_numpy().flatten()

eth_returns_mean = np.mean(eth_returns[1:])

eth_p_mean, eth_returns_mean, mar_p_mean


# %%
eth_price_ = eth_price.loc[start_date][0]

liquidation_ratio = 1.5 # 150%
liquidation_buffer = 2.0
target_price = 1.0

# %%
stability_fee = (historical_initial_state['beta'] * 30 / 365) / (30 * 24 * 3600)


# %%
partial_results = pd.DataFrame()
partial_results_file = f'''{simulation_directory}/results/{simulation_id}/partial_results.pickle'''
partial_results.to_pickle(partial_results_file)

ml_data = pd.DataFrame()
ml_data_file = f'''{simulation_directory}/results/{simulation_id}/ml_data.pickle'''
ml_data.to_pickle(ml_data_file)

# %%
import math

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

assert math.isclose(eth_collateral, eth_locked - eth_freed - eth_bitten, abs_tol=1e-6)

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

assert math.isclose(principal_debt, rai_drawn - rai_wiped - rai_bitten, abs_tol=1e-6)

print(f'Collateralization ratio: {eth_collateral * eth_price_ / principal_debt * target_price}')

# %%
# At historical start date:
median_cdp_collateral = 2500 # dollars
mean_cdp_collateral = 50 # dollars
genesis_cdp_count = int(eth_collateral / mean_cdp_collateral)
genesis_cdp_count


# %%
# Create a set of "genesis" CDPs

cdp_list = []
for i in range(genesis_cdp_count):
    cdp_list.append({
        'open': 1, # True/False == 1/0 for integer/float series
        'time': 0,
        'locked': eth_collateral / genesis_cdp_count,
        'drawn': principal_debt / genesis_cdp_count,
        'wiped': 0.0,
        'freed': 0.0,
        'w_wiped': 0.0,
        'v_bitten': 0.0,
        'u_bitten': 0.0,
        'w_bitten': 0.0,
        'dripped': 0.0
    })

cdps = pd.DataFrame(cdp_list)
cdps

# %%
market_price = debt_market_df.loc[start_date]['p']
market_price

# %%
initial_state = {
    'events': [],
    'cdps': cdps,
    'cdp_metrics': {},
    # Start time
    'timestamp': dt.datetime.strptime(start_date, '%Y-%m-%d'), # datetime
    # Loaded from exogenous parameter
    'eth_price': eth_price_, # dollars
    # v
    'eth_collateral': eth_collateral, # Q
    'eth_locked': eth_locked, # v1
    'eth_freed': eth_freed, # v2
    'eth_bitten': eth_bitten, # v3
    'v_1': historical_initial_state['v_1'],
    'v_2': historical_initial_state['v_2 + v_3'] / 2,
    'v_3': historical_initial_state['v_2 + v_3'] / 2,
    # u
    'principal_debt': principal_debt, # D1
    'rai_drawn': rai_drawn, # u1 "minted"
    'rai_wiped': rai_wiped, # u2
    'rai_bitten': rai_bitten, # u3
    'u_1': historical_initial_state['u_1'],
    'u_2': historical_initial_state['u_2'],
    'u_3': historical_initial_state['u_3'],
    # w
    'w_1': historical_initial_state['w_1'],
    'w_2': historical_initial_state['w_2'],
    'w_3': historical_initial_state['w_3'],
    'accrued_interest': historical_initial_state['D_2'],
    'stability_fee': stability_fee,
    'market_price': market_price,
    'target_price': target_price, # dollars == redemption price
    'target_rate': 0 / (30 * 24 * 3600), # per second interest rate (X% per month)
    'p_expected': target_price,
    'p_debt_expected': target_price,
}

initial_state.update(historical_initial_state)

# Set dataframe to start from start date
debt_market_df = debt_market_df.loc[start_date:]

from .tests.apt_tests import apt_tests
enable_apt_tests = False

parameters = {
    'debug': [True], # Print debug messages (see APT model)
    'raise_on_assert': [False], # See assert_log() in utils.py
    'test': apt_tests if enable_apt_tests else [
        {
            'enable': False
        },
    ],
    'free_memory_states': [['cdps', 'events']], #'cdps',
    #'eth_market_std': [1],
    #'random_state': [np.random.RandomState(seed=0)],
    'new_cdp_proportion': [0.5],
    'new_cdp_collateral': [median_cdp_collateral],
    'liquidation_ratio': [liquidation_ratio], # %
    'liquidation_buffer': [liquidation_buffer], # multiplier applied to CDP collateral by users
    'stability_fee': [lambda timestep, df=debt_market_df: stability_fee], # df.iloc[timestep].beta / (365 * 24 * 3600), # per second interest rate (1.5% per month)
    'liquidation_penalty': [0], # 0.13 == 13%
    'cdp_top_up_buffer': [2],
    # Average CDP duration == 3 months: https://www.placeholder.vc/blog/2019/3/1/maker-network-report
    # The tuning of this parameter is probably off the average, because we don't have the CDP size distribution matched yet,
    # so although the individual CDPs could have an average debt age of 3 months, the larger CDPs likely had a longer debt age.
    'average_debt_age': [3 * (30 * 24 * 3600)], # delta t (seconds)
    'eth_price': [lambda timestep, df=debt_market_df: df.iloc[timestep].rho_star],
    #'v_1': [lambda state, _state_history, df=debt_market_df: df.iloc[state['timestep']].v_1], # Driven by historical data
    #'u_1': [lambda timestep, df=debt_market_df: df.iloc[timestep].u_1], # Driven by historical data
    'seconds_passed': [lambda timestep, df=debt_market_df: df.iloc[timestep].seconds_passed],
    # 'market_price': [lambda timestep, df=debt_market_df: target_price],
    # APT model
    # **{
    #     'use_APT_ML_model': [False],
    #     'root_function': [G_OLS], # glf, G, G_OLS
    #     'features': [features], # features_ml, features
    # },
    **{
        'use_APT_ML_model': [True],
        'root_function': [glf], # glf, G, G_OLS
        'callback': [glf_continue_callback], # glf callback
        'model': [model],
        'features': [features_ml], # features_ml, features
    },
    'freeze_feature_vector': [False], # Use the same initial state as the feature vector for each timestep
    'optvars': [optvars],
    'bounds': [[(xmin,debt_market_df[optvars].max()[i]) 
        for i,xmin in enumerate(debt_market_df[optvars].min())
    ]],
    'interest_rate': [1.0],
    'eth_p_mean': [eth_p_mean],
    'eth_returns_mean': [eth_returns_mean],
    'mar_p_mean': [mar_p_mean],
    # APT OLS model
    'alpha_0': [0],
    'alpha_1': [1],
    'beta_0': [1.0003953223600617],
    'beta_1': [0.6756295152422528],
    'beta_2': [3.86810578185312e-06],    
    # Controller
    'controller_enabled': [True],
    'kp': [-1.5e-6], #5e-7 #proportional term for the stability controller: units 1/USD
    'ki': [lambda control_period=3600: parameter_ki / control_period], #-1e-7 #integral term for the stability controller: units 1/(USD*seconds)
    'partial_results': [partial_results_file],
}

# Override system parameters with `execute.py` execution parameters
parameters.update(execution_parameters)

# parameters = parameters.update({
#     'delta_v1': [lambda state, state_history: delta_v1(state, state_history)],
#     'market_price': [lambda timestep, df=debt_market_df: df.iloc[timestep].p]
# })

# %% [markdown]
# # Simulation Execution

# %%
# Load from execution parameter
SIMULATION_TIMESTEPS = len(debt_market_df) - 1 # approx. 600
MONTE_CARLO_RUNS = 1

# %%
from models.config_wrapper import ConfigWrapper
import models.system_model_v2 as system_model_v2

system_simulation = ConfigWrapper(system_model_v2, T=range(SIMULATION_TIMESTEPS), M=parameters, initial_state=initial_state)


# %%
from cadCAD import configs
del configs[:]

system_simulation.append()

(simulation_result, tensor_field, sessions) = run(drop_midsteps=False)

# %%
partial_results: pd.DataFrame = pd.read_pickle(partial_results_file)
partial_results

# %%
# ml_data: pd.DataFrame = pd.read_pickle(ml_data_file)
# ml_data


# %%

# # ml_data.query('timestep == 1').plot(x='iteration', y='err_abs')

# import plotly.express as px
# ml_data: pd.DataFrame = pd.read_pickle(ml_data_file)
# ml_data['err_abs'] = ml_data.err.abs()
# ml_data = ml_data.query('timestep == 1')
# fig = px.line(ml_data, x="iteration", y="err_abs", facet_col="timestep", facet_col_wrap=2, log_y=True)
# fig.update_yaxes(matches=None)
# fig.update_xaxes(matches=None)
# fig.show()


# %%
# Print system events e.g. liquidation assertion errors
simulation_result[simulation_result.events.astype(bool)].events.apply(lambda x: x[0])

# %% [markdown]
# # Simulation Analysis

# %%
#simulation_result = pd.concat([simulation_result, debt_market_df.reset_index()], axis=1)

simulation_result = simulation_result.assign(eth_collateral_value = simulation_result.eth_collateral * simulation_result.eth_price)

simulation_result['collateralization_ratio'] = (simulation_result.eth_collateral * simulation_result.eth_price) / (simulation_result.principal_debt * simulation_result.target_price)
#simulation_result['historical_collateralization_ratio'] = (simulation_result.Q * simulation_result.rho_star) / (simulation_result.D_1 * simulation_result.p)

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 50)

simulation_result

# %% [markdown]
# ## Save simulation

# %%
# simulation_result.to_pickle(f'{simulation_directory}/results/{simulation_id}/results.pickle')

# %% [markdown]
# # Simulation Analysis

# %%
simulation_result = pd.read_pickle(f'{simulation_directory}/results/{simulation_id}/results.pickle')
# simulation_result = pd.read_csv(f'{simulation_directory}/results/{simulation_id}/results.csv')
max_substep = max(simulation_result.substep)
is_droppable = (simulation_result.substep != max_substep)
is_droppable &= (simulation_result.substep != 0)
simulation_result = simulation_result.loc[~is_droppable]
simulation_result

# %% [markdown]
# ## Select simulation

# %%
df = simulation_result.query('simulation == 0 and subset == 0')


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
import ast

def transform_optimal_values(v):
    try:
        return ast.literal_eval(v)
    except:
        return {}

df['optimal_values'] = df['optimal_values'].map(lambda v: transform_optimal_values(v))


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

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
plt.plot(std_mkt)


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

import plotly.express as px

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
