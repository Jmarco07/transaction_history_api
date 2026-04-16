resource "aws_s3_bucket" "lambda_s3" {
  bucket = "${var.common.project_name}-transactions-${var.common.environment}-lambda-deploymentbucket"
  tags   = var.common.default_tags
}

data "archive_file" "this" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  type = "zip"

  source_dir  = "${path.module}/src/${each.value.stack_name}"
  output_path = "${path.module}/zip/${each.value.stack_name}.zip"
}

resource "aws_s3_object" "this" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  bucket      = aws_s3_bucket.lambda_s3.bucket
  key         = "lambda/${var.common.project_name}-${var.common.environment}-lambda-${each.value.stack_name}.zip"
  source      = "${path.module}/zip/${each.value.stack_name}.zip"
  source_hash = data.archive_file.this[each.value.stack_name].output_md5

  tags = merge({
    Name = "${var.common.project_name}-${var.common.environment}-lambda-${each.value.stack_name}.zip"
    }, var.common.default_tags
  )

}
