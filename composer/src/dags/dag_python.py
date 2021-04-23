"""PythonOperatorでmacrosを調べるDAG"""

from datetime import datetime, timezone
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
import pendulum
from function import utils

# DAG設定
DAG_NAME = 'dag_macros'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args, catchup=False)

# get_today_op_args = PythonOperator(
#     task_id='get_today_op_args',
#     python_callable=util.get_today_op_args,
#     op_args=['{{ execution_date }}',],
#     # provide_context=-True,
#     dag=dag,
# )

get_today_op_kwargs = PythonOperator(
    task_id='get_today_op_kwargs',
    python_callable=utils.get_templates_dict,
    op_kwargs={
        'ds': '{{ ds }}',
        'ds_nodash': '{{ ds_nodash }}',
        'prev_ds': '{{ prev_ds }}',
        'prev_ds_nodash': '{{ prev_ds_nodash }}',
        'next_ds': '{{ next_ds }}',
        'next_ds_nodash': '{{ next_ds_nodash }}',
        'yesterday_ds': '{{ yesterday_ds }}',
        'yesterday_ds_nodash': '{{ yesterday_ds_nodash }}',
        'tomorrow_ds': '{{ tomorrow_ds }}',
        'tomorrow_ds_nodash': '{{ tomorrow_ds_nodash }}',
        'ts': '{{ ts }}',
        # 'ts': '{{ ts + macros.timedelta(hours=+9) }}',
        'ts_nodash': '{{ ts_nodash }}',
        'ts_nodash_with_tz': '{{ ts_nodash_with_tz }}',
        'execution_date': '{{ execution_date }}',
        'execution_date+9_ymd': Variable.get('today') if Variable.get('today') else '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'prev_execution_date': '{{ prev_execution_date }}',
        'prev_execution_date_success': '{{ prev_execution_date_success }}',
        'prev_start_date_success': '{{ prev_start_date_success }}',
        'next_execution_date': '{{ next_execution_date }}',
        # 'dag': '{{ dag }}',
        # 'task': '{{ task }}',
        # 'macros': '{{ macros }}',
        # 'task_instance': '{{ task_instance }}',
        # 'end_date': '{{ end_date }}',
        # 'latest_date': '{{ latest_date }}',
        # 'ti': '{{ ti }}',
        # 'params': '{{ params }}',
        # 'var.value.my_var': '{{ var.value.my_var }}',
        # 'var.json.my_var.path': '{{ var.json.my_var.path }}',
        # 'task_instance_key_str': '{{ task_instance_key_str }}',
        # 'conf': '{{ conf }}',
        # 'run_id': '{{ run_id }}',
        # 'dag_run': '{{ dag_run }}',
        # 'test_mode': '{{ test_mode }}',
    },
    # provide_context=-True,
    dag=dag,
)
