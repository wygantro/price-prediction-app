# ./app/feature_service_models.py

from sqlalchemy import Column, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Daily_price_data(Base):
    __tablename__ = 'daily_price_data'

    daily_datetime_id = Column(DateTime(), primary_key=True)

    # daily price data
    btc_daily_price_open = Column(Numeric(15, 6))
    btc_daily_price_close = Column(Numeric(15, 6))
    btc_daily_price_high = Column(Numeric(15, 6))
    btc_daily_price_low = Column(Numeric(15, 6))
    btc_daily_price_vol = Column(Numeric(15, 6))
    btc_daily_price_vol_weight_avg = Column(Numeric(15, 6))
    # one-to-many relationship with hour_price_data
    hour_price_data = relationship(
        "Hour_price_data", back_populates="daily_price_data")
    # one-to-many relationship with minute_price_data
    minute_price_data = relationship(
        "Minute_price_data", back_populates="daily_price_data")


class Hour_price_data(Base):
    __tablename__ = 'hour_price_data'

    hour_datetime_id = Column(DateTime(), primary_key=True)
    daily_id = Column(DateTime(), ForeignKey(
        'daily_price_data.daily_datetime_id'))

    # hour price data
    btc_hour_price_open = Column(Numeric(15, 6))
    btc_hour_price_close = Column(Numeric(15, 6))
    btc_hour_price_high = Column(Numeric(15, 6))
    btc_hour_price_low = Column(Numeric(15, 6))
    btc_hour_price_vol = Column(Numeric(15, 6))
    btc_hour_price_vol_weight_avg = Column(Numeric(15, 6))
    # many-to-one relationship with daily_price_data
    daily_price_data = relationship(
        "Daily_price_data", back_populates="hour_price_data")
    # one-to-many relationship with minute_price_data
    minute_price_data = relationship(
        "Minute_price_data", back_populates="hour_price_data")


class Minute_price_data(Base):
    __tablename__ = 'minute_price_data'

    minute_datetime_id = Column(DateTime(), primary_key=True)
    daily_id = Column(DateTime(), ForeignKey(
        'daily_price_data.daily_datetime_id'))
    hour_id = Column(DateTime(), ForeignKey(
        'hour_price_data.hour_datetime_id'))

    # minute price data
    btc_minute_price_open = Column(Numeric(15, 6))
    btc_minute_price_close = Column(Numeric(15, 6))
    btc_minute_price_high = Column(Numeric(15, 6))
    btc_minute_price_low = Column(Numeric(15, 6))
    btc_minute_price_vol = Column(Numeric(15, 6))
    btc_minute_price_vol_weight_avg = Column(Numeric(15, 6))
    # many-to-one relationship with daily_price_data
    daily_price_data = relationship(
        "Daily_price_data", back_populates="minute_price_data")
    # many-to-one relationship with hour_price_data
    hour_price_data = relationship(
        "Hour_price_data", back_populates="minute_price_data")


class Daily_feature_data(Base):
    __tablename__ = 'daily_feature_data'

    daily_feature_datetime_id = Column(DateTime(), primary_key=True)

    # economic idicators
    real_gdp_quarterly = Column(Numeric(15, 6))
    real_gdp_per_capita_quarterly = Column(Numeric(15, 6))
    treasury_yield_3m_daily = Column(Numeric(15, 6))
    treasury_yield_2y_daily = Column(Numeric(15, 6))
    treasury_yield_5y_daily = Column(Numeric(15, 6))
    treasury_yield_7y_daily = Column(Numeric(15, 6))
    treasury_yield_10y_daily = Column(Numeric(15, 6))
    treasury_yield_30y_daily = Column(Numeric(15, 6))
    federal_funds_daily = Column(Numeric(15, 6))
    cpi_monthly = Column(Numeric(15, 6))
    inflation_yearly = Column(Numeric(15, 6))
    retail_sales_monthly = Column(Numeric(15, 6))
    durables_monthly = Column(Numeric(15, 6))
    unemployment_monthy = Column(Numeric(15, 6))
    nonfarm_payroll_monthly = Column(Numeric(15, 6))
    # commodities
    crude_oil_prices_wti_daily = Column(Numeric(15, 6))
    crude_oil_prices_brent_daily = Column(Numeric(15, 6))
    natural_gas_daily = Column(Numeric(15, 6))
    copper_monthly = Column(Numeric(15, 6))
    aluminum_monthly = Column(Numeric(15, 6))
    wheat_monthly = Column(Numeric(15, 6))
    corn_monthly = Column(Numeric(15, 6))
    cotten_monthly = Column(Numeric(15, 6))
    sugar_monthly = Column(Numeric(15, 6))
    coffee_monthly = Column(Numeric(15, 6))
    global_commodity_index_monthly = Column(Numeric(15, 6))
    # currency
    eur_usd_daily = Column(Numeric(15, 6))
    jpy_usd_daily = Column(Numeric(15, 6))
    gbp_usd_daily = Column(Numeric(15, 6))
    cad_usd_daily = Column(Numeric(15, 6))
    sek_usd_daily = Column(Numeric(15, 6))
    chf_usd_daily = Column(Numeric(15, 6))
    brl_usd_daily = Column(Numeric(15, 6))
    rub_usd_daily = Column(Numeric(15, 6))
    inr_usd_daily = Column(Numeric(15, 6))
    cny_usd_daily = Column(Numeric(15, 6))
    sar_usd_daily = Column(Numeric(15, 6))
