variable "aws_region" {
  description = "AWS region to deploy into"
  type = string
}
variable "aws_profile" {
  description = "AWS CLI profile"
  type = string
}
variable "aws_account_id" {
  description = "AWS Account ID"
  type = string
}
variable "project_name" {
  description = "Project Name"
  type = string
}
variable "environment" {
  description = "Environment"
  type = string
}
variable "default_tags" {
  description = "Default tags for resources"
  type        = map(string)
}
variable "redshift_lambda_user_username" {
  type = string
}
variable "redshift_lambda_user_password" {
  type = string
}
variable "redshift_endpoint" {
  type = string
}
variable "redshift_arn" {
  type = string
}
variable "redshift_database_name" {
  type = string
}
variable "redshift_workgroup_name" {
  type = string
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




