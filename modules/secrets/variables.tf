variable "common" {
  description = "common variables"
}

variable "redshift_lambda_user_username" {
  type = string
}

variable "redshift_lambda_user_password" {
  type      = string
  sensitive = true
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
