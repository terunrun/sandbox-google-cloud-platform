# [Cloud Run](https://cloud.google.com/run/?hl=ja)

## ディレクトリ説明
* python：pythonで記述したコード群

## ビルド
[Cloud Build](https://cloud.google.com/build?hl=ja)を使う。
ソースコードおよびDockerfileが存在するディレクトリにて以下コマンドを実行する。
> {FUNCTION NAME} はmain.py内の関数名を指定する。
```sh
$ gcloud builds submit --tag gcr.io/{PROJECT_ID}/{IMAGE_NAME}
```
これにより、Cloud BuildによってDockerfileに従ってコンテナイメージが作成される。
Cloud Storage（{PROJECT_ID}_cloudbuildバケット）にビルド用ファイルが作成され、イメージ自体はContainer Registryに格納される。
IMAGE_NAMEに大文字は使用できない模様。
Artifact Registryを使用する場合はあらかじめArtifact Registryのリポジトリを作成しておく必要がある。


## デプロイ
以下コマンドを実行する。
image引数にはデプロイしたいイメージを指定する。
```sh
$ gcloud run deploy {FUNCTION_NAME} \
  --image gcr.io/{PROJECT_ID}/{IMAGE_NAME} \
  --platform managed \
  --region=$REGION --max-instances=1 \
  --memory=256Mi --timeout=60 \
  --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
  --project=${PROJECT_ID} \
  --set-env-vars "PROJECT=${PROJECT_ID}"
```

実行するとサービス名（そのままEnterでFUNCTION NAMEになる）、リージョン、未認証呼び出し可否の入力を求められる。

## トリガー
以下コマンドを実行する。
```sh
$ curl "URL"
```
もしくはブラウザで上記URLにアクセスする。


## 削除
以下コマンドを実行する。
> platformとregionを指定しないと対話式に聞かれる。
```sh
$ gcloud run services delete {FUNCTION_NAME} --platform managed --region asia-northeast1 --project {PROJECT_ID}
```

Cloud Storageにバケットが作成されているため削除する。
* {PROJECT_ID}_cloudbuild

Container Registoryにリソースが作成されているため削除する。
* gcr.io/{PROJECT_ID}/{FUNCTION_NAME}

