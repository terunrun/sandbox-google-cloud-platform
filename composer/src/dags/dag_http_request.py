"""HTTPリクエストを発行するサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
import pendulum
from function import consts, utils

# DAG設定
DAG_NAME = 'dag_http_request'
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

# Cloud Functions/Run に対してcurlを実行するとエラーになる
# Your client does not have permission to get URL
# curl = BashOperator(
# 　  task_id='curl',
#     bash_command='curl https://asia-northeast1-{project_id}.cloudfunctions.net/{function_name',
#     dag=dag,
# )

# gcloud_auth_print = BashOperator(
#     task_id='gcloud_auth_print',
#     bash_command='gcloud auth print-identity-token',
#     xcom_push=True,
#     dag=dag,
# )

# gcloud_auth_list = BashOperator(
#     task_id='gcloud_auth_list',
#     bash_command='gcloud auth list',
#     dag=dag,
# )

# Cloud Functions/Run に対してHeaderに認証情報を渡してcurlを実行してもエラーになる
# Your client does not have permission to get URL
# curl_with_header = BashOperator(
#     task_id='curl_with_header',
#     bash_command='curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" {0}'.format('URL'),
#     xcom_push=False,
#     # env=[],
#     output_encoding='utf-8',
#     dag=dag,
# )

# SimpleHttpOperatorはhttp_conn_idをurlごとに登録すればいけるのかもしれない。
# http_request = SimpleHttpOperator(
#     task_id='http_request',
#     endpoint='URL',
#     method='GET',
#     # data='',
#     headers='Authorization: Bearer "{{ti.xcom_pull(task_ids="gcloud_auth_print", key="return_value")}}"',
#     # response_check=,
#     # extra_options=,
#     # xcom_push=,
#     # log_response=,
#     dag=dag,
# )

scrape = PythonOperator(
    task_id='scrape',
    python_callable=utils.scrape,
    templates_dict={
        # Airflow Variablesに登録したものを使用するならこのように記述する
        # 'url': Variable.get('URL'),
         'url': 'XXX',
    },
    provide_context=True,
    dag=dag,
)

# gcloud_auth_print >> curl_with_header