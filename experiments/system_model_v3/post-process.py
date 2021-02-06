import pandas as pd


simulation_result = None


df = pd.DataFrame(simulation_result)
df = drop_dataframe_midsteps(simulation_result)

# Add new columns to dataframe
df = df.assign(eth_collateral_value = df.eth_collateral * df.eth_price)
df['collateralization_ratio'] = (df.eth_collateral * df.eth_price) / (df.principal_debt * df.target_price)

liquidation_ratio = 1.5
df['target_price'] = df['target_price'] * liquidation_ratio
