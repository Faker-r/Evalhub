# Import existing S3 bucket and related configurations

resource "aws_s3_bucket" "evalhub" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evalhub" {
  bucket = aws_s3_bucket.evalhub.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}
