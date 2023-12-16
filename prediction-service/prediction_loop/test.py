# test.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.prediction_service_models import Model_directory_info
from app.query import current_datetime, get_full_feature_dataframe, get_model_object_gcs

import logging
import pandas as pd

# run and load logger object
logger = init_logger('prediction-service')

# define sessions
# feature-service-db
database_service = 'feature-service'
db_url = connect_url(database_service)
session_feature_service = create_db_models(
    logger, db_url, database_service)
logger.log(logging.INFO, f"{database_service} session created")

# prediction-service-db
database_service = 'prediction-service'
db_url = connect_url(database_service)
session_prediction_service = create_db_models(
    logger, db_url, database_service)
logger.log(logging.INFO, f"{database_service} session created")

# mlflow-db engine
database_service = 'mlflow'
db_url = connect_url(database_service)
session_mlflow = create_db_models(
    logger, db_url, database_service)
logger.log(logging.INFO, f"{database_service} session created")

# list of deployed models SQL alchemy objects
deployed_models_obj_lst = session_prediction_service.query(Model_directory_info)\
    .filter(Model_directory_info.deployed_status == True).all()
for deployed_model in deployed_models_obj_lst:
    model_id = deployed_model.model_id
    model_lookahead = deployed_model.labels.lookahead_value
    print(model_lookahead)

    # get model object
    model = get_model_object_gcs(logger, session_mlflow, model_id)
    print(model)

    # get dataframe from volume directory
    df = pd.read_csv('./dataframes/hour_data.csv')

    for i in range(model_lookahead*2):
        # offset i for reverse indexing and slice dataframe
        i_offset = -(i+1)
        df_predict_i = df.iloc[:i_offset]

        # get i_offset values
        price_datetime_i = df_predict_i['hour_datetime_id'].iloc[-1]
        price_i = df_predict_i['btc_hour_price_close'].iloc[-1]
        df_predict_i = df_predict_i.drop(['hour_datetime_id', 'daily_id'], axis=1)
        X_predict_i = df_predict_i.tail(1)

        prediction_value = int(model.predict(X_predict_i)[0])
        print((prediction_value, price_datetime_i, price_i))