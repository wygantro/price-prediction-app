# ./app/test_service_models.py

from sqlalchemy import Column, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Daily_eth_price_data(Base):
    __tablename__ = 'daily_eth_price_data'

    daily_datetime_id = Column(DateTime(), primary_key=True)

    # daily price data
    eth_daily_price_open = Column(Numeric(15, 6))
    eth_daily_price_close = Column(Numeric(15, 6))
    eth_daily_price_high = Column(Numeric(15, 6))
    eth_daily_price_low = Column(Numeric(15, 6))
    eth_daily_price_vol = Column(Numeric(15, 6))
    eth_daily_price_vol_weight_avg = Column(Numeric(15, 6))


class Hour_eth_price_data(Base):
    __tablename__ = 'hour_eth_price_data'

    hour_datetime_id = Column(DateTime(), primary_key=True)

    # hour price data
    eth_hour_price_open = Column(Numeric(15, 6))
    eth_hour_price_close = Column(Numeric(15, 6))
    eth_hour_price_high = Column(Numeric(15, 6))
    eth_hour_price_low = Column(Numeric(15, 6))
    eth_hour_price_vol = Column(Numeric(15, 6))
    eth_hour_price_vol_weight_avg = Column(Numeric(15, 6))


class Minute_eth_price_data(Base):
    __tablename__ = 'minute_eth_price_data'

    minute_datetime_id = Column(DateTime(), primary_key=True)

    # minute price data
    eth_minute_price_open = Column(Numeric(15, 6))
    eth_minute_price_close = Column(Numeric(15, 6))
    eth_minute_price_high = Column(Numeric(15, 6))
    eth_minute_price_low = Column(Numeric(15, 6))
    eth_minute_price_vol = Column(Numeric(15, 6))
    eth_minute_price_vol_weight_avg = Column(Numeric(15, 6))