# [Cloud Functions](https://cloud.google.com/functions?hl=ja)

## ディレクトリ説明
* python：pythonで記述したコード群


## デプロイ（Pythonの場合）
デプロイ対象のmainファイルを含むディレクトリで以下コマンドを実行する。
> プロジェクト作成時点ではCloud Functions APIが無効のため、実行時に有効化するか聞かれる（が、有効化できてもさらにCloud Build APIの有効化が必要であり失敗する）
```sh
$ gcloud functions deploy {FUNCTION_NAME} \
  --region=$REGION --runtime python39 --max-instances=1 \
  --memory=256MB --timeout=60 \
  --trigger-http --security-level=secure-always --allow-unauthenticated \
  --trigger-resource {起動トリガーとするGCSバケット} \
  --trigger-event google.storage.object.finalize \
  --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
  --source=./{main.pyの格納ディレクトリパス} --entry-point={エントリポイントとなる関数名} \
  --project=${PROJECT_ID} \
  --set-env-vars "PROJECT=${PROJECT_ID}"
* {Function Name}はエントリポイントとなる関数と同名である必要がある？
* allow-unauthenticatedで未認証ユーザでも実行可能としている
```

## トリガー
以下コマンドを実行する。
```sh
$ curl "https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}"
```
もしくはブラウザで上記URLにアクセスする。


## 削除
以下コマンドを実行する。
```sh
$ gcloud functions delete {FUNCTION_NAME} --region {REGION} --project {PROJECT_ID}
```
Cloud Storageにバケットが作成されているため削除する。
* gcf-sources-{RUNDOM_NUMBER}-{REGION}

Container Registoryにリソースが作成されているので削除する。
* gcf/us-central1/
