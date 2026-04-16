variable "common" {
  description = "common variables"
}

variable "apigw_execution_arn" {
  type = string
}
variable "runtime" {
  type = string
}
variable "redshift_arn" {
  type = string
}
variable "redshift_lambda_user_secret_arn" {
  type = string
}

variable "lambdas_with_redshift_list" {
  type = list(object({
    name = string
  }))
  description = "Lambdas needing redshift permissions List"
}

variable "lambdas_with_secrets_manager_list" {
  type = list(object({
    name = string
  }))
  description = "Lambdas needing secrets manager permissions List"
}

variable "lambda_layer_list" {
  type = list(object({
    name = string
  }))
  description = "Lambda Layer List"
}

variable "lambda_function_list" {
  type = list(object({
    stack_name = string,
    function_name = string,
    description = string,
    role = string,
    handler = string,
    runtime = string,
    memory_size = number,
    timeout = number,
    layers = list(string),
    vpc_config = map(list(string)),
    variables = map(string)
  }))
  description = "Lambda Function List"
}
variable "lambda_vpc_id" {
  type = string
}

variable "lambda_vpc_subnet_ids" {
  type = list(string)
}
variable "lambda_security_group_ids" {
  type = list(string)
}
