"""BigQueryOperatorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
import pendulum
from function import consts

# DAG設定
DAG_NAME = 'dag_bigquery'
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
run_bq_query = BigQueryOperator(
    task_id='run_bq_query',
    # 非推奨なのでsqlパラメータを使用する
    # bql='',
    # 実行するsqlをハードコードまたはクエリファイルとして指定する
    # クエリファイルとして指定する場合、composerバケット配下のdagsフォルダから相対パスで記述する
    sql=consts.SQL_FOLDER + '/' + consts.FOLDER_NAME + '/' + consts.DATA_NAME + consts.EXT_SQL,
    # クエリ発行結果の出力先データセット.テーブル
    destination_dataset_table=consts.WARM_DATASET + '.' + consts.DATA_NAME + '_' + '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}',
    # 出力先テーブルが存在する場合の挙動
    write_disposition='WRITE_TRUNCATE',
    # クエリ発行結果が大きい場合を許容するかどうか
    allow_large_results=True,
    # flatten_results=None,
    # delegate_to=None,
    # udf_config=None,
    use_legacy_sql=False,
    # maximum_billing_tier=None,
    # maximum_bytes_billed=None,
    # 出力先テーブルが存在しない場合の挙動
    create_disposition='CREATE_IF_NEEDED',
    # schema_update_options=(),
    # クエリパラメータを複数指定することができる（macrosは使用できない）
    query_params=[{ 'name': 'target_date', 'parameterType': { 'type': 'STRING' }, 'parameterValue': { 'value': '{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}' },],
    # labels=None,
    # priority='INTERACTIVE',
    # time_partitioning=None,
    # api_resource_configs=None,
    # cluster_fields=None,
    location=consts.BASE_LOCATION,
    # encryption_configuration=None,
    dag=dag,
)
