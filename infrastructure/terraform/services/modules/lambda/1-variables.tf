variable "lambda_name" {
  description = "The name prefix for the Lambda function"
  type        = string
}

variable "image_uri" {
  description = "The ECR image URI for the Lambda function"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
  default = {
  }
}

variable "db_ssm_parameter_arn" {
  description = "The ARN of the SSM parameter for the database"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the Lambda function VPC configuration"
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID where the Lambda function will be deployed"
  type        = string
}
