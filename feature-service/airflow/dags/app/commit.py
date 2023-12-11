# ./app/commit.py

import logging


def current_datetime():
    """
    Output current datetime object for daily, hourly and minute timeframe.

    This function returns three standardized datetime objects to be 
    utilized as database unique value IDs for API timeseries data.

    Args: None

    Returns:
        datetime.datetime: Current datetime (year, month, day)
        datetime.datetime: Current datetime (year, month, day, hour)
        datetime.datetime: Current datetime (year, month, day, hour, 
        minute)
    """
    import datetime
    import pytz

    # define daily, hour and minute datetime
    utc = pytz.UTC
    now = datetime.datetime.now(utc)
    daily_datetime_id = datetime.datetime(
        year=now.year, month=now.month, day=now.day)
    hour_datetime_id = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour)
    minute_datetime_id = datetime.datetime(year=now.year,
        month=now.month, day=now.day, hour=now.hour, minute=now.minute)
    
    return daily_datetime_id, hour_datetime_id, minute_datetime_id


# daily freq price data
def commit_daily_data(logger, session, date_daily, daily_price_data):
    """
    Index and commit daily datetime ID and price data.

    This function takes input logger and database session objects from 
    application initialization. Then takes a datetime object ID and 
    daily price data list and commits to database.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        date_daily (datetime.datetime): Daily datetime object timestamp 
        daily_price_data (list): Indexable list from daily_price output

    Returns: None
    """
    from app.feature_service_models import Daily_price_data

    # commit daily price data
    try:
        daily_data = Daily_price_data(
            daily_datetime_id=date_daily,
            btc_daily_price_open=daily_price_data[1],
            btc_daily_price_close=daily_price_data[2],
            btc_daily_price_high=daily_price_data[3],
            btc_daily_price_low=daily_price_data[4],
            btc_daily_price_vol=daily_price_data[5],
            btc_daily_price_vol_weight_avg=daily_price_data[6]
        )

        session.add(daily_data)
        session.commit()
        logger.log(
            logging.INFO, "daily data successfully committed to the database")

    except Exception as e:
        session.rollback()
        logger.log(logging.ERROR, f"an error occurred: {e}")
    finally:
        session.close()


# intra daily freq data
def commit_intra_daily_data(logger, session, intra_daily_price_update):
    """
    Queries latest daily price record and updates with intra daily data.

    This function takes input logger and database session objects from 
    application initialization. Then queries daily price data table and
    gets latest record to update with intra daily price data list.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        intra_daily_price_update (list): Indexable list from daily_price 
        output

    Returns: None
    """
    from app.feature_service_models import Daily_price_data
    from sqlalchemy import desc

    # intra daily update
    latest_daily_price_record = session.query(Daily_price_data).order_by(
        desc(Daily_price_data.daily_datetime_id)).first()
    latest_daily_price_record_id = latest_daily_price_record.daily_datetime_id

    if latest_daily_price_record_id == intra_daily_price_update[0]:
        try:
            latest_daily_price_record.btc_daily_price_open = intra_daily_price_update[1]
            latest_daily_price_record.btc_daily_price_close = intra_daily_price_update[2]
            latest_daily_price_record.btc_daily_price_high = intra_daily_price_update[3]
            latest_daily_price_record.btc_daily_price_low = intra_daily_price_update[4]
            latest_daily_price_record.btc_daily_price_vol = intra_daily_price_update[5]
            latest_daily_price_record.btc_daily_price_vol_weight_avg = intra_daily_price_update[
                6]
            session.commit()
            logger.log(
                logging.INFO,
                f"latest intra daily price data {latest_daily_price_record_id} updated"
            )
        except Exception as e:
            session.rollback()
            logger.log(logging.ERROR, f"an error occurred: {e}")
        finally:
            session.close()
    else:
        logger.log(
            logging.INFO, "latest intra daily price data does not match API")


# daily freq feature data
def commit_daily_features(logger, session, date_daily, daily_feature_data_dict):
    """
    Index and commit daily datetime ID and associated features.

    This function takes input logger and database session objects from 
    application initialization. Then takes a datetime object ID and 
    daily price feature dictionary and commits to database.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        date_daily (datetime.datetime): Daily datetime object timestamp 
        daily_feature_data_dict (dict): Feature: Value dictionary associated 
        with daily ID

    Returns: None
    """
    from app.feature_service_models import Daily_feature_data

    # commit daily features
    try:
        daily_features = Daily_feature_data(
            daily_feature_datetime_id=date_daily,
            # economic idicators
            real_gdp_quarterly=daily_feature_data_dict['real_gdp_quarterly'],
            real_gdp_per_capita_quarterly=daily_feature_data_dict[
                'real_gdp_per_capita_quarterly'],
            treasury_yield_3m_daily=daily_feature_data_dict[
                'treasury_yield_3m_daily'],
            treasury_yield_2y_daily=daily_feature_data_dict[
                'treasury_yield_2y_daily'],
            treasury_yield_5y_daily=daily_feature_data_dict[
                'treasury_yield_5y_daily'],
            treasury_yield_7y_daily=daily_feature_data_dict[
                'treasury_yield_7y_daily'],
            treasury_yield_10y_daily=daily_feature_data_dict[
                'treasury_yield_10y_daily'],
            treasury_yield_30y_daily=daily_feature_data_dict[
                'treasury_yield_30y_daily'],
            federal_funds_daily=daily_feature_data_dict['federal_funds_daily'],
            cpi_monthly=daily_feature_data_dict['cpi_monthly'],
            inflation_yearly=daily_feature_data_dict['inflation_yearly'],
            retail_sales_monthly=daily_feature_data_dict['retail_sales_monthly'],
            durables_monthly=daily_feature_data_dict['durables_monthly'],
            unemployment_monthy=daily_feature_data_dict['unemployment_monthy'],
            nonfarm_payroll_monthly=daily_feature_data_dict[
                'nonfarm_payroll_monthly'],
            # commodities
            crude_oil_prices_wti_daily=daily_feature_data_dict[
                'crude_oil_prices_wti_daily'],
            crude_oil_prices_brent_daily=daily_feature_data_dict[
                'crude_oil_prices_brent_daily'],
            natural_gas_daily=daily_feature_data_dict['natural_gas_daily'],
            copper_monthly=daily_feature_data_dict['copper_monthly'],
            aluminum_monthly=daily_feature_data_dict['aluminum_monthly'],
            wheat_monthly=daily_feature_data_dict['wheat_monthly'],
            corn_monthly=daily_feature_data_dict['corn_monthly'],
            cotten_monthly=daily_feature_data_dict['cotten_monthly'],
            sugar_monthly=daily_feature_data_dict['sugar_monthly'],
            coffee_monthly=daily_feature_data_dict['coffee_monthly'],
            global_commodity_index_monthly=daily_feature_data_dict[
                'global_commodity_index_monthly'],
            # daily currency data
            eur_usd_daily=daily_feature_data_dict['eur_usd_daily'],
            jpy_usd_daily=daily_feature_data_dict['jpy_usd_daily'],
            gbp_usd_daily=daily_feature_data_dict['gbp_usd_daily'],
            cad_usd_daily=daily_feature_data_dict['cad_usd_daily'],
            sek_usd_daily=daily_feature_data_dict['sek_usd_daily'],
            chf_usd_daily=daily_feature_data_dict['chf_usd_daily'],
            brl_usd_daily=daily_feature_data_dict['brl_usd_daily'],
            rub_usd_daily=daily_feature_data_dict['rub_usd_daily'],
            inr_usd_daily=daily_feature_data_dict['inr_usd_daily'],
            cny_usd_daily=daily_feature_data_dict['cny_usd_daily'],
            sar_usd_daily=daily_feature_data_dict['sar_usd_daily'])

        session.add(daily_features)
        session.commit()
        logger.log(
            logging.INFO, "daily features successfully committed to the database")

    except Exception as e:
        session.rollback()
        logger.log(logging.ERROR, f"an error occurred: {e}")
    finally:
        session.close()


# hour feature data
def commit_hour_data(logger, session, date_hour, hour_price_data):
    """
    Index and commit hourly datetime ID and price data.

    This function takes input logger and database session objects from 
    application initialization. Then takes a datetime object ID and 
    hourly price data list and commits to database.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        date_hour (datetime.datetime): Hourly datetime object timestamp 
        hour_price_data (list): Indexable list from hour_price output

    Returns: None
    """
    from app.feature_service_models import Hour_price_data

    # commit hour price data
    try:
        hour_data = Hour_price_data(hour_datetime_id=date_hour,
                                    daily_id=date_hour.replace(hour=0),
                                    btc_hour_price_open=hour_price_data[1],
                                    btc_hour_price_close=hour_price_data[2],
                                    btc_hour_price_high=hour_price_data[3],
                                    btc_hour_price_low=hour_price_data[4],
                                    btc_hour_price_vol=hour_price_data[5],
                                    btc_hour_price_vol_weight_avg=hour_price_data[6])

        session.add(hour_data)
        session.commit()
        logger.log(
            logging.INFO, "hour data successfully committed to the database")

    except Exception as e:
        session.rollback()
        logger.log(logging.ERROR, f"an error occurred: {e}")

    finally:
        session.close()


# update intra hour data
def commit_intra_hour_data(logger, session, intra_hour_price_update):
    """
    Queries latest hour price record and updates with intra hour data.

    This function takes input logger and database session objects from 
    application initialization. Then queries hour data table and gets 
    latest record to update with intra hour price data list.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        intra_hour_price_update (list): Indexable list from hour_price 
        output

    Returns: None
    """
    from app.feature_service_models import Hour_price_data
    from sqlalchemy import desc

    # intra hour update
    latest_hour_price_record = session.query(Hour_price_data).order_by(
        desc(Hour_price_data.hour_datetime_id)).first()
    latest_hour_price_record_id = latest_hour_price_record.hour_datetime_id

    if latest_hour_price_record_id == intra_hour_price_update[0]:
        try:
            latest_hour_price_record.btc_hour_price_open = intra_hour_price_update[1]
            latest_hour_price_record.btc_hour_price_close = intra_hour_price_update[2]
            latest_hour_price_record.btc_hour_price_high = intra_hour_price_update[3]
            latest_hour_price_record.btc_hour_price_low = intra_hour_price_update[4]
            latest_hour_price_record.btc_hour_price_vol = intra_hour_price_update[5]
            latest_hour_price_record. \
                btc_hour_price_vol_weight_avg = intra_hour_price_update[6]
            session.commit()
            logger.log(
                logging.INFO, f"latest intra hour price data {latest_hour_price_record_id} updated")
        except Exception as e:
            session.rollback()
            logger.log(logging.ERROR, f"an error occurred: {e}")
        finally:
            session.close()
    else:
        logger.log(
            logging.INFO, "latest intra hour price data does not match API")


# minute freq data
def commit_minute_data(logger, session, date_minute, minute_price_data):
    """
    Index and commit minute datetime ID and price data.

    This function takes input logger and database session objects from 
    application initialization. Then takes a datetime object ID and 
    minute price data list and commits to database.

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): SQLAlchemy object
        date_minute (datetime.datetime): Minute datetime object timestamp 
        minute_price_data (list): Indexable list from minute_price output

    Returns: None
    """
    from app.feature_service_models import Minute_price_data

    # commit minute price data
    try:
        minute_data = Minute_price_data(
            minute_datetime_id=date_minute,
            hour_id=date_minute.replace(minute=0),
            daily_id=date_minute.replace(hour=0, minute=0),
            btc_minute_price_open=minute_price_data[1],
            btc_minute_price_close=minute_price_data[2],
            btc_minute_price_high=minute_price_data[3],
            btc_minute_price_low=minute_price_data[4],
            btc_minute_price_vol=minute_price_data[5],
            btc_minute_price_vol_weight_avg=minute_price_data[6]
        )

        session.add(minute_data)
        session.commit()
        logger.log(
            logging.INFO, "minute data successfully committed to the database")

    except Exception as e:
        session.rollback()
        logger.log(logging.ERROR, f"an error occurred: {e}")

    finally:
        session.close()