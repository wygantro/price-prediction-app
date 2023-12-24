# ./app/query.py

def current_datetime():
    """
    Output current datetime object for daily, hourly and minute timeframe.

    This function returns three standardized datetime objects to be 
    utilized as database unique value IDs for API timeseries data.

    Args: None

    Returns:
            datetime.datetime: Current datetime (year, month, day) object
            datetime.datetime: Current datetime (year, month, day, hour) object
            datetime.datetime: Current datetime (year, month, day, hour,
            minute) object
    """
    import datetime
    import pytz

    # define daily, hour and minute datetime
    utc = pytz.UTC
    now = datetime.datetime.now(utc)
    daily_datetime_id = datetime.datetime(
        year=now.year, month=now.month, day=now.day)
    hour_datetime_id = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour)
    minute_datetime_id = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute)

    return daily_datetime_id, hour_datetime_id, minute_datetime_id


def get_full_feature_dataframe(logger, session):
    """
    Connects with database, queries datetime range data for daily, hourly
    and minute tables and returns a full dataframe.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
         pandas.core.frame.DataFrame: price/features dataframe
    """
    import pandas as pd
    from app.feature_service_models import Daily_price_data, Daily_feature_data, Hour_price_data

    # query all minute, hour and daily data and join to dataframe
    query = session.query(Hour_price_data, Daily_price_data, Daily_feature_data)\
        .join(Daily_price_data, Hour_price_data.daily_id == Daily_price_data.daily_datetime_id)\
        .join(Daily_feature_data, Hour_price_data.daily_id == Daily_feature_data.daily_feature_datetime_id)

    df_data = pd.read_sql(query.statement, query.session.bind)
    df_data = df_data.drop(columns=[
        'daily_datetime_id',
        'daily_feature_datetime_id'
    ])

    df_data = df_data.sort_values(by='hour_datetime_id', ascending=True)
    df_data = df_data.reset_index(drop=True)

    return df_data


def get_live_minute_price_dataframe(logger, session):
    """
    Connects with database, queries datetime range data for daily, hourly
    and minute tables and returns a full dataframe.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
         pandas.core.frame.DataFrame: price/features dataframe
    """
    import pandas as pd
    from app.feature_service_models import Minute_price_data

    # query live minute price data from minute table
    minute_price_results = session.query(
        Minute_price_data.minute_datetime_id,
        Minute_price_data.btc_minute_price_close)\
        .order_by(Minute_price_data.minute_datetime_id.desc()).limit(60*24*1).all()

    df = pd.DataFrame({
        'datetime': [dt for dt, _ in minute_price_results],
        'minute_price': [price for _, price in minute_price_results]
    })
    df = df.sort_values(by='datetime', ascending=False)
    df['minute_price'] = df['minute_price'].astype(float).round(2)

    return df


def get_labels_ids(logger, session):
    """
    Connects with database, queries all available labels ID.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
         list: labels IDs
    """
    from app.prediction_service_models import Labels_directory

    # query and create list of labels
    labels_ids = session.query(Labels_directory.labels_id).distinct().all()
    labels_ids_lst = [label[0] for label in labels_ids]

    return labels_ids_lst


def get_labels_details(logger, session, labels_id_input):
    """
    Connects with database, queries labels details for given
    labels ID input.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         labels_id_input (str): labels ID input

    Returns:
         list: labels IDs
    """
    from app.prediction_service_models import Labels_directory

    # query labels info for input labels ID
    labels_info = session.query(Labels_directory).filter(
        Labels_directory.labels_id == labels_id_input).first()

    return labels_info


def create_df_labels(logger, session, df, labels_id_input):
    """
    Connects with database, queries labels details for given
    labels ID input and joins with feature/price dataframe.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         df (pandas.core.frame.DataFrame): Input price/feature dataframe
         labels_id_input (str): labels ID input

    Returns:
         pandas.core.frame.DataFrame: labeled price/features dataframe
    """
    from app.binary_classification import binary_classification_lookahead
    from app.query import get_labels_details
    import pandas as pd

    # get labels details from prediction-service-db
    labels_details = get_labels_details(logger, session, labels_id_input)
    df['hour_datetime_id'] = pd.to_datetime(df['hour_datetime_id'])

    # labels start datetime index
    start_date = labels_details.labels_start_datetime
    start_date_i = df[df['hour_datetime_id'] == start_date].index.item()

    # labels end datetime index
    end_date = labels_details.labels_end_datetime
    end_date_i = df[df['hour_datetime_id'] == end_date].index.item()

    df_labels = df.iloc[start_date_i:end_date_i].copy()

    # recreate classification lookahead and threshold values
    hour_price_list = df_labels['btc_hour_price_close'].to_list()
    binary_lookahead_lst = binary_classification_lookahead(
        hour_price_list,
        lookahead=labels_details.lookahead_value,
        threshold_percent=labels_details.percent_change_threshold
    )
    df_labels['labels_values'] = binary_lookahead_lst[0]
    df_labels['labels_binary'] = binary_lookahead_lst[1]
    df_labels = df_labels[[
        'hour_datetime_id', 'btc_hour_price_close',
        'labels_values', 'labels_binary']]

    return df_labels


def get_model_ids(logger, session, model_id_input=None):
    """
    Connects with database, queries all model IDs and returns list
    of strings.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         model_id_input (str): model ID input

    Returns:
         list: list of active model IDs
    """
    from app.prediction_service_models import Model_directory_info

    # query all model IDs and store in list of dictionaries
    if model_id_input:
        model_ids = session.query(Model_directory_info).filter_by(
            model_labels_id=model_id_input).all()
    else:
        model_ids = session.query(
            Model_directory_info.model_id).distinct().all()

    model_ids_lst = [
        {"label": str(model.model_id), "value": model.model_id} for model in model_ids]

    return model_ids_lst


def get_active_models(logger, session, *metric_input):
    """
    Connects with database, queries all deployed model IDs and returns
    list of strings sorted by metric input.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         metric_input (str): metric type input

    Returns:
         list: list of active model IDs
    """
    import numpy as np
    from app.prediction_service_models import Model_directory_info

    active_models = session.query(Model_directory_info).filter(
        Model_directory_info.deployed_status == True).distinct().all()

    # sort and reformat if metric input and return list of tuples
    if metric_input:
        metric_input = metric_input[0]

        active_model_lst = [(model.model_id, getattr(
            model, metric_input)) for model in active_models]
        active_model_update_lst = []
        for i, model_value_pair in enumerate(active_model_lst):
            if not model_value_pair[1] or np.isnan(model_value_pair[1]):
                active_model_update_lst.append((active_model_lst[i][0], False))
            else:
                active_model_update_lst.append(model_value_pair)

        active_model_lst_sorted = sorted(
            active_model_update_lst, key=lambda x: x[1], reverse=True)
        active_model_lst_formatted = []
        for x, y in active_model_lst_sorted:
            y_formatted = "{:.2f}".format(round(y, 2))
            active_model_lst_formatted.append((x, y_formatted))

        return active_model_lst_formatted
    else:
        active_model_lst = [str(model.model_id) for model in active_models]

        return active_model_lst


def get_model_info(logger, session, models_id_input):
    """
    Connects with prediction-service-db, queries all model info for given deployed
    model ID.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         models_id_input (str): model ID input

    Returns:
         sqlalchemy.orm.query.Query: model info SQL alchemy object
    """
    from app.prediction_service_models import Model_directory_info

    model_info = session.query(Model_directory_info).filter(
        Model_directory_info.model_id == models_id_input).first()

    return model_info


def get_mlflow_model_info(logger, session, models_id_input):
    """
    Connects with mlflow-db, executes SQL string to query all model ID
    tag info for given input model ID.

    Args:
         logger (logging.Logger): Initialized logger object
         session_mlflow (sqlalchemy.orm.session.Session): SQLAlchemy object
         models_id_input (str): model ID input

    Returns:
         lst: list of mlflow registered model tags
    """

    result = session.execute(f"""
                             SELECT * FROM registered_model_tags
                             WHERE name = '{models_id_input}';
                             """)
    rows = result.fetchall()

    # append queried results to list
    results_lst =[]
    for row in rows:
        results_lst.append(row[1])

    session.close()

    return results_lst


def get_model_object(logger, session, models_id_input):
    """
    Connects with database, queries all model objects for given deployed
    model ID.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         models_id_input (str): model ID input

    Returns:
         sqlalchemy.orm.query.Query: model info SQL alchemy object
    """
    from app.prediction_service_models import Model_binaries

    # query model object for model ID
    model_object = session.query(Model_binaries).filter(
        Model_binaries.model_info_id == models_id_input).first()

    return model_object


def get_model_object_gcs(logger, session, models_id_input):
    """
    Connects with mlflow database, queries model run ID for given
    deployed model ID input. Then defines unique model Google Cloud
    Storage path and gets stored model from artifact directory

    Args:
         logger (logging.Logger): initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object
         models_id_input (str): model ID input

    Returns:
         sklearn.model_type: trained ML model object
    """
    from google.cloud import storage
    import joblib
    import pickle
    from sqlalchemy import text

    # initialize a client to interact with Google Cloud Storage
    storage_client = storage.Client()

    # define SQLAlchemy query and get results
    query = text("""
                SELECT * FROM model_versions
                WHERE name = :value_name AND version = :value_version
                """)
    result = session.execute(query, {"value_name": f"{models_id_input}",
                                     "value_version": 1})
    rows = result.fetchall()

    # get and define model_id cloud storage path
    model_run_id = rows[0][8]

    # define Google Cloud Storage info and get bucket/blob
    bucket_name = "mlflow-models-nycdsa-project-4"
    file_name = f"0/{model_run_id}/artifacts/{models_id_input}/model.pkl"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # download pickle file and deserialize
    try:
        binary_model = blob.download_as_bytes()
        model = pickle.loads(binary_model)
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return model


def deployed_model_lst(logger, session):
    """
    Connects with prediction-service database, queries all active
    models and returns a list of model IDs.

    Args:
         logger (logging.Logger): Initialized logger object
         session (sqlalchemy.orm.session.Session): SQLAlchemy object

    Returns:
         lst: list of deployed models
    """
    from app.prediction_service_models import Model_directory_info

    # query deployed models
    query_lst = session.query(Model_directory_info.model_id)\
        .filter(Model_directory_info.deployed_status == True)\
        .order_by(Model_directory_info.model_id).all()
    
    deployed_model_lst = [model[0] for model in query_lst]

    return deployed_model_lst