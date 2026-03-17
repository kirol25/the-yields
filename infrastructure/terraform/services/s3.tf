# ============================================
# S3 bucket for app data storage
# ============================================

resource "aws_s3_bucket" "data" {
  count = var.s3.enabled ? 1 : 0

  bucket = var.s3.bucket_name
}

resource "aws_s3_bucket_public_access_block" "data" {
  count = var.s3.enabled ? 1 : 0

  bucket = aws_s3_bucket.data[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  count = var.s3.enabled ? 1 : 0

  bucket = aws_s3_bucket.data[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_versioning" "data" {
  count  = var.s3.enabled ? 1 : 0
  bucket = aws_s3_bucket.data[0].id

  versioning_configuration {
    status = "Enabled"
  }
}
