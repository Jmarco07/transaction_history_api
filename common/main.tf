// Common variables for all environments
locals {
  export = {
    project_name   = var.project_name
    region         = var.aws_region
    aws_account_id = var.aws_account_id
  }
}

output "export" { value = local.export }
