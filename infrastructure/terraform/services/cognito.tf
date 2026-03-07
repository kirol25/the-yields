# ============================================
# UserPool
# ============================================

resource "aws_cognito_user_pool" "main" {
  count = var.cognito.enabled ? 1 : 0

  name                     = "${var.stage}-${var.project_name}-user-pool"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  deletion_protection      = "ACTIVE"


  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  password_policy {
    minimum_length = var.cognito.password_min_length
  }

  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true

    string_attribute_constraints {
      min_length = 1
      max_length = 128
    }
  }

  schema {
    name                     = "preferred_username"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    required                 = true

    string_attribute_constraints {}
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  username_configuration {
    case_sensitive = false
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "Welcome to ${upper(var.project_name)}! Confirm Your Registration"
    email_message        = <<EOF
      <p>Welcome to ${upper(var.project_name)}!</p>
      <p>To complete your registration, please use the confirmation code below.</p>
      <p>Your Confirmation Code: <strong>{####}</strong></p>
      <p>If you did not request this code, please ignore this email. The code is valid for a limited time only, so please enter it promptly.</p>
      <p>We're excited to have you on board!</p>
      <p>Best regards,<br>
      The ${upper(var.project_name)}-Team</p>
    EOF
  }
}

# ============================================
# Client: Cognito
# ============================================

resource "aws_cognito_user_pool_client" "main" {
  count = var.cognito.enabled ? 1 : 0

  name         = "${var.stage}-${var.project_name}-client"
  user_pool_id = aws_cognito_user_pool.main[0].id

  generate_secret = false # REQUIRED for mobile apps
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  # OAuth REQUIRED for Apple federation
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  supported_identity_providers = [
    "COGNITO",
    #aws_cognito_identity_provider.apple[0].provider_name
  ]

  callback_urls = var.cognito.callback_urls
  logout_urls   = var.cognito.logout_urls

  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
}
