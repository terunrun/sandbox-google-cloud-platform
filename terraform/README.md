# [Terraform](https://www.terraform.io/)を利用したインフラ定義

## 概要

Terraformを利用して各環境のGCPリソースを管理する。  
workspace機能を使うと、同一種であるが各環境ごとに定義が異なるリソースを管理することができる。workspaceは例えば以下のように分ける。
* dev（開発環境想定）
* stg（検証環境想定）
* prd（本番環境想定）

上記各環境の状態を反映したtfstateファイルは開発環境のGCSで管理するとよい。  


## Terraform導入（ローカル環境）
#### terrafromバージョン管理ツールをインストールする。
```bash
$ brew install tfenv
```

#### インストール可能なバージョンを確認する。
```bash
$ tfenv list-remote
```

#### 任意のバージョンをインストールする。
```bash
$ tfenv install 0.14.5
$ tfenv use 0.14.5
```

#### インストールされたバージョンを確認する。
```bash
$ terraform version
```

## Terrafrom実行準備 （各環境で初回のみ実施）

#### tfstateファイル格納バケット作成（開発環境でのみ実施）
> tfstateファイルはTerraformで構築したリソースの状態を記載するものである。デフォルトではローカル保存される設定であるが、プロジェクトメンバー間での共有を可能とするためCloud Storageなどで管理するのがよい。

```bash
$ gsutil mb -l asia-northeast1 -p sandbox-terunrun-dev gs://sandbox-terunrun-dev-terraform-state
```

#### サービスアカウントおよびキー作成
1. GCP環境にstate管理用サービスアカウントおよびそのサービスアカウントキーを作成する。([サービスアカウントのキー作成](https://cloud.google.com/iam/docs/creating-managing-service-account-keys?hl=ja#creating_service_account_keys))

2. 1で作成したサービスアカウントにtfstateファイル格納バケットのストレージ管理者権限を付与する。

3. GCP環境にTerraform用サービスアカウントおよびそのサービスアカウントキーを作成する。

> 開発段階ではサービスアカウントの役割を「editor」に設定しておくのがよい（と思われる）。

4. 作成したキーをGoogleドライブなど、プロジェクト関係者が共通して参照できる場所に格納する。

## Terrafrom実行
### Terraform初期化
#### サービスアカウントキー配置
Googleドライブからサービスアカウントキーをダウンロードし、main.tfに記載されているキー格納場所に配置する。

#### Terraform初期化（terraformコマンド初回実行時のみ）
```bash
$ terraform init
```

### Terrafrom実行

#### フォーマット整形（必要な場合）
```bash
$ terraform fmt -recursive
```

#### 差分確認（tfファイルと実環境（tfstateファイル）の差分を出力）
```bash
$ terraform plan
```

#### 実行
> 差分確認結果が想定通りであることを必ず確認すること。
```bash
$ terraform apply
```

#### その他のコマンド
```bash
# 部分的にapplyしたい場合はtargetを付ける（非推奨）
$ terraform apply -target=<tfファイルのリソース名>
# 例） $ terraform apply -target=google_storage_bucket.gcp_infra_state
```

```bash
# 管理対象リソースの一部を削除する例。
# BigQueryのデータセットなど削除できないものもある。
$ terraform destroy -target 'google_compute_instance.dataflow-deploy-env'
```

```bash
# 管理対象リソース全てを削除する。
$ terraform destroy
```

## workspace関連
```bash
# workspaceを作成する
$ terraform workspace new stg
```

```bash
# workspaceを切り替える
$ terraform workspace select dev
```

```bash
# workspaceを確認する
$ terraform workspace list
```

## その他のコマンド
```bash
# 何らかの理由で先にGCPへ物を作ってしまった場合、importでtfstateへ反映可能。
$ terraform workspace select <workspace>
$ terraform import <tfファイルのリソース名> <GCPのリソース名>

# 例
$ terraform import google_composer_environment.composer-environment sandbox-terunrun

# 手動でリソース削除など行なった場合にtfstateの状態を最新化する
$ terraform refresh