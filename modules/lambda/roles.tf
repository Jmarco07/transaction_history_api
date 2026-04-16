resource "aws_iam_policy" "lambda_policy" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  name        = "${var.common.project_name}-${each.value.function_name}-lambda-policy-${var.common.environment}"
  description = "Lambda Execution Policy"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "logs:CreateLogStream",
            "logs:CreateLogGroup"
          ],
          "Resource" : [
            "arn:aws:logs:${var.common.region}:${var.common.aws_account_id}:log-group:/aws/lambda/${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}*:*"
          ],
          "Effect" : "Allow"
        },
        {
          "Action" : [
            "logs:PutLogEvents"
          ],
          "Resource" : [
            "arn:aws:logs:${var.common.region}:${var.common.aws_account_id}:log-group:/aws/lambda/${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}*:*:*"
          ],
          "Effect" : "Allow"
        },
        {
          "Action" : [
            "ec2:DescribeNetworkInterfaces",
            "ec2:CreateNetworkInterface",
            "ec2:DeleteNetworkInterface",
            "ec2:DescribeInstances",
            "ec2:AttachNetworkInterface",
            "dynamodb:PutItem",
            "dynamodb:BatchWriteItem",
            "dynamodb:UpdateItem",
            "dynamodb:GetItem",
            "dynamodb:BatchGetItem",
            "dynamodb:Query",
            "dynamodb:Scan"
          ],
          "Effect" : "Allow",
          "Resource" : "*"
        }
        # {
        #     "Action": [
        #         "ses:SendTemplatedEmail"
        #     ],
        #     "Resource": [
        #         "*"
        #     ],
        #     "Effect": "Allow"
        # }
      ]
    }
  )
}

resource "aws_iam_role" "lambda-exec-role" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  name = "${var.common.project_name}-${each.value.function_name}-lambda-role-${var.common.environment}"
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Action" : "sts:AssumeRole"
        }
      ]
    }
  )

  tags = var.common.default_tags

}


resource "aws_iam_role_policy_attachment" "lambda-exec-role-policy-attachment" {
  for_each = { for key, value in var.lambda_function_list : value.function_name => value }

  role       = aws_iam_role.lambda-exec-role[each.value.function_name].name
  policy_arn = aws_iam_policy.lambda_policy[each.value.function_name].arn
}

resource "aws_lambda_permission" "lambda_apigw_permission" {
  for_each = {
    for key, value in var.lambda_function_list : value.function_name => value
    if !contains(["cauth", "gen_cauth_token"], value.function_name)
  }

  statement_id  = "${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}-AllowAPIGWInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${var.common.project_name}-${var.common.environment}-lambda-${each.value.function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${var.apigw_execution_arn}/*/*"
}
