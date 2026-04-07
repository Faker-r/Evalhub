# Import existing KMS key

resource "aws_kms_key" "evalhub" {
  description             = "Key for Evalhub Capstone project's api key storage"
  deletion_window_in_days = 10
  enable_key_rotation     = false
}
