# ------------------------
# LAMBDA FUNCTION
# ------------------------

resource "aws_iam_role" "lambda" {
  name = "${var.lambda_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_lambda_function" "api" {
  function_name = var.lambda_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = var.image_uri

  timeout       = 90  # seconds
  memory_size   = 256 # MB
  architectures = ["arm64"]

  environment {
    variables = var.environment_variables
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }
}

# --- Security Group for Lambda ---
resource "aws_security_group" "lambda" {
  name   = "${var.lambda_name}-lambda-sg"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.lambda_name}-lambda-sg"
  }
}

# --- CloudWatch Log Group for Lambda ---
resource "aws_cloudwatch_log_group" "lambda_api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 1 # day
}

# ------------------------
# LAMBDA IAM POLICY
# ------------------------
resource "aws_iam_policy" "lambda_ssm" {
  name = "${var.lambda_name}-lambda-ssm"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssm:Get*",
        "ssm:Describe*",
        "ssm:List*"
      ]
      Resource = var.db_ssm_parameter_arn # "arn:aws:ssm:*:*:parameter/${var.project_name}/${var.stage}/db/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_proxy_attach" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_ssm.arn
}
