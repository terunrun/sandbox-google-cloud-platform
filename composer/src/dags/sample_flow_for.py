"""サンプルDAGファイル"""

import json
import codecs
import pendulum
from datetime import datetime
from function import consts, utils
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import DAG, Variable
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStoragePrefixSensor
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.gcs_delete_operator import GoogleCloudStorageDeleteOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.gcs_to_gcs import GoogleCloudStorageToGoogleCloudStorageOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# DAG設定
DAG_NAME = 'sample_flow_for'
default_args = {
    'owner': 'terunrun',
    'depends_on_past': True,
    'start_date': datetime(2021, 2, 22, 0, 0, tzinfo=pendulum.timezone('Asia/Tokyo')),
    'email_on_failure': False,
    'email_on_retry': False,
    # 同時実行できるタスクを制限するためpoolを指定する
    'pool': 'sample_flow_for',
    # 下流タスクを優先する
    'weight_rule': 'upstream',
    # 各Taskリトライ回数
    'retries': 0,
}

dag = DAG(DAG_NAME, schedule_interval="30 */1 * * *", default_args=default_args, catchup=False)

# 必要なパラメーターをファイルから読み取る
with codecs.open(f'{consts.DEFINITION_FOLDER}{sample.json}', 'r', 'utf-8') as file:
    args_list = json.load(file)

    for args in args_list:
        # プロジェクトID、バケット名をパラメータに追加
        args["project_id"] = consts.PROJECT_ID
        args["bucket"] = consts.CSV_BUCKET
        args["bucket_backup"] = consts.CSV_BACKUP_BUCKET

        # URLを実行してデータを取得する
        if 'is_first' in args.keys():
            get_data = PythonOperator(
                task_id='get_data',
                python_callable=utils.request_url,
                templates_dict={
                    'url':
                    Variable.get(f'url-{args["project_id"]}',
                                deserialize_json=True)[args["folder_name"]][args["url_var"]],
                },
                provide_context=True,
                dag=dag,
            )

        # Cloud Storageバケットのデータを検知する
        sensor = GoogleCloudStoragePrefixSensor(
            task_id='exist_csv_' + args["short_name"],
            bucket=f'{args["project_id"]}-{args["bucket"]}',
            prefix='{{params.folder_name}}/{{params.file_name}}',
            params=args,
            # Set to true to mark the task as SKIPPED on failure
            soft_fail=False,
            # timeout=60 * 60 * 24 * 7,
            dag=dag,
        )

        get_data >> sensor

        if 'is_first' in args.keys():
            # ファイル名を配列の形式にする
            file_list_diff = [item.get('file_name') + consts.EXT_CSV for item in args_list]

            # 前回データと差分比較
            diff = BranchPythonOperator(
                task_id='diff',
                python_callable=utils.diff,
                # 実行する関数に渡す引数
                templates_dict={
                    # データ格納バケット配下のフォルダ
                    'category': args["folder_name"],
                    # データ名称
                    'files': file_list_diff,
                    # 差分ありの場合に次に実行するtask_id(複数可)
                    'next_task_ids_when_diff': ['copy', 'delete',],
                    # 差分なしの場合に次に実行するtask_id(複数可)
                    'next_task_ids_when_no_diff': ['delete',]
                },
                provide_context=True,
                dag=dag,
            )

        sensor >> diff

        if 'is_first' in args.keys():
            # 次回の比較ため、backupバケットへコピー
            copy = GoogleCloudStorageToGoogleCloudStorageOperator(
                task_id='copy',
                source_bucket=f'{args["project_id"]}-{args["bucket"]}',
                source_object=
                f'{args["folder_name"]}/{args["file_name_prefix"]}' + "*",
                destination_bucket=
                f'{args["project_id"]}-{args["bucket_backup"]}',
                destination_object=
                f'{args["folder_name"]}/{args["file_name_prefix"]}',
                move_object=False,
                dag=dag,
            )

            # ファイル名を(file1 file2 file3)のシェルの配列の形式にする
            file_name_list = ""
            for i in range(len(args_list)):
                file_name_list +=  args_list[i]["file_name"] + " "
            args["file_name_list"] = "(" + file_name_list + ")"

            # CSVデータクレンジング
            with codecs.open(f'{consts.SHELL_FOLDER}{args["shell"]}', 'r', 'utf-8') as file:
                script = file.read()
                cleansing = BashOperator(
                    task_id='cleansing',
                    bash_command=script,
                    params=args,
                    dag=dag,
                )

            # BigQuery へロード
            with codecs.open(f'{consts.SCHEMA_FOLDER}{args["schema"]}', 'r', 'utf-8') as file:
                schema = json.load(file)
                load = GoogleCloudStorageToBigQueryOperator(
                    task_id='load',
                    bucket=f'{args["project_id"]}-{args["bucket"]}',
                    source_objects=[
                        '{{params.folder_name}}/{{params.file_name_prefix}}' + "*"
                    ],
                    destination_project_dataset_table='{{params.project_id}}.' +
                    consts.IMPORT_DATASET +
                    '.{{params.table_name}}_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d")}}',
                    schema_fields=schema,
                    source_format='CSV',
                    create_disposition='CREATE_IF_NEEDED',
                    skip_leading_rows=1,
                    write_disposition='WRITE_TRUNCATE',
                    params=args,
                    dag=dag,
                )

            # 加工データ作成(cold)
            with codecs.open(f'{consts.SQL_FOLDER}{args["table_name"]}/{args["create_cold"]}', 'r', 'utf-8') as file:
                query = file.read()
                create_cold = BigQueryOperator(
                    task_id='create_cold',
                    sql=query,
                    destination_dataset_table='{{params.project_id}}.' +
                    consts.COLD_DATASET +
                    '.{{params.table_name}}_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d")}}',
                    write_disposition='WRITE_TRUNCATE',
                    create_disposition='CREATE_IF_NEEDED',
                    use_legacy_sql=False,
                    location=consts.BASE_LOCATION,
                    params=args,
                    dag=dag,
                )

            # 分析データ作成(warm)
            with codecs.open(f'{consts.SQL_FOLDER}{args["table_name"]}/{args["merge_warm"]}', 'r', 'utf-8') as file:
                query = file.read()
                merge_warm = BigQueryOperator(
                    task_id='merge_warm',
                    sql=query,
                    write_disposition='WRITE_APPEND',
                    use_legacy_sql=False,
                    create_disposition='CREATE_IF_NEEDED',
                    location=consts.BASE_LOCATION,
                    params=args,
                    dag=dag,
                )

            # CSVファイルのバックアップ
            backup = GoogleCloudStorageToGoogleCloudStorageOperator(
                task_id='backup',
                source_bucket=f'{args["project_id"]}-{args["bucket_backup"]}',
                source_object=f'{args["folder_name"]}/{args["file_name_prefix"]}' + "*",
                destination_bucket=f'{args["project_id"]}-{args["bucket_backup"]}',
                destination_object=args["folder_name"] + '/backup/' +args["file_name_prefix"] +
                '_{{(execution_date + macros.timedelta(hours=+9)).strftime("%Y%m%d%H%M%S")}}',
                move_object=False,
                dag=dag,
            )

            filename_path = [f'{item.get("folder_name")}/{item.get("file_name")}{consts.EXT_CSV}' for item in args_list]
            # バケットからCSVファイル削除
            delete = GoogleCloudStorageDeleteOperator(
                task_id='delete',
                bucket_name=f'{args["project_id"]}-{args["bucket"]}',
                objects=filename_path,
                trigger_rule=TriggerRule.NONE_FAILED,
                dag=dag,
            )

        # 処理フロー設定
        diff >> [copy, delete]
        copy >> cleansing >> load >> [create_cold, backup, delete]
        create_cold >> merge_warm
