from datetime import datetime, timedelta
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app_init import init_logger
from app.test_service_models import Daily_eth_price_data
from app.query import current_datetime

# db url connection and create session
from app.test_service_models import Base

# create database engine
db_url = 'postgresql://user:postgres@35.184.60.255:5432/test-service-db'
engine = create_engine(db_url)

# create tables with Base object from models
Base.metadata.create_all(engine)

# define and return session object
Session = sessionmaker(bind=engine)
session = Session()

# # Define a function to call the API and save data to the database
# def call_api_and_save_to_db():

#     engine = create_engine('postgresql://user:postgres@35.184.60.255:5432/test-service-db')
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # get eth daily price
#     from app.get_data import eth_daily_price
#     daily_price = eth_daily_price(current_datetime()[0])
#     print(current_datetime()[0])
#     print(daily_price)

#     new_data = Daily_eth_price_data(
#         daily_datetime_id=current_datetime()[0],
#         eth_daily_price_open=daily_price[1],
#         eth_daily_price_close=daily_price[2],
#         eth_daily_price_high=daily_price[3],
#         eth_daily_price_low=daily_price[4],
#         eth_daily_price_vol=daily_price[5],
#         eth_daily_price_vol_weight_avg=daily_price[6]
#         )
#     session.add(new_data)
#     session.commit()
#     session.close()
#     print("Data saved to database successfully")


# call_api_and_save_to_db()