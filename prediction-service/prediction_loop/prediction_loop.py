# prediction_loop.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.feature_service_models import Hour_price_data
from app.prediction_service_models import Model_directory_info, Prediction_records
from app.prediction_metrics import get_live_predicted_results_df
from app.query import current_datetime, get_full_feature_dataframe, get_model_object_gcs, deployed_model_lst

import datetime
from google.cloud import storage
import joblib
import logging
import pandas as pd
import pickle
from sqlalchemy import desc, update
import time


def prediction_loop():
    """
    ML model predictoin scheduling loop to call prediction models and
    current input features for predictions. Then commits prediction
    records every hour.

     Args:
        initialize (bool): Initialization boolean input

    Returns: None
    """
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
    
    # get latest committed datetime values
    logger.log(logging.INFO, "getting latest database datetime record")
    latest_datetime_record = session_feature_service.query(
        Hour_price_data).order_by(desc(Hour_price_data.hour_datetime_id)).first()
    hour_datetime_id = latest_datetime_record.hour_datetime_id
    logger.log(logging.INFO, f"initial hour datetime ID: {hour_datetime_id}")

    # get and save initial df volumes to dataframes directory
    df = get_full_feature_dataframe(logger, session_feature_service)
    df.to_csv('./dataframes/hour_data.csv', index=False)

    current_price_datetime = df['hour_datetime_id'].iloc[-1]
    current_price = df['btc_hour_price_close'].iloc[-1]
    df = df.drop(['hour_datetime_id', 'daily_id'], axis=1)
    logger.log(
        logging.INFO, f"initial hour dataframe update and saved: {hour_datetime_id}")
    
    # initialize active model IDs list
    deployed_models = deployed_model_lst(logger, session_prediction_service)
    print(deployed_models)

    # enter prediction loop
    while True:
        # check and update hour ID and predictions
        if hour_datetime_id != current_datetime()[1]:
            # update hour_datetime_id
            hour_datetime_id = current_datetime()[1]
            start_time = time.time()

            # get and save df volumes to dataframes directory
            df = get_full_feature_dataframe(
                logger, session_feature_service)
            df.to_csv('./dataframes/hour_data.csv', index=False)
            current_price_datetime = df['hour_datetime_id'].iloc[-1]
            current_price = df['btc_hour_price_close'].iloc[-1]
            df = df.drop(['hour_datetime_id', 'daily_id'], axis=1)
            X_predict = df.tail(1)

            # list of deployed models SQL alchemy objects
            deployed_models_lst = session_prediction_service.query(
                Model_directory_info).filter(Model_directory_info.deployed_status == True).all()
            prediction_id = f"prediction_{len(deployed_models_lst)}_{int(datetime.datetime.now().timestamp())}"
            n = 0
            for deployed_model in deployed_models_lst:
                prediction_model_id = deployed_model.model_id
                prediction_lookahead = deployed_model.labels.lookahead_value
                percent_change_threshold = deployed_model.labels.percent_change_threshold

                # calculate prediction datetime/threshold value
                predicted_value_datetime = current_price_datetime + \
                    datetime.timedelta(hours=int(prediction_lookahead)) # - 1) 
                predicted_price_threshold = current_price * \
                    float(1 + percent_change_threshold / 100)
                    
                # get model_object from google cloud storage
                logger.log(
                    logging.INFO, f"getting prediction model from GCS {prediction_model_id}")
                model = get_model_object_gcs(logger, session_mlflow, prediction_model_id)

                # prediction entry ID
                prediction_entry_id = f"{datetime.datetime.now().timestamp()}"
                prediction_value = int(model.predict(X_predict)[0])

                # commit prediction data to database
                logger.log(
                    logging.INFO, f"committing prediction entry {prediction_entry_id}")
                try:
                    new_prediction = Prediction_records(prediction_entry_id=prediction_entry_id,
                                                        current_datetime=current_price_datetime,
                                                        current_price=current_price,
                                                        percent_change_threshold=percent_change_threshold,
                                                        lookahead_steps=prediction_lookahead,
                                                        lookahead_datetime=predicted_value_datetime,
                                                        prediction_threshold=predicted_price_threshold,
                                                        prediction_value=prediction_value,
                                                        model_prediction_id=prediction_model_id)

                    session_prediction_service.add(new_prediction)
                    session_prediction_service.commit()

                except:
                    session_prediction_service.rollback()

                # get running prediction results
                try:
                    df_prediction_results = get_live_predicted_results_df(
                        logger, session_prediction_service, prediction_model_id)

                    # create update object for model running metrics
                    prediction_update = update(Model_directory_info).\
                        where(Model_directory_info.model_id == prediction_model_id).\
                        values(running_accuracy=float(df_prediction_results['running_accuracy'].iloc[0]),
                                running_TPR=float(
                            df_prediction_results['running_TPR'].iloc[0]),
                        running_FPR=float(df_prediction_results['running_FPR'].iloc[0]))
                    session_prediction_service.execute(prediction_update)

                    # commit the changes to the database
                    session_prediction_service.commit()

                    logger.log(
                        logging.INFO,
                        f"updated running metrics for {prediction_entry_id} successfully")

                except IndexError:
                    logger.log(
                        logging.INFO,
                        f"no metric to update for {prediction_entry_id}")

                time.sleep(1)
                logger.log(
                    logging.INFO, f"prediction entry {prediction_entry_id} successfully")

            # close session once all model predictions committed
            logger.log(
                logging.INFO, f"prediction {prediction_id} successful")
            end_time = time.time()  # time ends
            elapsed_time = end_time - start_time
            logger.log(
                logging.INFO, f"prediction loop elapsed time: {elapsed_time}")

        else:
            logger.log(logging.INFO, f"no prediction update")
            logger.log(
                logging.INFO, f"prediction loop complete: {current_datetime()[2]}")
            

        # check for changeds in deployed model list
        deployed_models_update = deployed_model_lst(logger, session_prediction_service)
        if deployed_models != deployed_models_update:
            # define model sets for comparison
            deployed_models_set = set(deployed_models)
            deployed_models_update_set = set(deployed_models_update)

            # check if added deployed models
            if len(deployed_models) < len(deployed_models_update):
                print("new model was deployed!")
                # find added model ID and store in list
                model_added = deployed_models_set.symmetric_difference(deployed_models_update_set)
                model_added_lst = list(model_added)

                # call add prediction entries from list of added models
                for model_id in model_added_lst:
                    print(f"adding {model_id}")
                    # get added model info and prediction model object
                    added_model_obj = session_prediction_service.query(Model_directory_info)\
                        .filter(Model_directory_info.model_id == model_id).first()
                    model_lookahead = added_model_obj.labels.lookahead_value
                    percent_change_threshold = added_model_obj.labels.percent_change_threshold
                    model = get_model_object_gcs(logger, session_mlflow, model_id)
                    print(model)

                    # load dataframe from volume
                    df = pd.read_csv('./dataframes/hour_data.csv')

                    # initializing prediction entries
                    for i in range(model_lookahead*10):
                        # offset i for reverse indexing and slice dataframe
                        i_offset = -(i+1)
                        df_predict_i = df.iloc[:i_offset]
                        
                        # get i_offset values
                        price_datetime_i = df_predict_i['hour_datetime_id'].iloc[-1]
                        price_datetime_i = pd.to_datetime(price_datetime_i)
                        price_i = df_predict_i['btc_hour_price_close'].iloc[-1]
                        df_predict_i = df_predict_i.drop(['hour_datetime_id', 'daily_id'], axis=1)
                        X_predict_i = df_predict_i.tail(1)
                        prediction_value_i = int(model.predict(X_predict_i)[0])

                        # commit to prediction-service-db
                        prediction_entry_id = f"{datetime.datetime.now().timestamp()}"

                        # calculate prediction datetime/threshold value
                        predicted_value_datetime_i = price_datetime_i + datetime.timedelta(hours=int(model_lookahead))# - 1)
                        predicted_price_threshold_i = price_i * float(1 + percent_change_threshold / 100)

                        # commit prediction data to database
                        logger.log(
                            logging.INFO, f"committing prediction entry {prediction_entry_id}")
                        try:
                            new_prediction_i = Prediction_records(prediction_entry_id=prediction_entry_id,
                                                                  current_datetime=price_datetime_i,
                                                                  current_price=price_i,
                                                                  percent_change_threshold=percent_change_threshold,
                                                                  lookahead_steps=model_lookahead,
                                                                  lookahead_datetime=predicted_value_datetime_i,
                                                                  prediction_threshold=predicted_price_threshold_i,
                                                                  prediction_value=prediction_value_i,
                                                                  model_prediction_id=model_id)

                            session_prediction_service.add(new_prediction_i)
                            session_prediction_service.commit()
                            print("predictions commited")

                        except Exception as e:
                            session_prediction_service.rollback()
                            print(f"rolledback error {e}")
                        session_prediction_service.close()

            # check if deleted deployed models
            elif len(deployed_models) > len(deployed_models_update):
                print("model was deleted")
                # find deleted model ID and store in list
                model_deleted = deployed_models_update_set.symmetric_difference(deployed_models_set)
                model_deleted_lst = list(model_deleted)
                
                # call delete predictions function from list of deleted models
                for model_id in model_deleted_lst:
                    print(f"deleting {model_id}")
                    session_prediction_service.query(Prediction_records)\
                        .filter(Prediction_records.model_prediction_id == model_id).delete()
                    session_prediction_service.commit()
                    session_prediction_service.close()
                    print(f"{model_id} prediction entries deleted")
                print(model_deleted_lst)

            # update deployed_models list
            deployed_models = deployed_model_lst(logger, session_prediction_service)
            print(deployed_models)
        else:
            print("no change in deployed models list")

        time.sleep(1)


prediction_loop()
