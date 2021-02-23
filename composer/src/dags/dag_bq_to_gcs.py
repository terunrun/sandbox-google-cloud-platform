"""BigQueryToCloudStorageOperatorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
import pendulum
from function import consts, utils

# DAG設定
DAG_NAME = 'dag_bq_to_gcs'
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
bq_to_gcs = BigQueryToCloudStorageOperator(
    task_id='bq_to_gcs',
    # export対象データセット.テーブル
    source_project_dataset_table=consts.WARM_DATASET + '.' + consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
    # export先オブジェクト名（uriなのでgs://形式で記述する）
    destination_cloud_storage_uris='gs://' + consts.TABLE_EXPORT_BUCKET + '/' + consts.FOLDER_NAME + '/' + consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}'
    # 圧縮形式
    compression='GZIP',
    # export形式
    export_format='CSV',
    # exportファイルにヘッダー行を含めるかどうか
    print_header=False,
    dag=dag,
)
