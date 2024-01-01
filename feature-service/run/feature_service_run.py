# feature_service_run.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.commit import commit_daily_data, commit_eth_daily_data, commit_daily_features, commit_hour_data, commit_eth_hour_data, commit_minute_data, commit_eth_minute_data
from app.feature_service_models import Minute_price_data
from app.get_data import daily_price, daily_features, hour_price, minute_price, eth_hour_price, eth_minute_price
from app.query import current_datetime

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
latest_datetime_record = session.query(Minute_price_data).order_by(
    desc(Minute_price_data.minute_datetime_id)).first()

daily_datetime_id = latest_datetime_record.daily_id
logger.log(logging.INFO, f"initial daily datetime ID: {daily_datetime_id}")
hour_datetime_id = latest_datetime_record.hour_id
logger.log(logging.INFO, f"initial hour datetime ID: {hour_datetime_id}")
minute_datetime_id = latest_datetime_record.minute_datetime_id
logger.log(logging.INFO, f"initial minute datetime ID: {minute_datetime_id}")

# enter while true loop
logger.log(logging.INFO, "starting query loop")
while True:
    # check if datetime daily object has updated
    if daily_datetime_id != current_datetime()[0]:
        daily_datetime_id = current_datetime()[0]
        logger.log(logging.INFO, f"daily ID value update: {daily_datetime_id}")

        # get previous day price data and commit under daily_datetime_id
        daily_datetime_input = current_datetime(
        )[0] - datetime.timedelta(days=1)

        # ETH daily data
        eth_daily_price_data = eth_hour_price(daily_datetime_input)
        commit_eth_daily_data(
            logger, session, daily_datetime_input, eth_daily_price_data)

        # BTC daily data
        daily_price_data = daily_price(logger, daily_datetime_input)
        commit_daily_data(logger, session, daily_datetime_id, daily_price_data)
        logger.log(
            logging.INFO, f"daily price values updated and committed: {daily_datetime_id}")

        # get previous day feature data and commit
        daily_feature_data = daily_features(logger, daily_datetime_input)
        commit_daily_features(
            logger, session, daily_datetime_id, daily_feature_data)
        logger.log(
            logging.INFO, f"daily feature values updated and committed: {daily_datetime_id}")

    # check and update hour ID
    elif hour_datetime_id != current_datetime()[1]:
        hour_datetime_id = current_datetime()[1]
        logger.log(logging.INFO, f"hour ID value update: {hour_datetime_id}")

        # get previous hour price data and commit under hour_datetime_id
        hour_datetime_input = current_datetime(
        )[1] - datetime.timedelta(hours=1)

        # ETH hour data
        eth_hour_price_data = eth_hour_price(hour_datetime_input)
        commit_eth_hour_data(
            logger, session, hour_datetime_input, eth_hour_price_data)

        # BTC hour data
        hour_price_data = hour_price(logger, hour_datetime_input)
        commit_hour_data(logger, session, hour_datetime_id, hour_price_data)

    # check and update minute ID
    elif minute_datetime_id != current_datetime()[2]:
        minute_datetime_id = current_datetime()[2]
        logger.log(
            logging.INFO, f"minute ID value update: {minute_datetime_id}")

        # get previous minute price data and commit under minute_datetime_id
        minute_datetime_input = current_datetime(
        )[2] - datetime.timedelta(minutes=1)

        # ETH minute data
        eth_minute_price_data = eth_minute_price(minute_datetime_input)
        commit_eth_minute_data(
            logger, session, minute_datetime_input, eth_minute_price_data)

        # BTC minute data
        minute_price_data = minute_price(logger, minute_datetime_input)
        commit_minute_data(
            logger, session, minute_datetime_id, minute_price_data)

    else:
        logger.log(logging.INFO, f"no data update")

    logger.log(logging.INFO, "query loop complete")
    time.sleep(50)
