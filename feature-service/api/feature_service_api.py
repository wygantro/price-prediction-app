# ./feature_service_api.py

from flask import Flask, jsonify
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f'Hello, World! Current time is {current_time}'


# Macro Economic Feature Data
@app.route('/feature-data-daily', methods=['GET'])
def feature_data_daily_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime, commit_daily_features
    from app.get_data import daily_features

    time.sleep(30)

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get minute price
        daily_datetime_input = current_datetime()[0] #- timedelta(days=1)
        daily_feature_data = daily_features(daily_datetime_input)

        commit_daily_features(session, daily_datetime_input, daily_feature_data)

        return jsonify({'message': f'Feature Data requested, processed, and committed to database successfully at {daily_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


# BTC Price Data
@app.route('/btc-minute', methods=['GET'])
def btc_minute_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import minute_price
    from app.feature_service_models import Minute_price_data

    time.sleep(20)

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETC previous minute price
        minute_datetime_input = current_datetime()[2] - timedelta(minutes=1)
        btc_minute_price_data = minute_price(minute_datetime_input)

        new_data = Minute_price_data(
            minute_datetime_id=minute_datetime_input,
            #hour_id=current_datetime()[1], # hour_id for minute_price table
            #daily_id=current_datetime()[0], # daily_id for minute_price table
            btc_minute_price_open=btc_minute_price_data[1],
            btc_minute_price_close=btc_minute_price_data[2],
            btc_minute_price_high=btc_minute_price_data[3],
            btc_minute_price_low=btc_minute_price_data[4],
            btc_minute_price_vol=btc_minute_price_data[5],
            btc_minute_price_vol_weight_avg=btc_minute_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Minute BTC Price Data ({btc_minute_price_data[2]}) requested, processed, and committed to database successfully at {minute_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


@app.route('/btc-hour', methods=['GET'])
def btc_hour_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import hour_price
    from app.feature_service_models import Hour_price_data

    time.sleep(10)

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get BTC previous hour price
        hour_datetime_input = current_datetime()[1] #- timedelta(hours=1)
        btc_hour_price_data = hour_price(hour_datetime_input)

        new_data = Hour_price_data(
            hour_datetime_id=hour_datetime_input,
            #daily_id=current_datetime()[0], # daily_id for hour_price table
            btc_hour_price_open=btc_hour_price_data[1],
            btc_hour_price_close=btc_hour_price_data[2],
            btc_hour_price_high=btc_hour_price_data[3],
            btc_hour_price_low=btc_hour_price_data[4],
            btc_hour_price_vol=btc_hour_price_data[5],
            btc_hour_price_vol_weight_avg=btc_hour_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Hour BTC Price Data ({btc_hour_price_data[2]}) requested, processed, and committed to database successfully at {hour_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


@app.route('/btc-daily', methods=['GET'])
def btc_daily_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import daily_price
    from app.feature_service_models import Daily_price_data

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get BTC previous daily price
        daily_datetime_input = current_datetime()[0] #- timedelta(days=1)
        btc_daily_price_data = daily_price(daily_datetime_input)

        new_data = Daily_price_data(
            daily_datetime_id=daily_datetime_input,
            btc_daily_price_open=btc_daily_price_data[1],
            btc_daily_price_close=btc_daily_price_data[2],
            btc_daily_price_high=btc_daily_price_data[3],
            btc_daily_price_low=btc_daily_price_data[4],
            btc_daily_price_vol=btc_daily_price_data[5],
            btc_daily_price_vol_weight_avg=btc_daily_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Daily BTC Price Data ({btc_daily_price_data[2]}) requested, processed, and committed to database successfully at {daily_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


# ETH Price Data
@app.route('/eth-minute', methods=['GET'])
def eth_minute_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import eth_minute_price
    from app.feature_service_models import Minute_eth_price_data

    time.sleep(20)

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETH previous minute price
        minute_datetime_input = current_datetime()[2] - timedelta(minutes=1)
        eth_minute_price_data = eth_minute_price(minute_datetime_input)

        new_data = Minute_eth_price_data(
            minute_datetime_id=minute_datetime_input,
            eth_minute_price_open=eth_minute_price_data[1],
            eth_minute_price_close=eth_minute_price_data[2],
            eth_minute_price_high=eth_minute_price_data[3],
            eth_minute_price_low=eth_minute_price_data[4],
            eth_minute_price_vol=eth_minute_price_data[5],
            eth_minute_price_vol_weight_avg=eth_minute_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Minute ETH Price Data ({eth_minute_price_data[2]}) requested, processed, and committed to database successfully at {minute_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


@app.route('/eth-hour', methods=['GET'])
def eth_hour_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import eth_hour_price
    from app.feature_service_models import Hour_eth_price_data

    time.sleep(10)

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETH previous hour price
        hour_datetime_input = current_datetime()[1] #- timedelta(hours=1)
        eth_hour_price_data = eth_hour_price(hour_datetime_input)

        new_data = Hour_eth_price_data(
            hour_datetime_id=hour_datetime_input,
            eth_hour_price_open=eth_hour_price_data[1],
            eth_hour_price_close=eth_hour_price_data[2],
            eth_hour_price_high=eth_hour_price_data[3],
            eth_hour_price_low=eth_hour_price_data[4],
            eth_hour_price_vol=eth_hour_price_data[5],
            eth_hour_price_vol_weight_avg=eth_hour_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Hour ETH Price Data ({eth_hour_price_data[2]}) requested, processed, and committed to database successfully at {hour_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


@app.route('/eth-daily', methods=['GET'])
def eth_daily_price_to_db():

    from app.connect_db import connect_url
    from app.commit import current_datetime
    from app.get_data import eth_daily_price
    from app.feature_service_models import Daily_eth_price_data

    try:
        db_url = connect_url('feature-service')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETH previous daily price
        daily_datetime_input = current_datetime()[0] #- timedelta(days=1)
        eth_daily_price_data = eth_daily_price(daily_datetime_input)

        new_data = Daily_eth_price_data(
            daily_datetime_id=daily_datetime_input,
            eth_daily_price_open=eth_daily_price_data[1],
            eth_daily_price_close=eth_daily_price_data[2],
            eth_daily_price_high=eth_daily_price_data[3],
            eth_daily_price_low=eth_daily_price_data[4],
            eth_daily_price_vol=eth_daily_price_data[5],
            eth_daily_price_vol_weight_avg=eth_daily_price_data[6]
        )
        session.add(new_data)
        session.commit()
        session.close()

        return jsonify({'message': f'Daily ETH Price Data ({eth_daily_price_data[2]}) requested, processed, and committed to database successfully at {daily_datetime_input}'}), 200
    except Exception as e:
        session.rollback()

        return jsonify({'error': f'{e}'}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')