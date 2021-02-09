terraform {
  required_version = "~>0.14"
  # 他環境から開発環境にあるstateファイルを参照するための定義
  backend "gcs" {
    bucket      = "sandbox-terunrun-dev-terraform-state"
    prefix      = "terraform/state"
    credentials = "backend_credential.json" # terraform-backendのサービスアカウントキー
  }
  required_providers {
    google = "~> 3.54.0"
  }
}

resource "google_storage_bucket" "terraform-state" {
  count              = terraform.workspace == "dev" ? 1 : 0
  name               = "${local.project}-terraform-state"
  location           = local.region1
  storage_class      = "REGIONAL"
  uniform_bucket_level_access = true
  # labels = {
  # }
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

  # instance
  machine-type   = local.env["machine-type"]

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

      # instance
      machine-type   = "n1-standard-1"

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


######################################## network ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_address

resource "google_compute_address" "test-static-ip" {
  name   = "test-static-ip"
  region = local.region1
}

######################################## instance ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance

resource "google_compute_instance" "test-instance" {
  name         = "test-${terraform.workspace}"
  machine_type = local.machine-type
  zone         = local.zone1
  description  = "テスト用サーバ"
  # tags         = ["no-ip"]

  labels = {
    env           = terraform.workspace
    friendly_name = "テスト用サ-バ"
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.test-static-ip.address
    }
  }

  # metadata_startup_script = ""
}

######################################## storage ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket

resource "google_storage_bucket" "csv-bucket" {
  name          = "${local.project}-csv-bucket"
  location      = local.region1
  storage_class = "REGIONAL"
  labels = {
    env         = terraform.workspace
  }
}

resource "google_storage_bucket" "csv-bucket-buckup" {
  name          = "${local.project}-csv-bucket-buckup"
  location      = local.region1
  storage_class = "REGIONAL"
  labels = {
    env         = terraform.workspace
  }
}

# Cloud Composer環境を作成によって自動で作成されるため、あとでstateにimportする
# resource "google_storage_bucket" "composer-bucket" {
#   name          = local.composer-bucket-name
#   location      = local.region1
#   storage_class = "STANDARD"
#   labels = {
#     "goog-composer-environment" = local.project
#     "goog-composer-location"    = local.region1
#     "goog-composer-version"     = local.composer_version
#   }
# }

######################################## Cloud Composer ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/composer_environment

# INFO:デフォルト設定を一旦使用するものも、あとで変更する場合に備えて残してある
# resource "google_composer_environment" "composer-environment" {
#   name   = local.project
#   region = local.region1
#   # labels = null
#   config {
#     # node_count = 3

#     node_config {
#       zone         = local.zone1
#     #   machine_type = local.machine-type-composer
#     #   disk_size_gb = local.disk-size-composer
#     #   oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
#     #   tags         = null
#     }

#     software_config {
#       airflow_config_overrides = {
#         core-dagbag_import_timeout       = 60
#         core-default_timezone            = "Asia/Tokyo"
#         core-dags_are_paused_at_creation = "True"
#         core-logging_level               = terraform.workspace == "dev" ? "DEBUG" : "INFO"
#       }
#     #   env_variables  = null
#     #   pypi_packages = {
#     #     google-cloud-datastore = "==1.8.0"
#     #   }
#       image_version  = "composer-1.13.3-airflow-1.10.12"
#       python_version = 3
#     }
#   }
# }

######################################## bigquery ########################################
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
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
