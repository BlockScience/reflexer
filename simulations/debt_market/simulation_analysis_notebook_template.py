# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Debt Market Model
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

# %% [markdown]
# # Parameters

# %% tags=["parameters"]

# %% [markdown]
# # Imports

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
debt_market_df = pd.read_csv('market_model/data/debt_market_df.csv', index_col='date', parse_dates=True)
debt_market_df


# %%
debt_market_df.insert(0, 'seconds_passed', 24 * 3600)
debt_market_df['cumulative_v_1'] = debt_market_df['v_1'].cumsum()


# %%
debt_market_df.plot()

# %% [markdown]
# # Simulation Analysis

# %%
simulation_result = pd.read_pickle(f'{simulation_directory}/results/{simulation_id}/results.pickle')
simulation_result

# %% [markdown]
# ## Select simulation

# %%
df = simulation_result.query('simulation == 0 and subset == 0')

# %% [markdown]
# ## Historical ETH price: December 2017 to September 2019

# %%
df.plot(x='timestamp', y=['eth_price'])


# %%
df.plot(x='timestamp', y=['eth_return'])

# %% [markdown]
# ## Target price / redemption price set to 1 "dollar" for historical comparison

# %%
df.plot(x='timestamp', y=['target_price', 'market_price'])


# %%
df.plot(x='timestamp', y=['p_expected', 'p_debt_expected'])


# %%
df.plot(x='timestamp', y=['target_rate'])

# %% [markdown]
# ## Historical system ETH collateral vs. model

# %%
df['locked - freed - bitten'] = df['eth_locked'] - df['eth_freed'] - df['eth_bitten']
df.plot(y=['eth_collateral', 'locked - freed - bitten']) #'Q'

# %% [markdown]
# ## Historical system ETH collateral value vs. model

# %%
df.plot(x='timestamp', y=['eth_collateral_value']) #'C_star'

# %% [markdown]
# ## Debt market ETH activity

# %%
df.plot(x='timestamp', y=['eth_locked', 'eth_freed', 'eth_bitten'])


# %%
df.plot(x='timestamp', y=['v_1', 'v_2', 'v_3'])

# %% [markdown]
# ## Debt market principal debt "Rai" activity

# %%
df['drawn - wiped - bitten'] = df['rai_drawn'] - df['rai_wiped'] - df['rai_bitten']
df.plot(x='timestamp', y=['principal_debt', 'drawn - wiped - bitten']) #, 'D_1'


# %%
df.plot(x='timestamp', y=['rai_drawn', 'rai_wiped', 'rai_bitten'])


# %%
df.plot(x='timestamp', y=['u_1', 'u_2', 'u_3'])

# %% [markdown]
# ## Accrued interest and system revenue (MKR)

# %%
df.plot(x='timestamp', y=['w_1', 'w_2', 'w_3'])


# %%
df.plot(x='timestamp', y=['accrued_interest']) #, 'D_2'


# %%
df.plot(x='timestamp', y=['system_revenue'])

# %% [markdown]
# ## Historical collateralization ratio vs. model

# %%
df.plot(x='timestamp', y=['collateralization_ratio']) #, 'historical_collateralization_ratio'

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
