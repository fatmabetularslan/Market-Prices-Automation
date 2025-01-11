from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Adana, Mersin ve Kocaeli dosyalarını çalıştıracak fonksiyonlar
def run_adana_py():
    subprocess.run(["python3", "/opt/airflow/dags/ADANA.py"], check=True)

def run_mersin_py():
    subprocess.run(["python3", "/opt/airflow/dags/MERSİN.py"], check=True)

def run_kocaeli_py():
    subprocess.run(["python3", "/opt/airflow/dags/KOCAELİ.py"], check=True)
def run_izmirpy():
    subprocess.run(["python3", "/opt/airflow/dags/izmir.py"], check=True)
# Varsayılan ayarlar (retry, başlangıç tarihi vs.)
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 24),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG'in tanımlanması
dag = DAG(
    'hal_fiyatlari_dag',
    default_args=default_args,
    description='Adana, Mersin, İzmir ve Kocaeli hal fiyatlarını otomatik çekme',
    schedule_interval='@daily',  # Her gün çalışacak
)

# PythonOperator ile Adana, Mersin ve Kocaeli dosyalarını çalıştırma
run_adana_task = PythonOperator(
    task_id='run_adana_py',
    python_callable=run_adana_py,
    dag=dag,
)

run_mersin_task = PythonOperator(
    task_id='run_mersin_py',
    python_callable=run_mersin_py,
    dag=dag,
)

run_kocaeli_task = PythonOperator(
    task_id='run_kocaeli_py',
    python_callable=run_kocaeli_py,
    dag=dag,
)
run_izmir_task = PythonOperator(
    task_id='run_izmir_py',
    python_callable=run_izmir_py,
    dag=dag,
)
# Task'lerin sırası (önce Adana, sonra Mersin, sonra Kocaeli)
run_adana_task >> run_mersin_task >> run_kocaeli_task>> run_izmir_task

