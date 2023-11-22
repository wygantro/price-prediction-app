# prediction_loop.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.feature_service_models import Hour_price_data
from app.prediction_service_models import Model_directory_info, Prediction_records
from app.query import current_datetime, get_full_feature_dataframe

import pandas as pd
import logging
from sqlalchemy import desc
import time
import datetime
import pickle

def prediction_loop(initialize=False):
     # run and load logger object
     logger = init_logger('prediction-service')
     
     # db url connection and create feature_service_session
     database_service = 'feature-service'
     db_url = connect_url(database_service)
     feature_service_session = create_db_models(logger, db_url, database_service)
     logger.log(logging.INFO, f"{database_service} session created")

     logger.log(logging.INFO, "getting latest database datetime record")
     latest_datetime_record = feature_service_session.query(Hour_price_data).order_by(desc(Hour_price_data.hour_datetime_id)).first()
     hour_datetime_id = latest_datetime_record.hour_datetime_id
     logger.log(logging.INFO, f"initial hour datetime ID: {hour_datetime_id}")

     # get and save initial df volumes to dataframes directory
     df = get_full_feature_dataframe(logger, feature_service_session)
     df.to_csv('./dataframes/hour_data.csv', index=False)

     current_price_datetime = df['hour_datetime_id'].iloc[-1]
     current_price = df['btc_hour_price_close'].iloc[-1]
     df = df.drop(['hour_datetime_id', 'daily_id'], axis=1)
     logger.log(logging.INFO, f"initial hour dataframe update and saved: {hour_datetime_id}")
     
     # db url connection and create feature_service_session
     database_service = 'prediction-service'
     db_url = connect_url(database_service)
     prediction_service_session = create_db_models(logger, db_url, database_service)
     logger.log(logging.INFO, f"{database_service} session created")

     # get initial list of deployed model IDs
     # deployed_models_lst = prediction_service_session.query(Model_directory_info).filter(Model_directory_info.deployed_status == True).all()

     if not initialize:
          while True:
               # get list of current deployed models
               # deployed_models_current_lst = prediction_service_session.query(Model_directory_info).filter(Model_directory_info.deployed_status == True).all()

               # check and update hour ID and predictions
               if hour_datetime_id != current_datetime()[1]:
                    hour_datetime_id = current_datetime()[1]
                    start_time = time.time()

                    # get and save df volumes to dataframes directory
                    df = get_full_feature_dataframe(logger, feature_service_session)
                    df.to_csv('./dataframes/hour_data.csv', index=False)
                    current_price_datetime = df['hour_datetime_id'].iloc[-1]
                    current_price = df['btc_hour_price_close'].iloc[-1]
                    df = df.drop(['hour_datetime_id', 'daily_id'], axis=1)
                    X_predict = df.tail(1)

                    # list of deployed models SQL alchemy objects
                    deployed_models_lst = prediction_service_session.query(Model_directory_info).filter(Model_directory_info.deployed_status == True).all()
                    prediction_id = f"prediction_{len(deployed_models_lst)}_{int(datetime.datetime.now().timestamp())}"
                    n = 0
                    for deployed_model in deployed_models_lst:
                         prediction_model_id = deployed_model.model_id
                         prediction_lookahead = deployed_model.labels.lookahead_value
                         percent_change_threshold = deployed_model.labels.percent_change_threshold

                         predicted_value_datetime = current_price_datetime + datetime.timedelta(hours=int(prediction_lookahead) - 1)
                         predicted_price_threshold = current_price * float(1 + percent_change_threshold / 100)

                         # get model_object as binary
                         model = pickle.loads(deployed_model.model_binaries.model_binary)
                         
                         # prediction entry ID
                         n += 1
                         prediction_entry_id = f"prediction_entry_{n}_{datetime.datetime.now().timestamp()}"
                         prediction_value = int(model.predict(X_predict)[0])

                         # commit prediction data to database
                         logger.log(logging.INFO, f"committing prediction entry {prediction_entry_id}")
                         try:
                              new_prediction = Prediction_records(prediction_entry_id=prediction_entry_id,
                                                                  prediction_id=prediction_id,
                                                                  datetime_entry=hour_datetime_id,
                                                                  current_datetime=current_price_datetime,
                                                                  current_price=current_price,
                                                                  percent_change_threshold=percent_change_threshold,
                                                                  lookahead_steps=prediction_lookahead,
                                                                  lookahead_datetime=predicted_value_datetime,
                                                                  prediction_threshold=predicted_price_threshold,
                                                                  prediction_value=prediction_value,
                                                                  model_prediction_id=prediction_model_id)
                              
                              prediction_service_session.add(new_prediction)
                              prediction_service_session.commit()
                         
                         except:
                              prediction_service_session.rollback()
                         
                         # update running prediction metrics in model_directory_info table
                         time.sleep(1)
                         logger.log(logging.INFO, f"prediction entry {prediction_entry_id} successfully")
                    
                    # close session once all model predictions committed
                    logger.log(logging.INFO, f"prediction {prediction_id} successful")
                    end_time = time.time() # time ends
                    elapsed_time = end_time - start_time
                    logger.log(logging.INFO, f"prediction loop elapsed time: {elapsed_time}")
               
               # # make predictions on recently deployed models
               # elif len(deployed_models_current_lst) > len(deployed_models_lst):

               #      # get list of recently activated models
               #      model_IDs_lst_update = [item.model_id for item in deployed_models_current_lst if item not in deployed_models_lst]
               #      print(model_IDs_lst_update)
                    
               #      # get current hour datetime
               #      hour_datetime_id = current_datetime()[1] # update hour_datetime_id
               #      start_time = time.time() # timer starts

               #      # get updated df and define values current price/datetime
               #      df = pd.read_csv('./dataframes/hour_data.csv')
               #      current_price_datetime = datetime.datetime.strptime(df['hour_datetime_id'].iloc[-1], "%Y-%m-%d %H:%M:%S")
               #      current_price = df['btc_hour_price_close'].iloc[-1]
               #      df = df.drop(['hour_datetime_id', 'daily_id'], axis=1)

               #      # get last sample from df and create X_predict features
               #      X_predict = df.tail(1)

               #      # query session object again to accomodate new prediction-service session
               #      model_obj_lst_update = [prediction_service_session.query(Model_directory_info).filter(Model_directory_info.model_id == model_id).first() for model_id in model_IDs_lst_update]

               #      # define prediction ID
               #      prediction_id = f"prediction_{len(deployed_models_lst)}_{int(datetime.datetime.now().timestamp())}"

               #      # initialize prediction_entry_id counter
               #      n = 0
               #      for deployed_model in model_obj_lst_update:
               #           prediction_model_id = deployed_model.model_id
               #           prediction_lookahead = deployed_model.labels.lookahead_value
               #           percent_change_threshold = deployed_model.labels.percent_change_threshold

               #           predicted_value_datetime = current_price_datetime + datetime.timedelta(hours=int(prediction_lookahead))
               #           predicted_price_threshold = current_price * float(1 + percent_change_threshold / 100)

               #           # get model_object as binary
               #           model = pickle.loads(deployed_model.model_binaries.model_binary)
                         
               #           # prediction entry ID
               #           n += 1
               #           prediction_entry_id = f"prediction_entry_{n}_{datetime.datetime.now().timestamp()}"

               #           # make prediction
               #           prediction_value = int(model.predict(X_predict)[0])

               #           # commit prediction data to database
               #           logger.log(logging.INFO, f"committing prediction entry {prediction_entry_id}")
               #           try:
               #                new_prediction = Prediction_records(prediction_entry_id=prediction_entry_id,
               #                                                    prediction_id=prediction_id,
               #                                                    datetime_entry=hour_datetime_id,
               #                                                    current_datetime=current_price_datetime,
               #                                                    current_price=current_price,
               #                                                    percent_change_threshold=percent_change_threshold,
               #                                                    lookahead_steps=prediction_lookahead,
               #                                                    lookahead_datetime=predicted_value_datetime,
               #                                                    prediction_threshold=predicted_price_threshold,
               #                                                    prediction_value=prediction_value,
               #                                                    model_prediction_id=prediction_model_id)
                              
               #                prediction_service_session.add(new_prediction)
               #                prediction_service_session.commit()
                         
               #           except:
               #                prediction_service_session.rollback()
                         
               #           # update running prediction metrics in model_directory_info table
               #           time.sleep(1) # delay to allow previous commit
                         
               #           logger.log(logging.INFO, f"prediction entry {prediction_entry_id} successfully")

               #      # update deployed_models_lst
               #      deployed_models_lst = prediction_service_session.query(Model_directory_info).filter(Model_directory_info.deployed_status == True).all()

               else:
                    logger.log(logging.INFO, f"no prediction update")
                    logger.log(logging.INFO, f"prediction loop complete: {current_datetime()[2]}")

               time.sleep(60)

prediction_loop()