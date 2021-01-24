# [Cloud Composer](https://cloud.google.com/composer?hl=ja)

## ディレクトリ説明
* sh：ファイルインポートツール
* src/dags：DAGファイル
    * definition：definitionファイル
    * function：functionファイル
    * schema：schemaファイル
    * sql：SQLファイル
* tests：単体テストコード

## ファイルインポート
> インポート先GCPプロジェクトにCloudComposer環境が存在することが条件  
> shやtxtの実行権限等は適宜設定すること
1. sh/import_XXX_list.txtにインポートしたいファイルを記載する。（XXXはインポート対象ファイル種別ごとに読み替える）
2. src/dags配下、src/dags/sql配下にインポートしたいファイルを配置する。
3. 以下を実行する。
```sh
cd sh/
./import.sh
* コンソールに表示される指示に従い、プロジェクト名、インポート対象ファイル種別の順に指定する
```
なお上記shを使用する以外に、以下のどちらかの方法でインポートが可能（ファイルごとに実施が必要）。
* インポート先GCSバケットに直接アップロードする。
* gcloudコマンドを実行する。（以下はdagまたはsqlファイルの場合。sqlファイルの場合はshの中身を参照しコマンドを確認すること。）
```sh
gcloud composer environments storage dags import --project {project_id} --environment {composer_project_name}  --location {location} --source インポート対象ファイル
```

## DAG一時停止/解除
* インポート直後のDAGは一時停止状態となっているため、稼働させるにはその解除が必要。<br>
* 不用意に実行されることを防ぐため、稼働させる必要がない場合は一時停止状態にすること。<br>
* 一時停止/解除はAirflowのWEBコンソールから行う。

## DAGの手動実行
何らかの理由でDAGを手動で実行させる場合は、以下のどちらかの方法で行う。
* AirflowのWEBコンソールから実行する。
* gcloudコマンドを実行する（--confにkey-value形式で指定することでDAGに値を渡すことが可能。）。
```sh
gcloud composer environments run {composer環境名} --location="{location}" trigger_dag -- “実行したいDAG_ID” --conf ‘{"XXX": "YYY"}’
```

## DAGファイル削除
1. 以下のどちらかの方法で削除対象のDAGファイルを削除する。
    * インポート先GCSバケットから直接削除する。
    * gcloudコマンドを実行する。
    ```sh
    gcloud config set project {project_id}
    gcloud composer environments storage dags delete --environment {composer_project_name} --location {location} 削除するDAGファイル
    ```
2. 以下どちらかの方法でAirflowのWEBコンソール画面から削除する。
    * AirflowのWEBコンソールから手動で削除する。
    * gcloudコマンドを実行する。
    ```sh
    gcloud config set project {project_id}
    gcloud composer environments run --location {location} {composer_project_name} delete_dag -- DAG_ID
    ```
###### * AirflowのWEBコンソールから削除する方法はうまく行かない場合がある。その場合はgcloudコマンドを実行する。
