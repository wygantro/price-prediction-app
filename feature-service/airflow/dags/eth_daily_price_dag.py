# eth_daily_price_dag.py

from datetime import datetime, timedelta
import time
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# define the default_args dictionary
default_args = {
    'owner': 'feature-service',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# define the DAG
dag = DAG(
    'eth_daily_price_dag',
    default_args=default_args,
    schedule_interval='10 1 * * *',
    #schedule_interval='@daily',
    catchup=False,
)

# define a function to call the API and save data to the database
def eth_daily_price_to_db():

    from app.commit import current_datetime
    from app.get_data import eth_daily_price
    from app.test_service_models import Daily_eth_price_data

    # delay function execution
    time.sleep(10)

    try:
        engine = create_engine('postgresql://user:postgres@172.30.192.3:5432/test-service-db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # get eth hour price
        eth_daily_price = eth_daily_price(current_datetime()[0])

        new_data = Daily_eth_price_data(
            daily_datetime_id=current_datetime()[0],
            eth_daily_price_open=eth_daily_price[1],
            eth_daily_price_close=eth_daily_price[2],
            eth_daily_price_high=eth_daily_price[3],
            eth_daily_price_low=eth_daily_price[4],
            eth_daily_price_vol=eth_daily_price[5],
            eth_daily_price_vol_weight_avg=eth_daily_price[6]
            )
        session.add(new_data)
        session.commit()
        session.close()
        print("Data saved to database successfully")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        print("Transaction rolled back")

# define a PythonOperator to execute the function
call_api_task = PythonOperator(
    task_id='eth_daily_price_to_db_task',
    python_callable=eth_daily_price_to_db,
    dag=dag,
)

if __name__ == "__main__":
    dag.cli()
