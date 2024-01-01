# ./app/get_data.py

import logging


def daily_date_range(logger, start_date, end_date):
    """
    Calculates a list of datetime objects over a start and end date. Then 
    stores and returns ordered objects in a single list.

    Args:
        logger (logging.Logger): Initialized logger object
        start_date (datetime.datetime): Start date reference datetime
        object end_date (datetime.datetime): End date reference datetime
        object

    Returns:
        lst: Ordered list of datetime (year, month, day) objects.
    """
    import pandas as pd

    # define range and return list of datetime objects
    range = end_date - start_date
    logger.log(
        logging.INFO,
        f"""initializing daily date range: {start_date} to {end_date}
        (range = {range.days} days)""")
    date_range_lst = pd.date_range(start_date, periods=range.days)

    return date_range_lst


def daily_price(logger, date_daily):
    """
    Connect to daily price API and return daily price data.

    This function takes input logger and daily datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return daily price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_daily (datetime.datetime): Daily datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests

    logger.log(logging.INFO, f"getting daily price data for: {date_daily}")
    date = date_daily.strftime("%Y-%m-%d")

    # connect to polygon.io and get daily price data
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/global/market/crypto/{date}?adjusted=true&apiKey={polygon_api_key}"
    r = requests.get(url)

    # get date from api call
    data = r.json()['results']
    unix_time = data[0]['t'] / 1000
    api_date = datetime.datetime.utcfromtimestamp(
        unix_time).replace(hour=0, minute=0, second=0, microsecond=0)
    btc_daily_price_info = list(
        filter(lambda ticker_info: ticker_info['T'] == 'X:BTCUSD', data))
    btc_price_results_lst = [api_date,
                             btc_daily_price_info[0]['o'],
                             btc_daily_price_info[0]['c'],
                             btc_daily_price_info[0]['h'],
                             btc_daily_price_info[0]['l'],
                             btc_daily_price_info[0]['v'],
                             btc_daily_price_info[0]['vw']]
    logger.log(
        logging.INFO, f"successful daily request price data for: {date}")

    return btc_price_results_lst


def daily_features(logger, date_daily):
    """
    Connect to daily price API and return daily price features.

    This function takes input logger and daily datetime reference object. 
    Then takes a datetime object ID input to connect with AlphaVantage API and 
    return feature values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_daily (datetime.datetime): Daily datetime object timestamp 

    Returns: None
    """
    import json
    import requests

    logger.log(logging.INFO, f"getting daily feature data for: {date_daily}")
    file_path = './data/api_reference.txt'
    with open(file_path, 'r') as json_file:
        api_dict = json.load(json_file)

    daily_feature_data_dict = {}
    for metric, url in api_dict.items():
        r = requests.get(url)
        try:
            data = r.json()['data'][0]['value']
            daily_feature_data_dict.update({metric: data})
        except KeyError:
            # handle first KeyError
            logger.log(logging.ERROR,
                       f"daily feature function first KeyError")
            try:
                date_string = date_daily.strftime("%Y-%m-%d")
                data = r.json()[
                    'Time Series FX (Daily)'][date_string]['1. open']
                daily_feature_data_dict.update({metric: data})
            except KeyError:
                # handle second KeyError
                logger.log(logging.ERROR,
                           f"daily feature function second KeyError")
                fx_data_dict = r.json()['Time Series FX (Daily)']
                date_key = next(iter(fx_data_dict))
                fx_data_dict = r.json()['Time Series FX (Daily)']
                data_key = fx_data_dict[date_key]['4. close']
                daily_feature_data_dict.update({metric: data_key})

    return daily_feature_data_dict


def hour_price(logger, date_hour, next_url=None):
    """
    Connect to hourly price API and return hourly price data.

    This function takes input logger and hourly datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return hourly price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_hour (datetime.datetime): Hourly datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests
    import time

    logger.log(logging.INFO, f"getting hour price data for: {date_hour}")
    date = date_hour.strftime("%Y-%m-%d")

    # initial api hour price call
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/hour/{date}/{date}?adjusted=true&sort=asc&limit=120&apiKey={polygon_api_key}"
    r = requests.get(url)
    data = r.json()

    # check api index
    try:
        api_datetime_0 = datetime.datetime.utcfromtimestamp(
            int(data['results'][0]['t']) / 1000.0)
        api_datetime_1 = datetime.datetime.utcfromtimestamp(
            int(data['results'][1]['t']) / 1000.0)
    except IndexError:
        api_datetime_1 = None

    # while loop over API datetime values and search for price data
    while api_datetime_0 != date_hour or api_datetime_1 != date_hour:
        if api_datetime_0 == date_hour:
            price_results_lst = [api_datetime_0,
                                 data['results'][0]['o'],
                                 data['results'][0]['c'],
                                 data['results'][0]['h'],
                                 data['results'][0]['l'],
                                 data['results'][0]['v'],
                                 data['results'][0]['vw']]
            break

        elif api_datetime_1 == date_hour:
            price_results_lst = [api_datetime_1,
                                 data['results'][1]['o'],
                                 data['results'][1]['c'],
                                 data['results'][1]['h'],
                                 data['results'][1]['l'],
                                 data['results'][1]['v'],
                                 data['results'][1]['vw']]
            break
        else:
            try:
                next_url = data['next_url']
            except KeyError:
                next_url = None

            url = f"{next_url}&apiKey={polygon_api_key}"
            r = requests.get(url)
            data = r.json()
            # check api index
            try:
                api_datetime_0 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][0]['t']) / 1000.0)
                api_datetime_1 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][1]['t']) / 1000.0)
            except IndexError:
                api_datetime_1 = None
        time.sleep(0.1)

    return price_results_lst


def hour_features(logger, date_hour, next_url=None):
    """
    Connect to hourly price API and return hourly price features.

    This function takes input logger and hourly datetime reference object. 
    Then takes a datetime object ID input to connect with AlphaVantage API and 
    return feature values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_hour (datetime.datetime): Hourly datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests
    import time

    logger.log(logging.INFO, f"getting hour feature data for: {date_hour}")
    date = date_hour.strftime("%Y-%m-%d")

    # initial api hour price call
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/hour/{date}/{date}?adjusted=true&sort=asc&limit=120&apiKey={polygon_api_key}"
    r = requests.get(url)
    data = r.json()
    # check api index
    try:
        api_datetime_0 = datetime.datetime.utcfromtimestamp(
            int(data['results'][0]['t']) / 1000.0)
        api_datetime_1 = datetime.datetime.utcfromtimestamp(
            int(data['results'][1]['t']) / 1000.0)
    except IndexError:
        api_datetime_1 = None

    while api_datetime_0 != date_hour or api_datetime_1 != date_hour:
        if api_datetime_0 == date_hour:
            price_results_lst = [api_datetime_0,
                                 data['results'][0]['o'],
                                 data['results'][0]['c'],
                                 data['results'][0]['h'],
                                 data['results'][0]['l'],
                                 data['results'][0]['v'],
                                 data['results'][0]['vw']]
            break

        elif api_datetime_1 == date_hour:
            price_results_lst = [api_datetime_1,
                                 data['results'][1]['o'],
                                 data['results'][1]['c'],
                                 data['results'][1]['h'],
                                 data['results'][1]['l'],
                                 data['results'][1]['v'],
                                 data['results'][1]['vw']]
            break

        else:
            try:
                next_url = data['next_url']
            except KeyError:
                next_url = None

            url = f"{next_url}&apiKey={polygon_api_key}"
            r = requests.get(url)
            data = r.json()
            # check api index
            try:
                api_datetime_0 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][0]['t']) / 1000.0)
                api_datetime_1 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][1]['t']) / 1000.0)
            except IndexError:
                api_datetime_1 = None
        time.sleep(0.1)

    return price_results_lst


def minute_price(logger, date_minute, next_url=None):
    """
    Connect to minute price API and return minute price data.

    This function takes input logger and minute datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return minute price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_minute (datetime.datetime): Minute datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests

    logger.log(logging.INFO, f"getting minute price data for: {date_minute}")
    date_input = date_minute
    date = date_input.strftime("%Y-%m-%d")

    # connect to polygon.io and get minute price data
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/minute/{date}/{date}?adjusted=true&sort=asc&limit=5000&apiKey={polygon_api_key}"
    r = requests.get(url)
    data = r.json()

    api_datetime_minute = datetime.datetime.utcfromtimestamp(
        int(data['results'][-1]['t']) / 1000.0)

    price_minute_results_lst = [api_datetime_minute,
                                data['results'][-1]['o'],
                                data['results'][-1]['c'],
                                data['results'][-1]['h'],
                                data['results'][-1]['l'],
                                data['results'][-1]['v'],
                                data['results'][-1]['vw']]

    return price_minute_results_lst


#### ETH price data ####
def eth_daily_price(date_daily):
    """
    Connect to daily price API and return daily price data.

    This function takes input logger and daily datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return daily price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_daily (datetime.datetime): Daily datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests

    # logger.log(logging.INFO, f"getting daily price data for: {date_daily}")
    date = date_daily.strftime("%Y-%m-%d")

    # connect to polygon.io and get daily price data
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/global/market/crypto/{date}?adjusted=true&apiKey={polygon_api_key}"
    r = requests.get(url)

    # get date from api call
    data = r.json()['results']
    unix_time = data[0]['t'] / 1000
    api_date = datetime.datetime.utcfromtimestamp(
        unix_time).replace(hour=0, minute=0, second=0, microsecond=0)
    eth_daily_price_info = list(
        filter(lambda ticker_info: ticker_info['T'] == 'X:ETHUSD', data))
    eth_price_results_lst = [api_date,
                             eth_daily_price_info[0]['o'],
                             eth_daily_price_info[0]['c'],
                             eth_daily_price_info[0]['h'],
                             eth_daily_price_info[0]['l'],
                             eth_daily_price_info[0]['v'],
                             eth_daily_price_info[0]['vw']]
    # logger.log(
    #     logging.INFO, f"successful daily request price data for: {date}")

    return eth_price_results_lst


def eth_hour_price(date_hour, next_url=None):
    """
    Connect to hourly price API and return hourly price data.

    This function takes input logger and hourly datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return hourly price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_hour (datetime.datetime): Hourly datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests
    import time

    # logger.log(logging.INFO, f"getting hour price data for: {date_hour}")
    date = date_hour.strftime("%Y-%m-%d")

    # initial api hour price call
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/ticker/X:ETHUSD/range/1/hour/{date}/{date}?adjusted=true&sort=asc&limit=120&apiKey={polygon_api_key}"
    r = requests.get(url)
    data = r.json()

    # check api index
    try:
        api_datetime_0 = datetime.datetime.utcfromtimestamp(
            int(data['results'][0]['t']) / 1000.0)
        api_datetime_1 = datetime.datetime.utcfromtimestamp(
            int(data['results'][1]['t']) / 1000.0)
    except IndexError:
        api_datetime_1 = None

    # while loop over API datetime values and search for hour price data
    while api_datetime_0 != date_hour or api_datetime_1 != date_hour:
        if api_datetime_0 == date_hour:
            price_results_lst = [api_datetime_0,
                                 data['results'][0]['o'],
                                 data['results'][0]['c'],
                                 data['results'][0]['h'],
                                 data['results'][0]['l'],
                                 data['results'][0]['v'],
                                 data['results'][0]['vw']]
            break

        elif api_datetime_1 == date_hour:
            price_results_lst = [api_datetime_1,
                                 data['results'][1]['o'],
                                 data['results'][1]['c'],
                                 data['results'][1]['h'],
                                 data['results'][1]['l'],
                                 data['results'][1]['v'],
                                 data['results'][1]['vw']]
            break
        else:
            try:
                next_url = data['next_url']
            except KeyError:
                next_url = None

            url = f"{next_url}&apiKey={polygon_api_key}"
            r = requests.get(url)
            data = r.json()
            # check api index
            try:
                api_datetime_0 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][0]['t']) / 1000.0)
                api_datetime_1 = datetime.datetime.utcfromtimestamp(
                    int(data['results'][1]['t']) / 1000.0)
            except IndexError:
                api_datetime_1 = None
        time.sleep(0.1)

    return price_results_lst


def eth_minute_price(date_minute, next_url=None):
    """
    Connect to minute price API and return minute price data.

    This function takes input logger and minute datetime reference object. 
    Then takes a datetime object ID input to connect with polygon.io API and 
    return minute price values as list.

    Args:
        logger (logging.Logger): Initialized logger object
        date_minute (datetime.datetime): Minute datetime object timestamp 

    Returns: None
    """
    import datetime
    import os
    import requests

    # logger.log(logging.INFO, f"getting minute price data for: {date_minute}")
    date_input = date_minute
    date = date_input.strftime("%Y-%m-%d")

    # connect to polygon.io and get minute price data
    polygon_api_key = os.environ["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/aggs/ticker/X:ETHUSD/range/1/minute/{date}/{date}?adjusted=true&sort=asc&limit=5000&apiKey={polygon_api_key}"
    r = requests.get(url)
    data = r.json()

    api_datetime_minute = datetime.datetime.utcfromtimestamp(
        int(data['results'][-1]['t']) / 1000.0)

    price_minute_results_lst = [api_datetime_minute,
                                data['results'][-1]['o'],
                                data['results'][-1]['c'],
                                data['results'][-1]['h'],
                                data['results'][-1]['l'],
                                data['results'][-1]['v'],
                                data['results'][-1]['vw']]

    return price_minute_results_lst
