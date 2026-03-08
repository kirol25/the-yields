# ============================================
# SES Domain Identities
# ============================================

moved {
  from = aws_sesv2_email_identity.domains["the-yields.com"]
  to   = aws_sesv2_email_identity.domain[0]
}

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
