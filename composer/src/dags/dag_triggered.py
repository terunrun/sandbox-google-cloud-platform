"""TriggerDagRunOperatorからトリガーされるサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import pendulum

# DAG設定
DAG_NAME = 'dag_triggered'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args, catchup=False)

triggered = BashOperator(
    task_id='triggered',
    # trigger元から渡された値を取得して表示する
    bash_command='echo {}'.format('{{dag_run.conf.closing_date}}'),
    dag=dag,
)
