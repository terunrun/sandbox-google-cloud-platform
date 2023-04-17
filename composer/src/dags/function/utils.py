"""Cloud ComposerのTASKで使用する関数を定義するファイル"""

import consts
import logging
import os
import requests
import subprocess
import google.auth.transport.requests
import google.oauth2.id_token
from airflow.models import Variable
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery, datastore


def get_templates_dict(**kwargs):
    """呼び出し元TASKから渡された値を順に表示する"""
    for key, val in kwargs.items():
        logging.info(f'key:{key}, value: {val}, type: {type(val)}')


def request_url(**kwargs):
    """urlにリクエストを発行する"""
    url = kwargs['templates_dict']['url']
    # リクエストにパラメーターを追加
    payload = kwargs['templates_dict']['data'] if 'data' in kwargs['templates_dict'] else {}

    # トークンを取得
    request = google.auth.transport.requests.Request()
    target_audience = url
    logging.info('token: %s', token)
    token = google.oauth2.id_token.fetch_id_token(request, target_audience)

    headers = {f'Authorization': 'Bearer {token}'}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    logging.info(response)


def diff(**kwargs):
    """Cloud Storageから取得したデータを比較し差分があるかどうかを判定する"""
    category = kwargs['templates_dict']['category']
    files = kwargs['templates_dict']['files']

    for file in files:
        # データコピー
        command = f'gsutil cp gs://{consts.PROJECT_ID}-{consts.CSV_BUCKET}/{category}/{file} /tmp/diff/{file}'
        ret = subprocess.run(command.split())

        # 比較データコピー
        command = f'gsutil cp gs://{consts.PROJECT_ID}-{consts.CSV_BACKUP_BUCKET}/{category}/{file} /tmp/diff/backup_{file}'
        ret = subprocess.run(command.split())

        # 比較データを取得できなきかった場合は「next_task_ids_when_diff」で指定されたTaskを実行
        if not os.path.isfile(f'/tmp/diff/backup_{file}'):
            return kwargs['templates_dict']['next_task_ids_when_diff']

        # CSVデータ比較
        command = f'diff /tmp/diff/{file} /tmp/diff/backup_{file}'
        ret = subprocess.run(command.split(), stdout=subprocess.PIPE)
        output = ret.stdout
        # 結果を行ごとにリストにする。
        lines = output.splitlines()

        # ローカルファイルを削除する。
        command = f'rm -f /tmp/diff/{file}'
        ret = subprocess.run(command.split())
        command = f'rm -f /tmp/diff/backup_{file}'
        ret = subprocess.run(command.split())

        # 差分ありのファイルがある（差分リストの中身が存在する）場合は「next_task_ids_when_diff」で指定されたTaskを実行
        if lines:
            logging.info('diff length: %s', len(lines))
            return kwargs['templates_dict']['next_task_ids_when_diff']
        continue

    # 全てのファイルに差分がない場合は「next_task_ids_when_no_diff」で指定されたTaskを実行
    return kwargs['templates_dict']['next_task_ids_when_no_diff']


def push_value(context, dag_run_obj):
    """TriggerDagRunOperatorでトリガーするDAGに値を送信する"""
    # 呼び出し元TASKで指定したパラメータはcontext引数から取得できる
    value = context['params']['key']
    logging.info('value in params is %s', value)

    # dag_run_obj.payloadにトリガーするDAGに値を渡せる
    dag_run_obj.payload = {
        # 呼び出しTASKで指定したパラメータを元にxcomから値を取得
        'execution_date': context['ti'].xcom_pull(key='execution_date', task_ids=value),
    }
    logging.info('pushed execution_date is %s', dag_run_obj.payload['execution_date'])
    return dag_run_obj


def get_today():
    """システム日付（日本時間）を取得する"""
    jst = timezone(timedelta(hours=+9), 'JST')
    jst_now = datetime.now(jst)
    today = jst_now.strftime('%Y%m%d')
    return today


def get_airflow_variables(variable_key):
    """AirflowのVariablesの値を取得する"""
    variable = Variable.get(variable_key)
    logging.info('variable: %s', variable)


def set_execution_date(**kwargs):
    """実行日付を設定し後続Taskを決定する"""
    isSkip = get_airflow_variables("isSkip")

    # AirflowのVariablesのisSkipがTrueの場合は「execute_task_id_2」で指定したTaskを実行する
    if isSkip:
        logging.info('Next task: %s', kwargs['templates_dict']['execute_task_id_2'])
        return kwargs['templates_dict']['execute_task_id_2']

    base_date = datetime.strptime(get_today, '%Y%m%d')
    logging.info('base_date is {}.'.format(base_date))

    execution_date = base_date + timedelta(days=-1)
    execution_date_str = execution_date.strftime('%Y%m%d')
    logging.info('execution_date is {}.'.format(execution_date_str))
    return kwargs['templates_dict']['execute_task_id_1']


def push_value_to_dag(context, dag_run_obj):
    """xcomから取得した値をTriggerDagRunOperatorでトリガーされるDAGに送信する"""
    logging.info('pull from xcom task id: %s', context['params']['task_id'])
    dag_run_obj.payload = {
        'push_value': context['ti'].xcom_pull(
                                key='push_value',
                                task_ids=context['params']['task_id']
                            ),
    }
    logging.info('pushed value is %s', dag_run_obj.payload['push_value'])
    return dag_run_obj


def push_value_to_xcom(**kwargs):
    """xcomに値を登録する"""
    push_value = kwargs['templates_dict']['push_value']
    logging.info('push value is %s.', push_value)
    kwargs['ti'].xcom_push(key='push_value', value=push_value)


# datastore------------------------------------------------------------------------------------------------------------------
def get_entity_from_datastore(client, data_type, start_date):
    """DatastoreからEntityを取得する"""
    client = datastore.Client(consts.PROJECT_ID)
    query = client.query(kind="sample_kind")
    query.add_filter('dataType', '=', data_type)
    query.add_filter('startDate', '<=', start_date)
    query.order = ['-startDate']
    result = query.fetch(1)
    return result


def set_entity_to_datastore(**kwargs):
    """DatastoreのEntityを登録する"""
    client = datastore.Client(consts.PROJECT_ID)
    key = client.key("sample_kind", "sample_key")
    entity = datastore.Entity(key=key)
    entity.update({
        'name': 'sample',
        'dataType': 'sample',
        'startDate': datetime.now(timezone(timedelta(hours=+9), 'JST')),
    })
    client.put(entity)
# datastore------------------------------------------------------------------------------------------------------------------


# bigquery------------------------------------------------------------------------------------------------------------------
def run_bq_query(**kwargs):
    """BigQueryへクエリを発行する"""
    data_name = kwargs['templates_dict']['data_name']
    destination_dataset = kwargs['templates_dict']['destination_dataset']
    destination_table = kwargs['templates_dict']['destination_table']
    write_disposition = kwargs['templates_dict']['write_disposition']
    create_disposition = kwargs['templates_dict']['create_disposition']
    query_param_values = kwargs['templates_dict']['query_param_values']
    time_partitioning = kwargs['templates_dict']['time_partitioning']
    cluster_fields = kwargs['templates_dict']['cluster_fields']
    location = kwargs['templates_dict']['location']
    # logging.info('data_name:{}'.format(data_name))
    # logging.info('destination_dataset:{}'.format(destination_dataset))
    # logging.info('destination_table:{}'.format(destination_table))
    # logging.info('write_disposition:{}'.format(write_disposition))
    # logging.info('create_disposition:{}'.format(create_disposition))
    # logging.info('location:{}'.format(location))

    # クエリファイルを文字列として展開
    with open(consts.COMPOSER_QUERY_PATH + data_name + consts.EXT_SQL) as file:
        query = file.read()
        logging.info('query:"%s"', query)

    client = bigquery.Client(consts.PROJECT_ID)
    # クエリ発行時の設定
    job_config = bigquery.QueryJobConfig()
    job_config.destination = client.dataset(destination_dataset).table(
        destination_table)
    job_config.write_disposition = write_disposition
    job_config.create_disposition = create_disposition
    job_config.use_legacy_sql = False

    # クエリパラメータの設定
    if query_param_values:
        query_params = []
        for key, value in query_param_values.items():
            logging.info('query parameter name: %s, value: %s', key, value)
            query_params.append(bigquery.ScalarQueryParameter(key, 'STRING', value))
        job_config.query_parameters = query_params

    # パーティションの設定
    if time_partitioning:
        logging.info('time_partitioning: %s', time_partitioning)
        job_config.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=time_partitioning,
        )
        # クラスタの設定
        if cluster_fields:
            logging.info('cluster_fields: %s', cluster_fields)
            job_config.clustering_fields = cluster_fields

    # クエリ発行
    query_job = client.query(query, job_config=job_config, location=location)
    query_job.result()


def get_table_modify_date(table_name):
    """指定のBigQueryテーブルの最終更新日を取得する"""
    client = bigquery.Client(consts.PROJECT_ID)
    table = client.get_table(table='{0}'.format(table_name))
    table_last_modified_jst = table.modified + timedelta(hours=+9)
    table_last_modified_jst_str = table_last_modified_jst.strftime("%Y%m%d")
    logging.info('%s was modified at %s', table_name, table_last_modified_jst_str)
    return table_last_modified_jst_str
# bigquery------------------------------------------------------------------------------------------------------------------
