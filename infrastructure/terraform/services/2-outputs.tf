# ============================================
# IAM deployment credentials
# ============================================

output "app_server_access_key_id" {
  description = "AWS access key ID for the app server IAM user"
  value       = var.s3.enabled ? aws_iam_access_key.app_server[0].id : null
}

output "app_server_secret_access_key" {
  description = "AWS secret access key for the app server IAM user"
  value       = var.s3.enabled ? aws_iam_access_key.app_server[0].secret : null
  sensitive   = true
}

# ============================================
# SES DKIM Records (add these to IONOS DNS)
# ============================================

output "ses_mail_from_records" {
  description = "DNS records required for custom MAIL FROM domain (add to IONOS DNS)"
  value = var.ses.enabled ? [
    {
      type     = "MX"
      name     = "mail.${var.ses.domain}"
      value    = "feedback-smtp.eu-central-1.amazonses.com"
      priority = 10
    },
    {
      type  = "TXT"
      name  = "mail.${var.ses.domain}"
      value = "v=spf1 include:amazonses.com ~all"
    }
  ] : []
}

output "ses_dkim_records" {
  description = "CNAME records to add to IONOS DNS for SES domain verification"
  value = var.ses.enabled ? [
    for token in aws_sesv2_email_identity.domain[0].dkim_signing_attributes[0].tokens :
    {
      type  = "CNAME"
      name  = "${token}._domainkey.${var.ses.domain}"
      value = "${token}.dkim.amazonses.com"
    }
  ] : []
}
