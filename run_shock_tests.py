import os
import itertools
import numpy as np

exponents = list(reversed(range(-10, 10, 1)))
kp_sweep = [-6.944e-6 * 10**exp for exp in exponents]
ki_sweep = [-1e-10 * 10**exp for exp in exponents]

controller_sweep = list(itertools.product(kp_sweep, ki_sweep))
controller_sweep

kp_sweep = [x[0] for x in controller_sweep]
ki_sweep = [x[1] for x in controller_sweep]

print(kp_sweep)
print(ki_sweep)

for kp_param, ki_param in zip(kp_sweep, ki_sweep):
    print(f'Running shock tests for parameters: Kp: {kp_param}; Ki: {ki_param}')
    shock_tests_cmd = f'''cat ./templates/shock_tests_nb.py |
    jupytext --from py:percent --to ipynb --set-kernel - |
    papermill - templates/shock_tests.ipynb --log-output -p kp_param {kp_param} -p ki_param {ki_param} --cwd .'''
    os.system(shock_tests_cmd)
