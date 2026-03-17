output "ses_dkim_records" {
  description = "CNAME records to add to IONOS DNS for SES domain verification"
  value       = module.api.ses_dkim_records
}
