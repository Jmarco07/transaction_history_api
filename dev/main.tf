# Creating S3
resource "aws_s3_bucket" "backend_s3" {
  bucket = "${var.project_name}-tfstate-bucket-${var.environment}"
  tags = var.default_tags
}

# Creating DynamoDB State lock
 resource "aws_dynamodb_table" "backend-state-lock" {
  name         = "${var.project_name}-tfstate-lock-table-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
  tags = var.default_tags
}
