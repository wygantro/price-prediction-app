from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
    return "Hello Airflow!"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'my_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
) as dag:
    start = DummyOperator(task_id='start')
    print_task = PythonOperator(task_id='print_hello', python_callable=print_hello)
    end = DummyOperator(task_id='end')

    start >> print_task >> end
