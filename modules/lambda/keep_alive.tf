variable "keep_alive_lambda_list" {
  type = list(object({
    function_name = string
  }))
  description = "Lambda functions to keep warm with EventBridge keep-alive pings"
  default     = []
}

resource "aws_cloudwatch_event_rule" "keep_alive" {
  for_each = { for item in var.keep_alive_lambda_list : item.function_name => item }

  name                = "${var.common.project_name}-${var.common.environment}-keep-alive-${each.key}"
  description         = "Keep Lambda ${each.key} warm by pinging every 5 minutes"
  schedule_expression = "rate(5 minutes)"

  tags = merge({
    Name = "${var.common.project_name}-${var.common.environment}-keep-alive-${each.key}"
  }, var.common.default_tags)
}

resource "aws_cloudwatch_event_target" "keep_alive" {
  for_each = { for item in var.keep_alive_lambda_list : item.function_name => item }

  rule = aws_cloudwatch_event_rule.keep_alive[each.key].name
  arn  = aws_lambda_function.this[each.key].arn

  input = jsonencode({
    keep_alive = true
  })
}

resource "aws_lambda_permission" "allow_eventbridge_keep_alive" {
  for_each = { for item in var.keep_alive_lambda_list : item.function_name => item }

  statement_id  = "AllowEventBridgeKeepAlive-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this[each.key].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.keep_alive[each.key].arn
}
