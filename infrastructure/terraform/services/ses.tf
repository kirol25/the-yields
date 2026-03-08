# ============================================
# SES Domain Identities
# ============================================

resource "aws_sesv2_email_identity" "domain" {
  count = var.ses.enabled ? 1 : 0

  email_identity = var.ses.domain

  dkim_signing_attributes {
    next_signing_key_length = "RSA_2048_BIT"
  }

  tags = {
    Name = var.ses.domain
  }
}

# ============================================
# Custom MAIL FROM domain
# ============================================

resource "aws_sesv2_email_identity_mail_from_attributes" "domain" {
  count = var.ses.enabled ? 1 : 0

  email_identity   = aws_sesv2_email_identity.domain[0].email_identity
  mail_from_domain = "mail.${var.ses.domain}"
}
