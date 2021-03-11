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
# # Setup and Dependencies

# %%
# Set project root folder, to enable importing project files from subdirectories
from typing import List, Dict
from time import time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from pathlib import Path
import os
from typing import NamedTuple

path = Path().resolve()
root_path = str(path).split("notebooks")[0]
os.chdir(root_path)

from shared import *

# Force reload of project modules, sometimes necessary for Jupyter kernel
# %load_ext autoreload
# %autoreload 2

# Display cadCAD version for easy debugging
# %pip show cadCAD

# %%
# Import all shared dependencies and setup


# import plotly.io as pio
# pio.renderers.default = "png"


# %%


def simulate(sim_ts_list: List[int],
             state_vars_update: dict = {},
             params_update: dict= {}) -> Dict[int, float]:
    exec_time = {}
    for sim_ts in sim_ts_list:
        t1 = time()
        from models.system_model_v3.model.state_variables.init import state_variables
        from models.system_model_v3.model.params.init import params

        state_variables.update(state_vars_update)
        params.update(params_update)

        system_simulation = ConfigWrapper(
            system_model_v3, T=range(sim_ts), M=params, initial_state=state_variables,
        )
        del configs[:]
        run(system_simulation, drop_midsteps=False)
        t2 = time()
        exec_time[sim_ts] = t2 - t1
    return exec_time


sim_ts_list = [125, 250, 500]


class FakeUniswapOracle(NamedTuple):
    update_result: callable
    median_price: float


fake_oracle = FakeUniswapOracle(lambda x: None, 2.0)
update = {"uniswap_oracle": fake_oracle}

update_params = {'constant_uniswap_price': [True]}

fake_oracle_times = simulate(sim_ts_list, update)
constant_times = simulate(sim_ts_list, params_update=update_params)
oracle_times = simulate(sim_ts_list)

# %%

def f(time_dict, kv: dict):
    s = pd.Series(time_dict)
    s.index.name = "timesteps"
    s.name = "execution_time"
    df = s.reset_index().assign(**kv)
    return df



df_1 = f(oracle_times, {"oracle": 'yes'})
df_2 = f(fake_oracle_times, {"oracle": 'fake'})
df_2 = f(constant_times, {"oracle": 'constant'})
df = pd.concat([df_1, df_2])
fig = px.scatter(df,
                 x="timesteps",
                 y="execution_time",
                 color="oracle",
                 log_x=True,
                 log_y=True,
                 trendline='ols')
fig.show()
# %%
