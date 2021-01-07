# %% [markdown]
# # RAI System Model v2
# %% [markdown]
# # Parameters
# %% tags=["parameters"]

# %% [markdown]
# # Imports

# %%
# To re-generate notebook, set root directory if necessary
# %cd ~/workspace/reflexer
from shared import *


# %%
import numpy as np
import datetime as dt
import pandas as pd

import plotly.io as pio
pio.renderers.default = "png"

# %% [markdown]
# # Historical MakerDAO Dai debt market activity

# %%
debt_market_df = pd.read_csv('models/market_model/data/debt_market_df.csv', index_col='date', parse_dates=True)
debt_market_df


# %%
debt_market_df.insert(0, 'seconds_passed', 24 * 3600)


# %%
debt_market_df.plot()

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
