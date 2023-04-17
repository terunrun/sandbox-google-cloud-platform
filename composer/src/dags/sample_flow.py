"""サンプルDAGファイル"""

import json
import codecs
import pendulum
from datetime import datetime
from function import consts, utils
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import DAG, Variable
# from airflow.models import XCom
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStoragePrefixSensor
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
# from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
# from airflow.contrib.operators.dataflow_operator import DataflowTemplateOperator
from airflow.contrib.operators.gcs_delete_operator import GoogleCloudStorageDeleteOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.gcs_to_gcs import GoogleCloudStorageToGoogleCloudStorageOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# DAG設定
DAG_NAME = 'sample_flow'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': True,
    'start_date': datetime(2020, 12, 15, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    # 同時実行できるタスクを制限するためpoolを指定する
    'pool': 'sample_flow',
    # 下流タスクを優先する
    'weight_rule': 'upstream',
    # 各Taskリトライ回数
    'retries': 0,
}
# スケジュール起動させる場合
# dag = DAG(DAG_NAME, schedule_interval='@daily', default_args=default_args, catchup=False)
# スケジュール起動させない場合
dag = DAG(DAG_NAME, schedule_interval="0 6,11 * * *", default_args=default_args, catchup=False)

# 必要なパラメーターをファイルから読み取る
with codecs.open(consts.DEFINITION_FOLDER + 'sample.json', 'r', 'utf-8') as f:
    args = json.load(f)[0]
    # プロジェクトID、バケット名をパラメータに追加
    args["project_id"] = consts.PROJECT_ID
    args["bucket"] = consts.CSV_BUCKET
    args["bucket_backup"] = consts.CSV_BACKUP_BUCKET

    # URLを実行してデータを取得する
    get_data = PythonOperator(
        task_id='get_data',
        python_callable=utils.request_url,
        templates_dict={
            # AirflowのVariablesに登録されているエンドポイントを取得して渡す
            'url': Variable.get(f'url-{args["project_id"]}', deserialize_json=True)[args["file_name"]],
        },
        provide_context=True,
        dag=dag,
    )

    # Cloud Storageバケットのデータを検知する
    sensor = GoogleCloudStoragePrefixSensor(
        task_id='exist_csv',
        bucket=f'{args["project_id"]}-{args["bucket"] }',
        prefix='{{params.folder_name}}/{{params.file_name}}',
        params=args,
        # Set to true to mark the task as SKIPPED on failure
        #soft_fail=False,
        # timeout=60 * 60 * 24 * 7,
        dag=dag,
    )

    # 前回データと差分比較
    diff = BranchPythonOperator(
        task_id='diff',
        python_callable=utils.diff,
        # 実行する関数に渡す引数
        templates_dict={
            # データ格納バケット配下のフォルダ
            'category': args["folder_name"],
            # データ名称
            'files': [args["file_name"] + consts.EXT_CSV],
            # 差分ありの場合に次に実行するtask_id(複数可)
            'next_task_ids_when_diff': ['copy', 'delete',],
            # 差分なしの場合に次に実行するtask_id(複数可)
            'next_task_ids_when_no_diff': ['delete',]
        },
        provide_context=True,
        dag=dag,
    )

    # 次回の比較ため、backupバケットへコピー
    copy = GoogleCloudStorageToGoogleCloudStorageOperator(
        task_id='copy',
        source_bucket=f'{args["project_id"]}-{args["bucket"] }',
        source_object=f'{args["folder_name"]}/{args["file_name"]}{consts.EXT_CSV}',
        destination_bucket=f'{args["project_id"]}-{args["bucket_backup"]}',
        destination_object=f'{args["folder_name"]}/{args["file_name"]}{consts.EXT_CSV}',
        move_object=False,
        dag=dag,
    )

    # データクレンジング
    with codecs.open(consts.SHELL_FOLDER + args["shell"], 'r', 'utf-8') as f:
        script = f.read()
        cleansing = BashOperator(
            task_id='cleansing',
            bash_command=script,
            params=args,
            dag=dag,
        )

    # BigQueryへロード
    with codecs.open(consts.SCHEMA_FOLDER + args["schema"], 'r', 'utf-8') as f:
        schema = json.load(f)
        load = GoogleCloudStorageToBigQueryOperator(
            task_id='load',
            bucket=f'{args["project_id"]}-{args["bucket"] }',
            source_objects=['{{params.folder_name}}/{{params.file_name}}' + consts.EXT_CSV],
            destination_project_dataset_table='{{params.project_id}}.' + consts.IMPORT_DATASET + '.{{params.file_name}}_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d")}}',
            schema_fields=schema,
            source_format='CSV',
            # compression=None,
            create_disposition='CREATE_IF_NEEDED',
            skip_leading_rows=1,
            write_disposition='WRITE_TRUNCATE',
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
            params=args,
            dag=dag,
        )

    # TODO:Dataflowを使用する場合に実装する。
    # ETL
    # etl = DataflowTemplateOperator(
    #     task_id='etl',
    #     template=consts.DATAFLOW_TEMPLATE_FMT + 'EtlSpot2020',
    #     dataflow_default_options={
    #         'project' : args["project_id"],
    #         'region': consts.BASE_LOCATION
    #     },
    #     parameters={
    # 		"XXX": "XXX",
    # 		"YYY": "YYY",
    #     },
    #     dag=dag,
    # )

    # 加工データ作成
    with codecs.open(consts.SQL_FOLDER + args["file_name"] + '/' + args["create_cold"], 'r', 'utf-8') as f:
        query = f.read()
        create_cold = BigQueryOperator(
            task_id='create_cold',
            sql=query,
            # クエリファイルを参照する場合、GCSのcomposerバケット配下のdagsフォルダから相対パスで記述する。
            # sql=consts.SQL_FOLDER + '/' + consts.DATA_NAME + consts.EXT_SQL,
            # クエリをハードコードするならmacrosが使用できる
            #sql='select * from `import.sample_*` where _TABLE_SUFFIX = "{}"'.format('{{ (execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d") }}'),
            destination_dataset_table='{{params.project_id}}.' + consts.COLD_DATASET + '.{{params.file_name}}_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d")}}',
            write_disposition='WRITE_TRUNCATE',
            create_disposition='CREATE_IF_NEEDED',
            use_legacy_sql=False,
            # allow_large_results=True,
            # flatten_results=None,
            # delegate_to=None,
            # udf_config=None,
            # maximum_billing_tier=None,
            # maximum_bytes_billed=None,
            # schema_update_options=(),
            # labels=None,
            # priority='INTERACTIVE',
            # time_partitioning=None,
            # api_resource_configs=None,
            # cluster_fields=None,
            location=consts.BASE_LOCATION,
            # encryption_configuration=None,
            params=args,
            dag=dag,
        )

    # 分析データ作成
    with codecs.open(consts.SQL_FOLDER + args["file_name"] + '/' + args["merge_warm"], 'r', 'utf-8') as f:
        query = f.read()
        merge_warm = BigQueryOperator(
            task_id='merge_warm',
            sql=query,
            #destination_dataset_table='{{params.project_id}}.' + consts.WARM_DATASET + '.{{params.file_name}}',
            write_disposition='WRITE_APPEND',
            # allow_large_results=True,
            # flatten_results=None,
            # delegate_to=None,
            # udf_config=None,
            use_legacy_sql=False,
            # maximum_billing_tier=None,
            # maximum_bytes_billed=None,
            # REVIEW: パーティションテーブルの作成は terrafrom で用意？
            create_disposition='CREATE_IF_NEEDED',
            # schema_update_options=(),
            # query_params=None,
            # labels=None,
            # priority='INTERACTIVE',
            # time_partitioning=None,
            # api_resource_configs=None,
            # cluster_fields=None,
            location=consts.BASE_LOCATION,
            # encryption_configuration=None,
            params=args,
            dag=dag,
        )

    # データのバックアップ
    backup = GoogleCloudStorageToGoogleCloudStorageOperator(
        task_id='backup',
        source_bucket=f'{args["project_id"]}-{args["bucket_backup"]}',
        source_object=f'{args["folder_name"]}/{args["file_name"]}{consts.EXT_CSV}',
        destination_bucket=f'{args["project_id"]}-{args["bucket_backup"]}',
        destination_object=args["folder_name"] + '/backup/' + args["file_name"] + '_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d%H%M%S")}}' + consts.EXT_CSV,
        move_object=False,
        dag=dag,
    )

    # Cloud Strorageバケットからデータ削除
    delete = GoogleCloudStorageDeleteOperator(
        task_id='delete',
        bucket_name=f'{args["project_id"]}-{args["bucket"] }',
        objects=['{{params.folder_name}}/{{params.file_name}}' + consts.EXT_CSV],
        # prefix='',
        # 差分ありなしどちらでも実行されるようにするための設定
        # 先行taskがすべて失敗かスキップでない場合に実行
        trigger_rule=TriggerRule.NONE_FAILED,
        params=args,
        dag=dag,
    )

    # TODO:必要な場合にコメントアウトを外す
    # 加工データバックアップ
    # backup_warm = BigQueryToCloudStorageOperator(
    #     task_id='backup_warm',
    #     source_project_dataset_table=consts.COLD_DATASET + '.' +
    #     consts.DATA_NAME + '_20201216',
    #     destination_cloud_storage_uris='gs://test-for-backup/{0}/{1}{2}{3}{4}'.
        # format(consts.CATEGORY_NAME, consts.DATA_NAME, '_20201216',
    #            consts.EXT_CSV, consts.EXT_GZIP),
    #     compression='GZIP',
    #     # export_format='CSV',
    #     # field_delimiter=',',
    #     print_header=True,
    #     dag=dag,
    # )

    # 処理フロー設定
    get_data >> sensor >> diff >> [copy, delete]
    copy >> cleansing >> load >> [create_cold, backup, delete]
    create_cold >> merge_warm
