# [Terraform](https://www.terraform.io/)

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
> tfstateファイルはTerraformで構築したリソースの状態を記載するものである。
> デフォルトではローカル保存される設定であるが、プロジェクトメンバー間での共有を可能とするためCloud Storageなどで管理するのがよい。

```bash
$ gsutil mb -l asia-northeast1 -p sandbox-terunrun-dev gs://sandbox-terunrun-dev-terraform-state
```

#### サービスアカウントおよびキー作成
1. GCP環境にstate管理用サービスアカウントを作成する。([サービスアカウント作成](https://cloud.google.com/iam/docs/creating-managing-service-accounts?hl=ja))
```sh
$ gcloud iam service-accounts create SERVICE_ACCOUNT_ID \
--description="DESCRIPTION" \
--display-name="DISPLAY_NAME"
```
2. 1.で作成したサービスアカウントのキーを作成する。([サービスアカウントキー作成](https://cloud.google.com/iam/docs/creating-managing-service-account-keys?hl=ja))
```sh
$ gcloud iam service-accounts keys create ~/backend_credential.json \
--iam-account sa-name@project-id.iam.gserviceaccount.com
```
3. 1.で作成したサービスアカウントにtfstateファイル格納バケットのストレージ管理者権限を付与する。
4. GCP環境にTerraform用サービスアカウントおよびそのサービスアカウントキーを作成する。
5. 作成したキーをGoogleドライブなど、プロジェクト関係者が共通して参照できる場所に格納する。

## Terrafrom実行
### Terraform初期化
#### サービスアカウントキー配置
Googleドライブなどからサービスアカウントキーをダウンロードし、main.tfに記載されているキー格納場所に配置する。

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
> terraform apply時に同じ結果が返ってくるため必須ではない
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
# 管理対象リソース全てを削除する。
$ terraform destroy
```

```bash
# importコマンドでTerraformを使わず作成したリソースをtfstateファイルへ反映可能。
$ terraform workspace select <workspace>
$ terraform import <tfファイルのリソース名> <GCPのリソース名>

# 例
$ terraform import google_composer_environment.composer-environment sandbox-terunrun

# 手動でリソース削除など行なった場合にtfstateの状態を最新化する
$ terraform refresh
