from radcad.core import generate_parameter_sweep
import pandas as pd
import time
from models.utils.process_results import drop_dataframe_midsteps


def post_process_results(df, params, set_params=['ki', 'kp', 'liquidation_ratio']):
    start = time.time()
    print("Dropping midsteps")
    df = drop_dataframe_midsteps(df)
    print(time.time() - start)

    # Add new columns to dataframe
    print("Adding new columns")
    df.eval('eth_collateral_value = eth_collateral * eth_price', inplace=True)
    df.eval('collateralization_ratio = (eth_collateral * eth_price) / (principal_debt * target_price)', inplace=True)
    print(time.time() - start)

    # Get parameter sweep
    print("Getting parameter sweep")
    param_sweep = generate_parameter_sweep(params)
    param_sweep = [{param: subset[param] for param in set_params} for subset in param_sweep]
    print(time.time() - start)

    # Assign parameters to subsets
    print("Assigning parameters to subsets")
    for subset_index in df['subset'].unique():
        for (key, value) in param_sweep[subset_index].items():
            df.loc[df.eval(f'subset == {subset_index}'), key] = value
    print(time.time() - start)
    
    # Update target price to account for liquidation_ratio
    print("Creating target_price_scaled")
    df.eval('target_price_scaled = target_price * liquidation_ratio', inplace=True)
    print(time.time() - start)

    return df
