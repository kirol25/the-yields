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
# Sending authorization policy — allows Cognito to use this identity
# ============================================

resource "aws_sesv2_email_identity_policy" "cognito" {
  count = var.ses.enabled && var.cognito.from_email_address != null ? 1 : 0

  email_identity = aws_sesv2_email_identity.domain[0].email_identity
  policy_name    = "CognitoSendingPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "cognito-idp.amazonaws.com" }
        Action    = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource  = aws_sesv2_email_identity.domain[0].arn
      }
    ]
  })
}

# ============================================
# Custom MAIL FROM domain
# ============================================

resource "aws_sesv2_email_identity_mail_from_attributes" "domain" {
  count = var.ses.enabled ? 1 : 0

  email_identity   = aws_sesv2_email_identity.domain[0].email_identity
  mail_from_domain = "mail.${var.ses.domain}"
}
