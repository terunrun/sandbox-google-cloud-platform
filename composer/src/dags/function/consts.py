"""各TASK共通で使用する定数を定義するファイル"""

import os

# 拡張子
EXT_CSV = '.csv'
EXT_SQL = '.sql'
EXT_JSON = '.json'
EXT_GZIP = '.gz'

# Composer環境変数としてプリ設定されているものを取得するもの
# プロジェクID
PROJECT_ID = os.environ['GCP_PROJECT']
# Composer用バケット
COMPOSER_BUCKET = os.environ['GCS_BUCKET']
# DAG格納フォルダ
# DAGS_FOLDER = '/home/airflow/dag/'
DAGS_FOLDER = os.environ['DAGS_FOLDER']

# ベースリージョン
BASE_LOCATION = 'asia-northeast1'

# GCSバケット
CSV_BUCKET = 'csv-bucket'
CSV_BACKUP_BUCKET = 'csv-bucket-backup'
TABLE_EXPORT_BUCKET = 'export-backet'
# CSV_BUCKET = 'scraping-csv'
# CSV_BUCKET_BACKUP = 'scraping-csv-backup'
# Dataflowを使用する場合はコメントアウトを外す
# DATAFLOW_TEMPLATE_BUCKET = 'dataflow-files'

# BigQueryデータセット
MASTER_DATASET = 'master'
IMPORT_DATASET = 'import'
COLD_DATASET = 'cold'
WARM_DATASET = 'warm'
HOT_DATASET = 'hot'

# Composer用バケットフォルダセパレータ
SCHEMA_FOLDER = 'schema'
SQL_FOLDER = 'sql'

DEFINITION_FOLDER = f'{DAGS_FOLDER}/definition/'
SCHEMA_FOLDER = f'{DAGS_FOLDER}/schema/'
SHELL_FOLDER = f'{DAGS_FOLDER}/shell/'
SQL_FOLDER = f'{DAGS_FOLDER}/sql/'

# # 受信データ格納GCSフォルダ名称
FOLDER_NAME = 'sample_folder'

# # 受信データ名
DATA_NAME = 'sample_data'

# CloudComposer用パスフォーマット
COMPOSER_QUERY_FMT = 'gs://{}/dags/{}'.format(COMPOSER_BUCKET, SQL_FOLDER)
COMPOSER_QUERY_PATH = DAGS_FOLDER + '/{}/'.format(SQL_FOLDER)
COMPOSER_DATA_FMT = 'gs://{}/data'.format(COMPOSER_BUCKET)

# Dataflowを使用する場合はコメントアウトを外す
# DATAFLOW_TEMPLATE_BUCKET = 'dataflow-files'
# Dataflowテンプレート格納フォルダ
# DATAFLOW_TEMPLATE_FMT = 'gs://{}-{}/templates/'.format(PROJECT_ID, DATAFLOW_TEMPLATE_BUCKET)
