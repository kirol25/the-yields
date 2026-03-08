# ============================================
# SES Domain Identities
# ============================================

resource "aws_sesv2_email_identity" "domains" {
  for_each = var.ses.enabled ? toset(var.ses.domains) : []

  email_identity = each.value

  dkim_signing_attributes {
    next_signing_key_length = "RSA_2048_BIT"
  }

  tags = {
    Name = each.value
  }
}
