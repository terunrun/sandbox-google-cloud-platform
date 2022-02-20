# [Cloud Workflows](https://cloud.google.com/workflows/?hl=ja)

## ディレクトリ説明
* retry：ワークフローステップのリトライするサンプル
* run_to_run：複数のCloud Runを起動するサンプル
*  step：：ワークフローのステップ実行のサンプル

## デプロイ
```sh
$ gcloud workflows deploy {WORKFLOW_ID} \
 --location=$REGION_2 --async \
 --description="description for workflows" \
 --service-account="functions-executor@$PROJECT_ID.iam.gserviceaccount.com" \
 --source=./workflows/{WORKFLOW_ID}.yaml \
 --project=${PROJECT_ID}
```

## 実行
```sh
$ 
```
## 削除
```sh
$ 
```
