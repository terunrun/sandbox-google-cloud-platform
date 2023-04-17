"""Cloud StorageのデータをBigQueryへロードするフローだけを記載したDAG"""

from airflow import DAG

from airflow.contrib.sensors.gcs_sensor import GoogleCloudStoragePrefixSensor
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.gcs_to_gcs import GoogleCloudStorageToGoogleCloudStorageOperator
from airflow.models import Variable
from airflow.models import XCom
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from datetime import datetime, timedelta, timezone
from function import consts, utils
import pendulum

# DAG設定
DAG_NAME = 'workflow_sample'
# 各Taskに共通させたい設定
default_args = {
    'owner': 'terunrun',
    # 前回実行結果に依存するかどうか（True:依存する=前回分が正常終了なら今回分を実行する）
    'depends_on_past': False,
    # スケジュール開始したい実日付-1日を設定する
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}
# スケジュール起動させる場合
# dag = DAG(DAG_NAME, schedule_interval='@daily', default_args=default_args, catchup=False)
# スケジュール起動させない場合
dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args, catchup=False)

# TASK設定
# 処理を実行するかどうかを判定
set_execution_date = BranchPythonOperator(
    task_id='set_execution_date',
    python_callable=utils.set_execution_date,
    templates_dict={
        'data_name': consts.DATA_NAME,
        'execute_task_id_1': 'sensor_csv',
        'execute_task_id_2': 'dummy',
    },
    provide_context=True,
    dag=dag,
)
# CloudStorageのCSVファイルを監視
sensor_csv = DummyOperator(
    task_id='sensor_csv',
    dag=dag,
)

# CloudStorageのCSVファイルを前回分と比較
compare_csv = DummyOperator(
    task_id='compare_csv',
    dag=dag,
)

# CloudStorageのCSVファイルをBigQueryのimportデータセットへロード
load_csv = DummyOperator(
    task_id='load_csv',
    dag=dag,
)

# BigQueryのimportデータセットへクエリ発行し、結果をcoldデータセットへ格納
create_cold = DummyOperator(
    task_id='create_cold',
    dag=dag,
)

# coldデータセットをCloudStorageへ抽出
extract_cold = DummyOperator(
    task_id='extract_cold',
    dag=dag,
)

# CloudStorageのCSVファイルを別バケットへ退避
backup_csv = DummyOperator(
    task_id='backup_csv',
    dag=dag,
)

# CloudStorageのCSVファイルを削除
delete_csv = DummyOperator(
    task_id='delete_csv',
    # 先行Taskが失敗またはスキップでない場合は実行する設定
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# 別のDAGを実行する
trigger_dag = DummyOperator(
    task_id='trigger_dag',
    dag=dag,
)

# 処理実行判定処理でスキップとなった場合に実行するダミー
dummy = DummyOperator(
    task_id='dummy',
    dag=dag,
)

# 処理フロー設定
set_execution_date >> sensor_csv >> compare_csv >> [load_csv, delete_csv]
load_csv >> create_cold >> [extract_cold, backup_csv, trigger_dag, ]
backup_csv >> delete_csv

# 処理実行判定からダミーへのフロー
set_execution_date >> dummy
