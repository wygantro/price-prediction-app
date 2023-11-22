from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
from app.commit import current_datetime, commit_daily_data, commit_hour_data
from app.get_data import daily_date_range, daily_price, hour_price
import logging
import datetime

# run and load logger object
logger = init_logger('feature-service')
    
# db url connection and create engine
db_url = connect_url('feature-service')

# check db tables and create sessions
logger.log(logging.INFO, "creating database session")
session = create_db_models(logger, db_url)
logger.log(logging.INFO, "database session created")

# intialize daily features
start_daily_date = datetime.datetime(year=2022, month=10, day=3)
end_daily_date = datetime.datetime(year=2022, month=10, day=5)
date_daily_lst = daily_date_range(logger, start_daily_date, end_daily_date)

logger.log(logging.INFO, "commiting initial daily and hour batch data")
for date in date_daily_lst:
    # daily price
    daily_price_data = daily_price(logger, date)
    if date == daily_price_data[0]:
        commit_daily_data(logger, session, date, daily_price_data)
        logger.log(logging.INFO, f"daily price commited: {daily_price_data[0]}")
        
    # hour price
    datetime_hour_objects = [date + datetime.timedelta(hours=hour) for hour in range(24)]
    for date_hour in datetime_hour_objects:
        hour_price_data = hour_price(logger, date_hour)
        if date_hour == hour_price_data[0]:
            commit_hour_data(logger, session, date_hour, hour_price_data)
            logger.log(logging.INFO, f"hour price commited: {hour_price_data[0]}")
        if date_hour == current_datetime()[1]:
            break

logger.log(logging.INFO, f"initial data committed to database complete")