variable "common" {
  description = "common variables"
}

variable "cauth_invoke_arn" {
  type = string
}

# variable "transaction_history_lambda_arn" {
# }
variable "apigw_lambda_list" {
  type = list(object({
    function_name   = string
    route_key       = string
    integration_uri = string
    requires_auth   = bool
  }))
  description = "API GW Lambda List"
}
