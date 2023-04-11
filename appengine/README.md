# [App Engine](https://cloud.google.com/functions?hl=ja)

## ディレクトリ説明
* standard：スタンダード環境向け資材
* flexible；フレキシブル環境向け資材

* python：pythonで記述したコード群


## デプロイ（Pythonの場合）
デプロイ対象のmainファイルを含むディレクトリで以下コマンドを実行する。
```sh
$ gcloud app deploy --project {PROJECT_ID}
```
* アプリケーションが有効でない場合はエラーとなる
* ERROR: (gcloud.app.deploy) Unable to deploy to application [sandbox-terunrun-dev] with status [USER_DISABLED]: Deploying to stopped apps is not allowed.
* defaultネットワークがないとエラーとなる
* ERROR: (gcloud.app.deploy) Error Response: [3] Flex operation projects/sandbox-terunrun-dev/regions/asia-northeast1/operations/5877a1c6-f913-4d97-97db-a8aa1b82343a error [INVALID_ARGUMENT]: An internal error occurred while processing task /app-engine-flex/insert_flex_deployment/flex_create_resources>2022-05-30T09:10:02.421Z11880.xb.2: Network 'default' does not exist

## トリガー
以下コマンドを実行する。
```sh
$ gcloud app browse
$ curl "https://{PROJECT_ID}.an.r.appspot.com/" 
```
もしくはブラウザで上記URLにアクセスする。


## 削除
アプリケーション自体の削除はできない。
アプリケーションのサービスやバージョンを削除するには、以下コマンドを実行する。
```sh
$ gcloud app versions delete {VERSION_ID} --project {PROJECT_ID} 
$ gcloud app services delete --project {PROJECT_ID} 
```
* バージョンは最低一つデプロイされている必要がある
* defaultサービスは削除できない

Cloud Storageにバケットが作成されているため削除する。
（全てがApp Engineによるものではないかもしれない）
artifacts.{PROJECT_ID}.appspot.com：空
asia.artifacts.{PROJECT_ID}.appspot.com
{PROJECT_ID}.appspot.com：空
staging.{PROJECT_ID}.appspot.com：
