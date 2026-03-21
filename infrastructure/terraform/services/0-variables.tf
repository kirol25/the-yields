variable "stage" {
  description = "The stage to deploy to (e.g., dev, prod)"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "cognito" {
  description = "Configuration for Cognito User Pool"
  type = object({
    enabled             = bool
    password_min_length = number
    callback_urls       = list(string)
    logout_urls         = list(string)
    from_email_address  = optional(string)
  })
}

variable "ses" {
  description = "Configuration for SES domain identity"
  type = object({
    enabled = bool
    domain  = string
  })
}
