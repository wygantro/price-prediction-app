# eth_hour_price_dag.py

from datetime import datetime, timedelta
import time
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
    'eth_hour_price_dag',
    default_args=default_args,
    schedule_interval='1 * * * *',
    catchup=False
)


def eth_hour_price_to_db():

    from app.commit import current_datetime
    from app.get_data import eth_hour_price
    from app.feature_service_models import Hour_eth_price_data

    # delay execution
    time.sleep(20)

    try:
        engine = create_engine(
            'postgresql://user:postgres@172.30.192.3:5432/feature-service-db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # get ETH previous hour price
        hour_datetime_input = current_datetime()[1] - timedelta(hours=1)
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

    except Exception as e:
        session.rollback()


call_api_task = PythonOperator(
    task_id='eth_hour_price_to_db_task',
    python_callable=eth_hour_price_to_db,
    dag=dag,
)

if __name__ == "__main__":
    dag.cli()
