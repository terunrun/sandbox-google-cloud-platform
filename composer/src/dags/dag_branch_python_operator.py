"""BranchPythonOperatorのサンプルDAG"""

import pendulum
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from datetime import datetime
from function import consts, utils

# DAG設定
DAG_NAME = 'dag_branch_python_operator'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args)

# TASK設定
set_execution_date_sample = BranchPythonOperator(
    task_id='set_execution_date_set_execution_date_sample',
    python_callable=utils.set_execution_date,
    templates_dict={
        'execute_task_id': ['execute_monthly', 'execute_monthly_2'],
    },
    provide_context=True,
    dag=dag,
)

# 呼び出し関数テスト用TASK
set_execution_date_invalid_data_name = BranchPythonOperator(
    task_id='set_execution_date_invalid_data_name',
    python_callable=utils.set_execution_date,
    templates_dict={
        'execute_task_id': ['execute_monthly', 'execute_monthly_2'],
    },
    provide_context=True,
    dag=dag,
)
set_execution_date_invalid_execute_task_id = BranchPythonOperator(
    task_id='set_execution_date_invalid_execute_task_id',
    python_callable=utils.set_execution_date,
    templates_dict={
        'execute_task_id': ['not_exist_task_1', 'not_exist_task_2'],
    },
    provide_context=True,
    dag=dag,
)
# 呼び出し関数テスト用TASK

# 呼び出し関数の判定動作確認用ダミーTASK
execute_monthly = DummyOperator(
    task_id='execute_monthly',
    dag=dag,
)
execute_monthly_2 = DummyOperator(
    task_id='execute_monthly_2',
    dag=dag,
)
dummy_task_for_skip = DummyOperator(
    task_id='dummy_task_for_skip',
    dag=dag,
)
# 呼び出し関数の判定動作確認用ダミーTASK

set_execution_date_sample >> [execute_monthly, execute_monthly_2, dummy_task_for_skip]
