output "ses_dkim_records" {
  description = "CNAME records to add to IONOS DNS for SES domain verification"
  value       = module.api.ses_dkim_records
}

output "app_server_access_key_id" {
  description = "AWS access key ID for the app server IAM user"
  value       = module.api.app_server_access_key_id
}

output "app_server_secret_access_key" {
  description = "AWS secret access key for the app server IAM user"
  value       = module.api.app_server_secret_access_key
  sensitive   = true
}
