"""BigQueryへクエリ発行する独自関数を実行するサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pendulum
from function import consts, utils

TODAY = '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}'

# DAG設定
DAG_NAME = 'dag_run_query'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': False,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
}
dag = DAG(DAG_NAME,
          schedule_interval=None,
          default_args=default_args,
          catchup=False)

# TASK設定
run_bq_query = PythonOperator(
    task_id='run_bq_query',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        # 'query_param_values': {'target_date': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}'},
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        # FIXME:パーティションを使用する場合はコメントアウトを外す
        # 'time_partitioning': 'performance_management_year_monthly',
        'time_partitioning': '',
        # 'cluster_fields': ['reference_date'],
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

# 呼び出し関数テスト用TASK
run_bq_query_invalid_destination_dataset = PythonOperator(
    task_id='run_bq_query_invalid_destination_dataset',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': 12345,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_destination_table = PythonOperator(
    task_id='run_bq_query_invalid_destination_table',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': '',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_write_disposition = PythonOperator(
    task_id='run_bq_query_write_disposition',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 12345,
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_create_disposition = PythonOperator(
    task_id='run_bq_query_invalid_create_disposition',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 12345,
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_query_param_values = PythonOperator(
    task_id='run_bq_query_invalid_query_param_values',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': {'invalid_param': 12345},
        'time_partitioning': '',
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_time_partitioning = PythonOperator(
    task_id='run_bq_query_invalid_time_partitioning',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}'},}],
        'time_partitioning': 12345,
        'cluster_fields': [],
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

create_raw_invalid_time_partitioning = PythonOperator(
    task_id='create_raw_invalid_time_partitioning',
    python_callable=util.run_bq_query,
    templates_dict={
        'data_name': const.RAW_PREFIX + const.DATA_NAME_SAMPLE,
        'destination_dataset': const.RAW_DATASET,
        'destination_table': const.RAW_PREFIX + 'destination_table',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': {'reference_date': '201903'},
        'time_partitioning': 12345,
        'cluster_fields': [],
        'location': 'US',
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_cluster_fields = PythonOperator(
    task_id='run_bq_query_invalid_cluster_fields',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        # クラスタリングカラムはどんな値でもエラーにならない
        'cluster_fields': {'cluster_field': 12345},
        'location': const.BASE_LOCATION,
    },
    provide_context=True,
    dag=dag,
)

run_bq_query_invalid_location = PythonOperator(
    task_id='run_bq_query_invalid_location',
    python_callable=utils.run_bq_query,
    templates_dict={
        'data_name': const.DATA_NAME,
        'destination_dataset': const.WARM_DATASET,
        'destination_table': consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
        'write_disposition': 'WRITE_TRUNCATE',
        'create_disposition': 'CREATE_IF_NEEDED',
        'query_param_values': [{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },}],
        'time_partitioning': '',
        'cluster_fields': [],
        'location': 12345,
    },
    provide_context=True,
    dag=dag,
)
# 呼び出し関数テスト用TASK
