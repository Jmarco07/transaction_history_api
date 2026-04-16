resource "aws_apigatewayv2_api" "apigw" {
  name          = "${var.common.project_name}-${var.common.environment}"
  protocol_type = "HTTP"

  tags = var.common.default_tags
}

resource "aws_apigatewayv2_deployment" "apigw_deployment" {
  for_each = { for key, value in var.apigw_lambda_list : value.function_name => value }

  depends_on  = [aws_apigatewayv2_route.apigw_route]
  api_id      = aws_apigatewayv2_api.apigw.id
  description = "${var.common.project_name} API Gateway deployment."

  triggers = {
    redeployment = sha1(jsonencode([
      aws_apigatewayv2_stage.apigw_stage,
      aws_apigatewayv2_route.apigw_route[each.value.function_name],
      aws_apigatewayv2_integration.lambda_apigw_integration[each.value.function_name],
    ]))
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_stage" "apigw_stage" {
  api_id      = aws_apigatewayv2_api.apigw.id
  name        = var.common.environment
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_apigw_integration" {
  for_each = { for key, value in var.apigw_lambda_list : value.function_name => value }

  api_id           = aws_apigatewayv2_api.apigw.id
  integration_type = "AWS_PROXY"

  connection_type    = "INTERNET"
  description        = "Lambda integation."
  integration_method = "GET"
  integration_uri    = each.value.integration_uri
}

resource "aws_apigatewayv2_authorizer" "cauth" {
  api_id                            = aws_apigatewayv2_api.apigw.id
  authorizer_type                   = "REQUEST"
  authorizer_uri                    = var.cauth_invoke_arn
  identity_sources                  = ["$request.header.Authorization"]
  name                              = "custom-authorizer"
  authorizer_payload_format_version = "2.0"
  authorizer_result_ttl_in_seconds  = 0
}


resource "aws_apigatewayv2_route" "apigw_route" {
  for_each = { for key, value in var.apigw_lambda_list : value.function_name => value }

  api_id             = aws_apigatewayv2_api.apigw.id
  route_key          = each.value.route_key
  authorization_type = lookup(each.value, "requires_auth", false) ? "CUSTOM" : "NONE"
  authorizer_id      = lookup(each.value, "requires_auth", false) ? aws_apigatewayv2_authorizer.cauth.id : null
  # route_key = "GET /api/transactions" # TODO highlight all the same in this file and change
  target = "integrations/${aws_apigatewayv2_integration.lambda_apigw_integration[each.value.function_name].id}"
}

output "apigw_id" {
  value = aws_apigatewayv2_api.apigw.id
}
output "apigw_execution_arn" {
  value = aws_apigatewayv2_api.apigw.execution_arn
}
output "apigw_endpoint" {
  value = aws_apigatewayv2_api.apigw.api_endpoint
}
