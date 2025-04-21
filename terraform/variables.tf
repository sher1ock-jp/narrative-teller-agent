variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "asia-northeast1"
}

variable "instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "manga-agent-sql"
}

variable "instance_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_name" {
  description = "DB name"
  type        = string
  default     = "manga_db"
}

variable "db_user" {
  description = "DB user name"
  type        = string
  default     = "app_user"
}

variable "db_password" {
  description = "DB user password"
  type        = string
  sensitive   = true
}

variable "service_account_id" {
  description = "Cloud Run service account ID (メールアドレスの @ 前部分)"
  type        = string
  default     = "cloud-run-sa"
}
