# ./app/ETL.py

def ETL_transform(hour_data, df_labels):
    """
    """
    import pandas as pd

    # remove 'btc_hour_price_close' column from df_labels to avoid repeat columns on join
    df_labels = df_labels.drop(['btc_hour_price_close'], axis=1)
    
    # sort hour_data by hour datetime column
    hour_data['hour_datetime_id'] = pd.to_datetime(hour_data['hour_datetime_id'])
    hour_data = hour_data.sort_values(by='hour_datetime_id')
    
    # sort df_labels by hour datetime column
    df_labels['hour_datetime_id'] = pd.to_datetime(df_labels['hour_datetime_id'])
    df_labels = df_labels.sort_values(by='hour_datetime_id')
    
    # inner join merge hour_data with df_labels and drop 'daily_id' column
    df = hour_data.merge(df_labels, on='hour_datetime_id', how='inner')
    df.drop(columns=['daily_id'], inplace=True)
    
    return df