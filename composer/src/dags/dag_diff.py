"""二つのファイルを比較し、差分有無によって次に実行するTASKを決定するDAG"""


from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
import pendulum
from function import consts, utils

# DAG設定
DAG_NAME = 'dag_diff'
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

# 単純に比較するだけならbashコマンドも使える。
# BashOperaorはコマンド実行結果をxcomに格納する。
# bash_diff = BashOperator(
#     task_id='bash_diff',
#     bash_command = 'diff /home/airflow/gcs/data/backup/test_2.csv.csv /home/airflow/gcs/data/test_1.csv.csv',
#     dag=dag,
# )

diff = BranchPythonOperator(
    task_id='diff',
    python_callable=utils.diff,
    templates_dict={
        'category': 'test',
        'files':['test_1.csv', 'test_2.csv'],
        'next_task_ids_when_no_diff': ['next_task_when_diff']
        'next_task_ids_when_no_diff': ['next_task_when_no_diff']
    },
    provide_context=True,
    dag=dag,
)

next_task_when_diff = DummyOperator(
    task_id='next_task_when_diff',
    dag=dag,
)

next_task_when_no_diff = DummyOperator(
    task_id='next_task_when_no_diff',
    dag=dag,
)

diff >> [next_task_when_diff, next_task_when_no_diff]
