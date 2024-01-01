# eth_daily_price_dag.py

from datetime import datetime, timedelta
import time
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

default_args = {
    'owner': 'feature-service',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'eth_daily_price_dag',
    default_args=default_args,
    schedule_interval='10 0 * * *',
    catchup=False
)


def eth_daily_price_to_db():

    from app.commit import current_datetime
    from app.get_data import eth_daily_price
    from app.feature_service_models import Daily_eth_price_data

    # delay function execution
    time.sleep(30)

    try:
        engine = create_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETH previous day price
        daily_datetime_input = current_datetime()[0] - timedelta(days=1)
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

    except Exception as e:
        session.rollback()


# PythonOperator to execute the function
call_api_task = PythonOperator(
    task_id='eth_daily_price_to_db_task',
    python_callable=eth_daily_price_to_db,
    dag=dag,
)

if __name__ == "__main__":
    dag.cli()
