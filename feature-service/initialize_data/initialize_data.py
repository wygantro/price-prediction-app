# initialize_data.py

from app.app_init import init_logger, create_db_models
from app.get_data import daily_date_range, eth_daily_price, eth_hour_price, daily_price, hour_price, daily_features

from app.connect_db import connect_url
from app.commit import current_datetime, commit_eth_daily_data, commit_eth_hour_data, commit_daily_data, commit_hour_data, commit_daily_features
from app.feature_service_models import Hour_price_data

import datetime
import logging

# run and load logger object
logger = init_logger('feature-service')

# db url connection and create engine
db_url = connect_url('feature-service')

# check db tables and create sessions
logger.log(logging.INFO, "creating database session")
session = create_db_models(logger, db_url, 'feature-service')
logger.log(logging.INFO, "database session created")

# intialize daily features
start_daily_date = datetime.datetime(year=2024, month=7, day=11)
end_daily_date = datetime.datetime(year=2025, month=1, day=3)
date_daily_lst = daily_date_range(logger, start_daily_date, end_daily_date)

logger.log(logging.INFO, "commiting initial daily and hour batch data")
for date in date_daily_lst:
    # daily price
    daily_btc_price_data = daily_price(logger, date) # get btc daily price
    daily_price_data = eth_daily_price(logger, date) # get eth daily price
    if date == daily_price_data[0] and date == daily_btc_price_data[0]:        
        # commit daily price data
        commit_daily_data(logger, session, date, daily_btc_price_data) # btc daily price
        logger.log(
            logging.INFO, f"daily btc price commited: {daily_btc_price_data[0]}")
        commit_eth_daily_data(logger, session, date, daily_price_data) # eth daily price
        logger.log(
            logging.INFO, f"daily eth price commited: {daily_price_data[0]}")
                
        # get previous day feature data and commit
        daily_feature_data = daily_features(logger, date)
        commit_daily_features(
            logger, session, date, daily_feature_data)
        logger.log(
            logging.INFO, f"daily feature values updated and committed: {date}")
        
    # hour price
    datetime_hour_objects = [
        date + datetime.timedelta(hours=hour) for hour in range(24)]
    for date_hour in datetime_hour_objects:
        hour_btc_price_data = hour_price(logger, date_hour) # get btc hour price
        hour_price_data = eth_hour_price(logger, date_hour) # get eth hour price
        if date_hour == hour_price_data[0]:
            commit_hour_data(logger, session, date_hour, hour_btc_price_data) # btc hour price
            logger.log(
                logging.INFO, f"hour price commited: {hour_price_data[0]}")
            commit_eth_hour_data(logger, session, date_hour, hour_price_data) # eth hour price
            logger.log(
                logging.INFO, f"hour price commited: {hour_price_data[0]}")
        if date_hour == current_datetime()[1]:
            break

logger.log(logging.INFO, f"initial data committed to database complete")