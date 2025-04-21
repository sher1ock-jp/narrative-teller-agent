output "instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.instance.connection_name
}
