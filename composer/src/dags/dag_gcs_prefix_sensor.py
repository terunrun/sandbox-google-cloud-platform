"""GoogleCloudStoragePrefixSensorのサンプルDAG"""

from datetime import datetime
from airflow import DAG
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStoragePrefixSensor
import pendulum
from function import consts

# DAG設定
DAG_NAME = 'dag_gcs_prefix_sensor'
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
sensor = GoogleCloudStoragePrefixSensor(
    task_id='sensor',
    # 監視先バケット
    bucket=consts.PROJECT_ID + '-' + consts.CSV_BUCKET,
    # 監視先バケット配下のファイル（前方一致）
    prefix='{}/{}'.format(consts.FOLDER_NAME + consts.DATA_NAME),
    # 監視を持続させる時間（秒）
    # デフォルトは60 * 60 * 24 * 7。
    timeout=60 * 60,
    # 監視持続時間を過ぎてもファイルを検知しなかった場合に自TASKを失敗とするかどうか
    # FalseにするとSkippedになる
    soft_fail=True,
    dag=dag,
)
