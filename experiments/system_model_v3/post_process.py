from radcad.core import generate_parameter_sweep
import pandas as pd


def post_process_results(experiment_result):
    df = pd.DataFrame(experiment_result)
    df = drop_dataframe_midsteps(experiment_result)

    # Add new columns to dataframe
    df.eval('eth_collateral_value = eth_collateral * eth_price', inplace=True)
    df.eval('collateralization_ratio = (eth_collateral * eth_price) / (principal_debt * target_price)', inplace=True)

    # Get parameter sweep
    param_sweep = generate_parameter_sweep(params)
    param_sweep = [{param: subset[param] for param in ('ki', 'kp', 'liquidation_ratio')} for subset in param_sweep]

    # Assign parameters to subsets
    for subset_index in df['subset']:
        for subset in param_sweep:
            for (key, value) in subset.items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value
    
    # Update target price to account for liquidation_ratio
    df.eval('target_price_scaled = target_price * liquidation_ratio', inplace=True)
