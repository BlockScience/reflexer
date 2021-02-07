from radcad.core import generate_parameter_sweep
import pandas as pd
from models.utils.process_results import drop_dataframe_midsteps


def post_process_results(df, params, set_params=['ki', 'kp', 'liquidation_ratio']):
    df = drop_dataframe_midsteps(df)

    # Add new columns to dataframe
    df.eval('eth_collateral_value = eth_collateral * eth_price', inplace=True)
    df.eval('collateralization_ratio = (eth_collateral * eth_price) / (principal_debt * target_price)', inplace=True)

    # Get parameter sweep
    param_sweep = generate_parameter_sweep(params)
    param_sweep = [{param: subset[param] for param in set_params} for subset in param_sweep]

    # Assign parameters to subsets
    for subset_index in df['subset']:
        for (key, value) in param_sweep[subset_index].items():
            df.loc[df.eval(f'subset == {subset_index}'), key] = value
    
    # Update target price to account for liquidation_ratio
    df.eval('target_price_scaled = target_price * liquidation_ratio', inplace=True)

    return df
