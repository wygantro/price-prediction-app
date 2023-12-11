# eth_hour_price_dag.py

from datetime import datetime, timedelta
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.test_service_models import Hour_eth_price_data

# Define the default_args dictionary
default_args = {
    'owner': 'feature-service',
    'start_date': datetime(2023, 1, 1, 0, 1, 0),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# define the DAG
dag = DAG(
    'eth_hour_price_dag',
    default_args=default_args,
    schedule_interval='0 * * * *',
    catchup=False
)

# define a function to call the API and save data to the database
def eth_hour_price_to_db():

    from app.commit import current_datetime
    from app.get_data import eth_hour_price

    try:
        engine = create_engine('postgresql://user:postgres@172.30.192.3:5432/test-service-db')
        Session = sessionmaker(bind=engine)
        session = Session()

        # get eth hour price
        eth_hour_price = eth_hour_price(current_datetime()[1])

        new_data = Hour_eth_price_data(
            hour_datetime_id=current_datetime()[1],
            # daily_id=current_datetime()[0],
            eth_hour_price_open=eth_hour_price[1],
            eth_hour_price_close=eth_hour_price[2],
            eth_hour_price_high=eth_hour_price[3],
            eth_hour_price_low=eth_hour_price[4],
            eth_hour_price_vol=eth_hour_price[5],
            eth_hour_price_vol_weight_avg=eth_hour_price[6]
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
    task_id='eth_hour_price_to_db_task',
    python_callable=eth_hour_price_to_db,
    dag=dag,
)

if __name__ == "__main__":
    dag.cli()
