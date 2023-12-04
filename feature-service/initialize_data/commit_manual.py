# commit_manual.py

from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
import logging
from datetime import datetime, timedelta
from app.feature_service_models import Hour_price_data

# define logger object and database connection
logger = init_logger('feature-service')
db_url = connect_url('feature-service')

# check db tables and create sessions
logger.log(logging.INFO, "creating database session")
session = create_db_models(logger, db_url)
logger.log(logging.INFO, "database session created")

# define time frame for manual commit
daily_time = datetime(2022, 10, 4)
start_time = datetime(2022, 10, 4, 0, 0)
end_time = datetime(2022, 10, 5, 0, 0)

# loop over timeframe and commit hour price data
current_time = start_time
while current_time < end_time:
    commit_input = Hour_price_data(hour_datetime_id=current_time,
                                   daily_id=daily_time,
                                   btc_hour_price_open=20022.00,
                                   btc_hour_price_close=20020.03,
                                   btc_hour_price_high=20030.70,
                                   btc_hour_price_low=20020.03,
                                   btc_hour_price_vol=1.05,
                                   btc_hour_price_vol_weight_avg=20027.32)

    session.add(commit_input)
    session.commit()

    current_time += timedelta(hours=1)

session.close()