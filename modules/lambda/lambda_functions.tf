resource "aws_lambda_function" "this" {
  for_each       = { for key, value in var.lambda_function_list : value.function_name => value }

  s3_bucket           = aws_s3_bucket.lambda_s3.bucket
  s3_key              = aws_s3_object.this[each.value.stack_name].key
  function_name       = "${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}"
  description         = each.value.description
  role                = aws_iam_role.lambda-exec-role[each.value.function_name].arn
  handler             = each.value.handler
  layers              = each.value.layers == null ? null : toset([for layer in each.value.layers : aws_lambda_layer_version.this[layer].arn])
  runtime             = "python3.11"  # Ensure this matches var.runtime in lambda_layers.tf
  memory_size         = each.value.memory_size
  timeout             = each.value.timeout

  source_code_hash = data.archive_file.this[each.value.stack_name].output_base64sha256

  vpc_config {
    subnet_ids         = each.value.vpc_config.subnet_ids
    security_group_ids = each.value.vpc_config.security_group_ids
  }

  environment {
    variables = each.value.variables
  }

  tags = merge({
    Name = "${var.common.project_name}-${var.common.environment}-lambda-function-${each.value.function_name}"
  }, var.common.default_tags)

  depends_on = [
    aws_iam_role.lambda-exec-role,
    aws_cloudwatch_log_group.lambda_logs,
    aws_lambda_layer_version.this  # Ensure layers are created first
  ]
}

# 🔹 Create CloudWatch Log Groups for each Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  name              = "/aws/lambda/${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}"
  retention_in_days = 30

  tags = merge({
    Name = "${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}-logs"
  }, var.common.default_tags)
}

# 🔹 Outputs
output "lambda_arns" {
  value = { for key, value in var.lambda_function_list : value.function_name => aws_lambda_function.this[value.function_name].arn }
}

output "lambda_invoke_arns" {
  value = { for key, value in var.lambda_function_list : value.function_name => aws_lambda_function.this[value.function_name].invoke_arn }
}