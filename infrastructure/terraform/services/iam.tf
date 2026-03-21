# ============================================
# IAM resources for app server access to S3
# ============================================

resource "aws_iam_user" "app_server" {
  count = var.s3.enabled ? 1 : 0

  name = "${var.project_name}-${var.stage}-app-server"
}

resource "aws_iam_user_policy" "app_server_s3" {
  count = var.s3.enabled ? 1 : 0

  name = "s3-data-access"
  user = aws_iam_user.app_server[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3DataAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data[0].arn,
          "${aws_s3_bucket.data[0].arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy" "app_server_ses" {
  count = var.s3.enabled && var.ses.enabled ? 1 : 0

  name = "ses-send-email"
  user = aws_iam_user.app_server[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "SESSendEmail"
        Effect   = "Allow"
        Action   = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource = aws_sesv2_email_identity.domain[0].arn
      }
    ]
  })
}

resource "aws_iam_access_key" "app_server" {
  count = var.s3.enabled ? 1 : 0

  user = aws_iam_user.app_server[0].name
}

# ============================================
# Store IAM credentials in SSM Parameter Store
# ============================================

resource "aws_ssm_parameter" "access_key_id" {
  count = var.s3.enabled ? 1 : 0

  name  = "/${var.project_name}/${var.stage}/access_key_id"
  type  = "String"
  value = aws_iam_access_key.app_server[0].id
}

resource "aws_ssm_parameter" "secret_access_key" {
  count = var.s3.enabled ? 1 : 0

  name  = "/${var.project_name}/${var.stage}/secret_access_key"
  type  = "SecureString"
  value = aws_iam_access_key.app_server[0].secret
}
