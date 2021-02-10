# [Cloud Functions](https://cloud.google.com/functions?hl=ja)

## ディレクトリ説明
* python：pythonで記述したコード群


## デプロイ（Pythonの場合）
デプロイ対象のmainファイルを含むディレクトリで以下コマンドを実行する。
> プロジェクト作成時点ではCloud Functions APIが無効のため、実行時に有効化するか聞かれる（が、有効化できてもさらにCloud Build APIの有効化が必要であり失敗する）
```sh
$ gcloud functions deploy {FUNCTION_NAME} \
--runtime python37 --trigger-http --allow-unauthenticated \
--region {REGION} --project {PROJECT_ID}
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
$ gcloud functions delete {FUNCTION_NAME}
```
Cloud Storageにバケットが作成されているため削除する。
* gcf-sources-{RUNDOM_NUMBER}-{REGION}

Container Registoryにリソースが作成されているので削除する。
* gcf/us-central1/
