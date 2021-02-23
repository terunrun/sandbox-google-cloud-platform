"""xcomの値を削除するDAG"""
"""delete_xcom_const.pyのSQLを用途に合わせて修正すること"""

from datetime import datetime
from airflow import DAG
from airflow.operators.mysql_operator import MySqlOperator
import pendulum
from function import const_delete_xcom as consts

DAG_NAME = 'dag_delete_xcom'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, catchup=False, default_args=default_args)

# TASK設定
delete_xcom = MySqlOperator(
    task_id='delete_xcom',
    mysql_conn_id='airflow_db',
    sql=[consts.QUERY],
    dag=dag,
)
