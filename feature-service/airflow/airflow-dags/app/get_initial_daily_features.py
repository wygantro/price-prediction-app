# ./app/get_initial_daily_features.py

import logging


def initial_daily_feature_df(logger, api_dict, *args_df, initialize=False):
    """
    Initial daily feature API call over a set datetime range.

    This function takes in a reference dictionary to call AlphaVantage API 
    data from 1/1/2017 to current datetime. Then tabulates and returns a 
    dataframe of results. 

    Args:
        logger (logging.Logger): Initialized logger object
        api_dict (dict): API address dictionary
        *args_df (pandas.core.frame.DataFrame): Optional reference dataframe
        initialize: Default to False. True if no reference dataframe input

    Returns:
        pandas.core.frame.DataFrame: dataframe of daily feature results
    """
    import pandas as pd
    import requests
    from datetime import datetime, date

    # initialize and define start datetime
    logger.log(logging.INFO, "initializing date range for daily features")
    api_dict = api_dict
    if not api_dict:
        logger.log(logging.ERROR, "input reference API dictionary required")
        raise ValueError("input reference API dictionary required")
    elif initialize:
        start_date = datetime.strptime("2017-01-01", "%Y-%m-%d")
    elif not initialize and args_df:
        start_date = datetime.today()
    else:
        logger.log(logging.ERROR, "input reference dataframe required")
        raise ValueError("input reference dataframe required")
    
    # deine end datetime and empty price dataframes
    end_date = datetime.today()
    D = 'D'
    date_list = list(pd.date_range(
        start_date, end_date, freq=D).strftime("%Y-%m-%d"))
    df_date = pd.DataFrame({'date': date_list}).set_index('date', drop=True)
    df_price = pd.DataFrame({'date': [],
                             'btc_close_price': [],
                             'btc_volume': [],
                             'btc_volume_weighted': [],
                             'btc_open_price': [],
                             'btc_high_price': [],
                             'btc_low_price': [],
                             'btc_n_transactions': []})
    logger.log(logging.INFO,
               "requesting daily price conditions from polygon.io API")
    
    # for loop over datetime values and request API
    for date_i in date_list:
        url = 'https://api.polygon.io/v2/aggs/grouped/locale/global/market/crypto/{date}?adjusted=true&apiKey=68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj'.format(
            date=date_i)
        r = requests.get(url)
        data = r.json()['results']
        btc_daily_price_info = list(
            filter(lambda ticker_info: ticker_info['T'] == 'X:BTCUSD', data))
        df_price.loc[len(df_price.index)] = [
            date_i,
            btc_daily_price_info[0]['c'],
            btc_daily_price_info[0]['v'],
            btc_daily_price_info[0]['vw'],
            btc_daily_price_info[0]['o'],
            btc_daily_price_info[0]['h'],
            btc_daily_price_info[0]['l'],
            btc_daily_price_info[0]['n']
        ]
    
    # reformat df_price
    logger.log(logging.INFO, "storing price conditions in dictionary")
    df_price = df_price.set_index('date')
    df_price = df_date.join(df_price)
    logger.log(logging.INFO, "getting json AlphaVantage API info")

    # append and store in API dictionary
    api_values_dict = {}
    for metric, url in api_dict.items():
        url = url
        r = requests.get(url)
        try:
            data = r.json()['data']
        except KeyError:
            data = []
            for date, value in r.json()['Time Series FX (Daily)'].items():
                data.append({'date': date, 'value': value['1. open']})
        date_lst = []
        values_lst = []
        for i in data:
            date_lst.append(i['date'])
            values_lst.append(i['value'])
        api_values_dict[str(metric)] = {
            'date': date_lst, str(metric): values_lst}
    logger.log(logging.INFO,
               "requesting daily price conditions from AlphaVantage API")
    logger.log(logging.INFO, "building initial dataframe")

    # for loop over api values dictionary and store in dataframe
    df_daily = df_price
    for metric_name, values in api_values_dict.items():
        df_metric_name = pd.DataFrame(values).set_index('date')
        df_daily = df_daily.join(df_metric_name).replace('.', method='ffill').fillna(
            method='ffill').fillna(method='bfill').astype(float)
    df_daily = df_daily.reset_index(drop=False)

    if initialize:
        logger.log(logging.INFO, "returning initial dataframe")
        df = df_daily
        df['date_predict'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        return df
    elif not initialize and args_df:
        df = args_df[0].iloc[:, :-6]
        last_record = df.iloc[-1]
        last_record_delta = datetime.today(
        ) - datetime.strptime(last_record['date'], "%Y-%m-%d")
        df = pd.concat([df, df_daily.tail(last_record_delta.days)]
                       ).reset_index(drop=True)
        
        return df
    
    else:
        logger.log(logging.ERROR, "check input df reference type")
        raise ValueError("check input df reference type")


def commit_initial_daily_features(logger, session, df):
    """
    Indexes input daily feature dataframe and commits to database

    This function takes in a reference dictionary to call AlphaVantage API 
    data from 1/1/2017 to current datetime. Then tabulates and returns a 
    dataframe of results. 

    Args:
        logger (logging.Logger): Initialized logger object
        session (sqlalchemy.orm.session.Session): Initialized SQLAlchemy session object
        df (pandas.core.frame.DataFrame): Daily feature values dataframe

    Returns: None
    """
    from app.feature_service_models import Daily_feature_data
    import datetime

    # for loop over feature dataframe and commit
    logger.log(logging.INFO, "commiting initial values to database")
    indicators_lst = []
    for i, rows in df.iterrows():
        indicators = [
            rows.date,
            rows.btc_close_price,
            rows.btc_volume,
            rows.btc_volume_weighted,
            rows.btc_open_price,
            rows.btc_high_price,
            rows.btc_low_price,
            rows.btc_n_transactions,
            # economic idicators
            rows.real_gdp_quarterly,
            rows.real_gdp_per_capita_quarterly,
            rows.treasury_yield_3m_daily,
            rows.treasury_yield_2y_daily,
            rows.treasury_yield_5y_daily,
            rows.treasury_yield_7y_daily,
            rows.treasury_yield_10y_daily,
            rows.treasury_yield_30y_daily,
            rows.federal_funds_daily,
            rows.cpi_monthly,
            rows.inflation_yearly,
            rows.retail_sales_monthly,
            rows.durables_monthly,
            rows.unemployment_monthy,
            rows.nonfarm_payroll_monthly,
            # commodities
            rows.crude_oil_prices_wti_daily,
            rows.crude_oil_prices_brent_daily,
            rows.natural_gas_daily,
            rows.copper_monthly,
            rows.aluminum_monthly,
            rows.wheat_monthly,
            rows.corn_monthly,
            rows.cotten_monthly,
            rows.sugar_monthly,
            rows.coffee_monthly,
            rows.global_commodity_index_monthly,
            # fx_DXY
            rows.eur_usd_daily,
            rows.jpy_usd_daily,
            rows.gbp_usd_daily,
            rows.cad_usd_daily,
            rows.sek_usd_daily,
            rows.chf_usd_daily,
            # fx_BRICS
            rows.brl_usd_daily,
            rows.rub_usd_daily,
            rows.inr_usd_daily,
            rows.cny_usd_daily,
            rows.sar_usd_daily,
            rows.date_predict
        ]
        indicators_lst.append(indicators)

    for i in range(len(indicators_lst)):
        date_i = datetime.datetime.strptime(indicators_lst[i][0], "%Y-%m-%d")
        logger.log(logging.INFO, f"commiting daily feature for: {date_i}")
        d_i = Daily_feature_data(
            daily_feature_datetime_id=date_i,
            # economic idicators
            real_gdp_quarterly=indicators_lst[i][8],
            real_gdp_per_capita_quarterly=indicators_lst[i][9],
            treasury_yield_3m_daily=indicators_lst[i][10],
            treasury_yield_2y_daily=indicators_lst[i][11],
            treasury_yield_5y_daily=indicators_lst[i][12],
            treasury_yield_7y_daily=indicators_lst[i][13],
            treasury_yield_10y_daily=indicators_lst[i][14],
            treasury_yield_30y_daily=indicators_lst[i][15],
            federal_funds_daily=indicators_lst[i][16],
            cpi_monthly=indicators_lst[i][17],
            inflation_yearly=indicators_lst[i][18],
            retail_sales_monthly=indicators_lst[i][19],
            durables_monthly=indicators_lst[i][20],
            unemployment_monthy=indicators_lst[i][21],
            nonfarm_payroll_monthly=indicators_lst[i][22],
            # commodities
            crude_oil_prices_wti_daily=indicators_lst[i][23],
            crude_oil_prices_brent_daily=indicators_lst[i][24],
            natural_gas_daily=indicators_lst[i][25],
            copper_monthly=indicators_lst[i][26],
            aluminum_monthly=indicators_lst[i][27],
            wheat_monthly=indicators_lst[i][28],
            corn_monthly=indicators_lst[i][29],
            cotten_monthly=indicators_lst[i][30],
            sugar_monthly=indicators_lst[i][31],
            coffee_monthly=indicators_lst[i][32],
            global_commodity_index_monthly=indicators_lst[i][33],
            # fx_DXY
            eur_usd_daily=indicators_lst[i][34],
            jpy_usd_daily=indicators_lst[i][35],
            gbp_usd_daily=indicators_lst[i][36],
            cad_usd_daily=indicators_lst[i][37],
            sek_usd_daily=indicators_lst[i][38],
            chf_usd_daily=indicators_lst[i][39],
            # fx_BRICS
            brl_usd_daily=indicators_lst[i][40],
            rub_usd_daily=indicators_lst[i][41],
            inr_usd_daily=indicators_lst[i][42],
            cny_usd_daily=indicators_lst[i][43],
            sar_usd_daily=indicators_lst[i][44]
        )
        try:
            session.add(d_i)
        except:
            session.rollback()
            logger.log(logging.INFO, "database commit rollback")
        session.commit()
        session.close()
    logger.log(logging.INFO, "daily features committed")