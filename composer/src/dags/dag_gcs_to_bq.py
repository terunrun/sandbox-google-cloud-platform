"""GoogleCloudStorageToBigQueryOperatorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
import pendulum
from function import consts

# DAG設定
DAG_NAME = 'dag_gcs_to_bq'
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
load = GoogleCloudStorageToBigQueryOperator(
    task_id='load',
    # ロードするファイルの格納バケット
    bucket=consts.PROJECT_ID + '-' + consts.CSV_BUCKET,
    # ロードするファイル（*をつけることでbucket配下のファイルを前方一致でまとめてロードできる）
    source_objects=[consts.FOLDER_NAME + '/' + consts.DATA_NAME + '*'],
    # ロード先データセット.テーブル
    destination_project_dataset_table=consts.COLD_DATASET + '.' + consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
    # スキーマ定義を直接記述する場合
    # schema_fields=[],
    # スキーマ定義を参照する場合、ロードするデータの格納バケット配下の相対パスで記述する。
    schema_object=consts.SCHEMA_FOLDER + '/' + consts.COLD_DATASET + '_' + consts.DATA_NAME + consts.EXT_JSON,
    source_format='CSV',
    # compression=None,
    # 出力先テーブルが存在しない場合の挙動
    create_disposition='CREATE_IF_NEEDED',
    # 出力先テーブルが存在する場合の挙動
    write_disposition='WRITE_TRUNCATE',
    # ロードをスキップする行数（最初の行を1とする）
    # skip_leading_rows=1,
    # field_delimiter=',',
    # max_bad_records=0,
    # quote_character=None,
    # ignore_unknown_values=False,
    # allow_quoted_newlines=False,
    # allow_jagged_rows=False,
    # max_id_key=None,
    # schema_update_options=[],
    # src_fmt_configs=None,
    # external_table=False,
    # time_partitioning=[],
    # cluster_fields=[" ",],
    # autodetect=False,
    dag=dag,
)
