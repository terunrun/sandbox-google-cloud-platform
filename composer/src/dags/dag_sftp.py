"""SFTPOperatorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.contrib.operators.sftp_operator import SFTPOperator
import pendulum

# DAG設定
DAG_NAME = 'dag_sftp'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args, catchup=False)

sftp = SFTPOperator(
    task_id='sftp',
    # 接続先等を記述したconnectionをaiflowに登録しておく必要がある
    ssh_conn_id='test_connection',
    # remote_host='',
    local_filepath='/tmp/test/test.txt',
    remote_filepath='/home/ubuntu/test.txt',
    operation='GET',
    # confirm=,
    create_intermediate_dirs=True,
    dag=dag,
)
