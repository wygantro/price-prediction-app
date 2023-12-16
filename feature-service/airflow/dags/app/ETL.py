# ./app/ETL.py

def ETL_transform(hour_data, df_labels):
    """
    This function takes input hour_data and df_labels as dataframes and
    joins price/feature data on datetime labeled index and returns a
    single dataframe

    Args:
        hour_data (logging.Logger): Initialized logger object
        df_labels (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
        pandas.core.frame.DataFrame: labeled price/features dataframe
    """
    import pandas as pd

    # drop price column from labels
    df_labels = df_labels.drop(['btc_hour_price_close'], axis=1)

    # sort both dataframes
    hour_data['hour_datetime_id'] = pd.to_datetime(
        hour_data['hour_datetime_id'])
    hour_data = hour_data.sort_values(by='hour_datetime_id')
    df_labels['hour_datetime_id'] = pd.to_datetime(
        df_labels['hour_datetime_id'])
    df_labels = df_labels.sort_values(by='hour_datetime_id')

    # inner join merge
    df = hour_data.merge(df_labels, on='hour_datetime_id', how='inner')
    df.drop(columns=['daily_id'], inplace=True)

    return df
