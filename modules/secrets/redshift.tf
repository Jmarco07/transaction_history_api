resource "aws_secretsmanager_secret" "redshift_lambda_user_secret" {
  name        = "${var.common.project_name}-redshift-lambda-user-${var.common.environment}"
  description = "Redshift Secret Admin user"
}

resource "aws_secretsmanager_secret_version" "redshift_lambda_user_credentials" {
  secret_id = aws_secretsmanager_secret.redshift_lambda_user_secret.id
  secret_string = jsonencode({
    username = "${var.redshift_lambda_user_username}"
    password = "${var.redshift_lambda_user_password}"
  })
}

output "redshift_lambda_user_secret_arn" {
  description = "The ARN of the secret"
  value       = aws_secretsmanager_secret.redshift_lambda_user_secret.arn
}
output "redshift_lambda_user_secret_name" {
  description = "The name of the secret"
  value       = aws_secretsmanager_secret.redshift_lambda_user_secret.name
}
