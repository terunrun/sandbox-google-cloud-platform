# [Cloud Run](https://cloud.google.com/run/?hl=ja)

## ディレクトリ説明
* python：pythonで記述したコード群

## ビルド
ソースコードおよびDockerfileが存在するディレクトリにて以下コマンドを実行する。  
> {FUNCTION NAME} はmain.py内の関数名を指定する。
```sh
$ gcloud builds submit --tag gcr.io/{PROJECT-ID}/{FUNCTION NAME}
```
これにより、Cloud BuildによってDockerfileに従ってコンテナイメージが作成される。  
Cloud Storage（{PROJECT_ID}_cloudbuildバケット）にビルド用ファイルが作成され、イメージ自体はContainer Registryに格納される。

## デプロイ
以下コマンドを実行する。
image引数にはデプロイしたいイメージを指定する。
```sh
$ gcloud run deploy --image gcr.io/{PROJECT-ID}/{FUNCTION NAME} --platform managed
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

