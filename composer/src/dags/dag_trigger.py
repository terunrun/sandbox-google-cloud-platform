"""TriggerDagRunOperatorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
import pendulum
from function import consts, utils

# DAG設定
DAG_NAME = 'dag_trigger'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args, catchup=False)

# TASK設定
trigger_dag = TriggerDagRunOperator(
    task_id='trigger_dag',
    # トリガー前に実行する関数を指定
    python_callable=utils.push_value,
    # 実行する関数に渡すパラメータを指定
    params={'key': 'value'},
    # トリガーするDAGを指定
    trigger_dag_id='dag_triggered_dag',
    # トリガーするexecution_dateを指定
    execution_date='{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
    dag=dag,
)
