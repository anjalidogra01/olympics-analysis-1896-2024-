import pandas as pd
import numpy as np

def preprocess(df, region_df):
    
    # Drop unnecessary columns
    df = df.drop(columns=['player_id', 'Season'])
    
    # Merge region info
    df = df.merge(region_df, on='NOC', how='left')
    
    # Replace "No medal" with NaN
    df['Medal'] = df['Medal'].replace('No medal', np.nan)

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # One-hot encode medals
    medal_dummies = pd.get_dummies(df['Medal'])
    df = pd.concat([df, medal_dummies], axis=1)

    # Ensure columns exist
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in df.columns:
            df[col] = 0

    # Create Total medals column
    df['Total'] = df['Gold'] + df['Silver'] + df['Bronze']

    return df
