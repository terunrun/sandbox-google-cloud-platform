terraform {
  required_version = "~>0.14"
  # 他環境から開発環境にあるstateファイルを参照するための定義
  backend "gcs" {
    bucket      = "sandbox-terunrun-dev-terraform-state"
    prefix      = "terraform/state"
    credentials = "backend_credential.json" # terraform-backendのサービスアカウントキー
  }
  required_providers {
    google = "~> 3.21.0"
  }
}

resource "google_storage_bucket" "terraform-state" {
  count              = terraform.workspace == "dev" ? 1 : 0
  name               = "${local.project}-terraform-state"
  location           = local.region1
  storage_class      = "REGIONAL"
  bucket_policy_only = true
  labels = {
    # TODO:設定するとエラーになるので一旦コメントアウト
    # description = "TerraformのStateファイル格納バケット"
  }
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = 0
      num_newer_versions = 5
      with_state = "ANY"
    }
    action {
      type = "Delete"
    }
  }
}

locals {
  # common
  project = local.env["project"]
  region1 = "asia-northeast1"
  region2 = "asia-east1"
  zone1   = "asia-northeast1-b" #メインで利用するゾーン

  # composer
  composer-bucket-name  = local.env["composer-bucket-name"]
  composer_version      = local.env["composer_version"]

  # monitoring
  # is_stackdriver_monitoring_project = terraform.workspace == "stg" || terraform.workspace == "prd" ? 1 : 0
  is_stackdriver_monitoring_project = terraform.workspace == "dev" || terraform.workspace == "stg" || terraform.workspace == "prd" ? 1 : 0
  notification_channel_email = [
    "terunrun@gmail.com",
  ]

  workspace = {
    dev = {
      # common
      project = "sandbox-terunrun-dev"

      # composer
      composer-bucket-name = ""
      composer_version     = "composer-1-13-3-airflow-1-10-12"

    }
    stg = {
      # common
      project = "sandbox-terunrun-stg"

    # TODO:CloudComposerによって作成されるのであとづけする
    #   # composer
    #   composer-bucket-name = ""
    #   composer_version     = ""
    }
    prd = {
      # common
      project = "sandbox-terunrun-prd"

    # TODO:CloudComposerによって作成されるのであとづけする
    #   # composer
    #   composer-bucket-name = ""
    #   composer_version     = ""
    }
  }
  env = local.workspace[terraform.workspace]
}

######################################## project ########################################

provider "google" {
  credentials = file("./${terraform.workspace}/terraform_deployment_service_account_credential.json")
  project     = local.project
  region      = local.region1
}

######################################## bigquery ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_table

resource "google_bigquery_dataset" "import" {
  dataset_id    = "import"
  friendly_name = "import"
  description   = "一時データ格納用データセット"
  location      = local.region1

  labels = {
    import = "import"
  }
}

resource "google_bigquery_table" "test_table" {
  dataset_id = google_bigquery_dataset.import.dataset_id
  table_id   = "test_table"

  labels = {
    env = "test_table"
  }

  # main.tfに直で記載する
  schema = <<EOF
[
  {
    "name": "name",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "名前"
  },
  {
    "name": "description",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "説明"
  }
]
EOF

}

resource "google_bigquery_table" "test_partitioning_table" {
  dataset_id = google_bigquery_dataset.import.dataset_id
  table_id   = "test_partitioning_table"

  # time_partitioningで使用するカラムを指定する
  time_partitioning {
    type = "DAY"
    field = "day"
  }

  labels = {
    env = "test_partitioning_table"
  }

  # schemaディレクトリに格納したスキーマ定義ファイルを読み込む
  schema = file("./schema/test_partitioning_table.json")
}
