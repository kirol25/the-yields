# ============================================
# SES DKIM Records (add these to IONOS DNS)
# ============================================

output "ses_dkim_records" {
  description = "CNAME records to add to IONOS DNS for SES domain verification"
  value = {
    for domain, identity in aws_sesv2_email_identity.domains :
    domain => [
      for token in identity.dkim_signing_attributes[0].tokens :
      {
        type  = "CNAME"
        name  = "${token}._domainkey.${domain}"
        value = "${token}.dkim.amazonses.com"
      }
    ]
  }
}
