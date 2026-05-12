resource "aws_dynamodb_table" "cauth_token" {
  name         = "${var.common.project_name}-cauth-tokens-${var.common.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sub"
  range_key    = "aud"

  attribute {
    name = "sub"
    type = "S"
  }

  attribute {
    name = "aud"
    type = "S"
  }

  tags = var.common.default_tags
}

output "dynamodb_cauth_token_table" {
  description = "The name of the DynamoDB cauth token table"
  value       = aws_dynamodb_table.cauth_token.name
}
