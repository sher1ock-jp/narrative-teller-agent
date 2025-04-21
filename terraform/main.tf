terraform {
  backend "remote" {
    organization = "sher1ock"
    workspaces {
      name = "narrative-teller-agent"
    }
  }
}

resource "google_project_service" "sqladmin" {
  service = "sqladmin.googleapis.com"
}

resource "google_sql_database_instance" "instance" {
  name             = var.instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.instance_tier

    backup_configuration {
      enabled = true
    }
  }
}

resource "google_sql_database" "db" {
  name     = var.db_name
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.instance.name
  password = var.db_password
}

# 新規: Cloud Run 用サービスアカウントを作成
resource "google_service_account" "run_sa" {
  account_id   = var.service_account_id
  display_name = "Cloud Run Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_run_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Enable Cloud Build API
resource "google_project_service" "cloudbuild" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
}
