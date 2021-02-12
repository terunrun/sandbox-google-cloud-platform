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
  zone1   = "asia-northeast1-b" #メインで利用するゾーン

  # instance
  machine-type   = local.env["machine-type"]

  # composer
  composer-bucket-name  = local.env["composer-bucket-name"]
  composer_version      = local.env["composer_version"]

  # monitoring
  # is_stackdriver_monitoring_project = terraform.workspace == "stg" || terraform.workspace == "prd" ? 1 : 0
  is_stackdriver_monitoring_project = terraform.workspace == "dev" || terraform.workspace == "stg" || terraform.workspace == "prd" ? 1 : 0
  notification_channel_email = local.env["notification_channel_email"]

  workspace = {
    dev = {
      # common
      project = "sandbox-terunrun-dev"

      # instance
      machine-type   = "n1-standard-1"

      # composer
      composer-bucket-name = ""
      composer_version     = "composer-1-13-3-airflow-1-10-12"

      notification_channel_email = [
        "terunrun@gmail.com",
      ]
    }
    stg = {
      # common
      project = "sandbox-terunrun-stg"

    # TODO:CloudComposerによって作成されるのであとづけする
    #   # composer
    #   composer-bucket-name = ""
    #   composer_version     = ""

      notification_channel_email = []
    }
    prd = {
      # common
      project = "sandbox-terunrun-prd"

    # TODO:CloudComposerによって作成されるのであとづけする
    #   # composer
    #   composer-bucket-name = ""
    #   composer_version     = ""

      notification_channel_email = []
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

data "template_file" "test-startup-script" {
  template = <<EOF
#!/bin/bash
sudo yum -y install python3
# パッケージインストール時にエラーになることがあるためその解決策として
sudo pip3 install --upgrade pip setuptools
sudo pip3 install paramiko
EOF
}

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
      # gcloud compute images listで表示されるPROJECT/FAMILYで指定する。
      # image = "debian-cloud/debian-9"
      image = "centos-cloud/centos-7"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # 固定IPを付与する。
      nat_ip = google_compute_address.test-static-ip.address
    }
  }

  metadata_startup_script = data.template_file.test-startup-script.rendered
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

######################################## scheduler ########################################
 
resource "google_cloud_scheduler_job" "schedule_cloud_functions" {
  name        = "schedule-cloud-functions"
  description = "Cloud Functions起動スケジュール"
  schedule    = "0 16 * * *"
  time_zone   = "Asia/Tokyo"
 
  http_target {
    http_method = "GET"
    uri         = "https://asia-northeast1-${local.project}.cloudfunctions.net/hello_world"
  }
}
 
######################################## stackdriver logging ########################################

# resource "google_logging_project_sink" "logging-sink" {
#   name                   = "logging-sink"
#   destination            = "bigquery.googleapis.com/projects/${local.project}/datasets/${google_bigquery_dataset.logging.dataset_id}"
#   filter                 = ""
#   unique_writer_identity = true
# }

# resource "google_logging_metric" "cloud_run_error" {
#   name        = "cloud-run-error-${terraform.workspace}"
#   description = "Cloud Runでのエラー"
#   filter      = <<-EOF
# resource.type = "cloud_run_revision"
# resource.labels.location = "asia-northeast1"
# severity>=WARNING
# EOF

#   metric_descriptor {
#     metric_kind = "DELTA"
#     value_type  = "INT64"
#   }
# }

resource "google_logging_metric" "cloud_functions_error" {
  name        = "cloud-functions-error-${terraform.workspace}"
  description = "Cloud Functionsでのエラー"
  filter      = <<-EOF
resource.type = "cloud_function"
resource.labels.region = "asia-northeast1"
severity>=WARNING
EOF

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

######################################## stackdriver monitoring ########################################

# resource "google_monitoring_notification_channel" "slack_alert_channel" {
#   count        = local.is_stackdriver_monitoring_project
#   display_name = "#"
#   type         = "slack"
#   labels = {
#     channel_name = "#"
#     auth_token   = "**************************************************************************"
#   }
# }

resource "google_monitoring_notification_channel" "email" {
  count        = local.is_stackdriver_monitoring_project == 1 ? length(local.notification_channel_email) : 0
  display_name = element(local.notification_channel_email, count.index)
  type         = "email"
  labels = {
    email_address = element(local.notification_channel_email, count.index)
  }
}

# resource "google_monitoring_alert_policy" "alive_composer" {
#   count        = local.is_stackdriver_monitoring_project
#   display_name = "サービス稼動監視（Composer）"
#   combiner     = "OR"
#   conditions {
#     display_name = "Databaseとの通信を確立できない時間が規定時間を超えました"
#     condition_threshold {
#       comparison      = "COMPARISON_LT"
#       duration        = "300s"
#       filter          = "metric.type=\"composer.googleapis.com/environment/database_health\" resource.type=\"cloud_composer_environment\""
#       threshold_value = 1
#       aggregations {
#         alignment_period   = "60s"
#         per_series_aligner = "ALIGN_COUNT_TRUE"
#       }
#       trigger {
#         count = 1
#       }
#     }
#   }
#   conditions {
#     display_name = "利用可能なWorker数が規定値を下回りました"
#     condition_threshold {
#       comparison      = "COMPARISON_LT"
#       duration        = "300s"
#       filter          = "metric.type=\"composer.googleapis.com/environment/num_celery_workers\" resource.type=\"cloud_composer_environment\""
#       threshold_value = 2
#       aggregations {
#         alignment_period   = "60s"
#         per_series_aligner = "ALIGN_MEAN"
#       }
#       trigger {
#         count = 1
#       }
#     }
#   }
#   # notification_channels = concat(google_monitoring_notification_channel.slack_alert_channel.*.name, google_monitoring_notification_channel.email.*.name)
#   notification_channels = concat(google_monitoring_notification_channel.email.*.name)
# }

# resource "google_monitoring_alert_policy" "workflow_error" {
#   count        = local.is_stackdriver_monitoring_project
#   display_name = "エラー監視（ワークフロー）"
#   combiner     = "OR"
#   conditions {
#     display_name = "Taskが失敗しました"
#     condition_threshold {
#       filter          = "metric.type=\"composer.googleapis.com/workflow/task/run_count\" resource.type=\"cloud_composer_workflow\" metric.label.\"state\"=\"failed\" resource.label.\"workflow_name\"=starts_with(\"${local.project}.workflow\")"
#       threshold_value = 0
#       duration        = "0s"
#       comparison      = "COMPARISON_GT"
#       aggregations {
#         alignment_period   = "60s"
#         per_series_aligner = "ALIGN_COUNT"
#       }
#       trigger {
#         count = 1
#       }
#     }
#   }
#   # notification_channels = concat(google_monitoring_notification_channel.slack_alert_channel.*.name, google_monitoring_notification_channel.email.*.name)
#   notification_channels = concat(google_monitoring_notification_channel.email.*.name)
#   documentation {
#     content   = <<EOT
# Composerで以下のTaskが失敗しました。
# DAG : $${resource.labels.workflow_name}  Task : $${metric.labels.task_name}
# Airflow UI : ${google_composer_environment.composer-environment.config.0.airflow_uri}/admin/taskinstance/?flt0_state_equals=failed&flt1_dag_id_contains=workflow
# EOT
#     mime_type = "text/markdown"
#   }
# }

resource "google_monitoring_alert_policy" "scraping_error" {
  count        = local.is_stackdriver_monitoring_project
  display_name = "エラー監視"
  combiner     = "OR"
  # conditions {
  #   display_name = "Cloud Runのエラーログを出力しました"
  #   condition_threshold {
  #     filter          = "metric.type=\"logging.googleapis.com/user/cloud-run-error-${terraform.workspace}\" resource.type=\"cloud_run_revision\""
  #     threshold_value = 0
  #     duration        = "0s"
  #     comparison      = "COMPARISON_GT"
  #     aggregations {
  #       alignment_period   = "60s"
  #       per_series_aligner = "ALIGN_COUNT"
  #     }
  #     trigger {
  #       count = 1
  #     }
  #   }
  # }
  conditions {
    display_name = "Cloud Functionsのエラーログを出力しました"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/cloud-functions-error-${terraform.workspace}\" resource.type=\"cloud_function\""
      threshold_value = 0
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
      trigger {
        count = 1
      }
    }
  }
  notification_channels = concat(google_monitoring_notification_channel.email.*.name)
  documentation {
    content   = <<EOT
ログの詳細は下記を参照

https://console.cloud.google.com/logs/query;query=resource.type%20%3D%20%22cloud_function%22%0Aresource.labels.region%20%3D%20%22${local.region1}%22%0Aseverity%3E%3DWARNING?hl=ja&supportedpurview=project&project=${local.project}
EOT
    mime_type = "text/markdown"
  }
}
