# ./app/feature_service_run.py

from app.connect_db import connect_url
from app.commit import commit_daily_data, commit_intra_daily_data, commit_daily_features, commit_hour_data, commit_intra_hour_data, commit_minute_data
from app.app_init import init_logger, create_db_models
from app.get_data import daily_price, daily_features, hour_price, minute_price
from app.query import current_datetime
from app.feature_service_models import Minute_price_data
import datetime
import logging
from sqlalchemy import desc
import time

# initialize logger
logger = init_logger('feature-service')

# db url connection and create session
db_url = connect_url('feature-service')
session = create_db_models(logger, db_url, 'feature-service')
logger.log(logging.INFO, "database session created")

# get and define initial datatime id
logger.log(logging.INFO, "getting latest database datetime record")
latest_datetime_record = session.query(Minute_price_data).order_by(desc(Minute_price_data.minute_datetime_id)).first()

daily_datetime_id = latest_datetime_record.daily_id
logger.log(logging.INFO, f"initial daily datetime ID: {daily_datetime_id}")
hour_datetime_id = latest_datetime_record.hour_id
logger.log(logging.INFO, f"initial hour datetime ID: {hour_datetime_id}")
minute_datetime_id = latest_datetime_record.minute_datetime_id
logger.log(logging.INFO, f"initial minute datetime ID: {minute_datetime_id}")

# begin loop
logger.log(logging.INFO, "starting query loop")
while True:
    # check if datetime daily object has updated
    if daily_datetime_id != current_datetime()[0]:
        daily_datetime_id = current_datetime()[0]
        logger.log(logging.INFO, f"daily ID value update: {daily_datetime_id}")

        # get price data and commit
        daily_price_data = daily_price(logger, daily_datetime_id)
        commit_daily_data(logger, session, daily_datetime_id, daily_price_data)        
        logger.log(logging.INFO, f"daily price values updated and commit: {daily_datetime_id}")
        
        # get feature data and commit
        daily_datetime_input = current_datetime()[0] - datetime.timedelta(days=1)
        daily_feature_data = daily_features(logger, daily_datetime_input)
        commit_daily_features(logger, session, daily_datetime_id, daily_feature_data)    
        logger.log(logging.INFO, f"daily feature values updated and commit: {daily_datetime_id}")

    # check and update hour ID
    elif hour_datetime_id != current_datetime()[1]:
        hour_datetime_id = current_datetime()[1]
        hour_price_data = hour_price(logger, hour_datetime_id)
        commit_hour_data(logger, session, hour_datetime_id, hour_price_data)    
        logger.log(logging.INFO, f"hour ID value update: {hour_datetime_id}")

        # intra daily update
        logger.log(logging.INFO, f"updating intra daily data: {hour_datetime_id}")
        intra_daily_datetime_id = current_datetime()[0]
        intra_daily_price_update = daily_price(logger, intra_daily_datetime_id)
        commit_intra_daily_data(logger, session, intra_daily_price_update)

    # check and update minute ID
    elif minute_datetime_id != current_datetime()[2]:
        minute_datetime_id = current_datetime()[2]
        minute_price_data = minute_price(logger, minute_datetime_id)
        commit_minute_data(logger, session, minute_datetime_id, minute_price_data)
        logger.log(logging.INFO, f"minute ID value update: {minute_datetime_id}")

        # intra hour update
        logger.log(logging.INFO, f"updating intra hour data: {minute_datetime_id}")
        intra_hour_datetime_id = current_datetime()[1]
        intra_hour_price_update = hour_price(logger, intra_hour_datetime_id)
        commit_intra_hour_data(logger, session, intra_hour_price_update)
    
    else:
        logger.log(logging.INFO, f"no data update")
    
    logger.log(logging.INFO, "query loop complete")
    time.sleep(50)
    