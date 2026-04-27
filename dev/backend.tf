locals {
  common = {
    project_name   = var.project_name
    region         = var.aws_region
    aws_account_id = var.aws_account_id
    environment    = var.environment
    default_tags   = var.default_tags
  }
}


terraform {
  backend "s3" {
    bucket         = "ppay-redshift-api-tfstate-bucket-dev"
    key            = "dev/palawanpay-redshift-api/terraform.tfstate"
    dynamodb_table = "ppay-redshift-api-tfstate-lock-table-dev"
    region         = "ap-southeast-1"
  }
}

provider "aws" {
  alias  = "apse1"
  region = var.aws_region
}

module "api_gateway" {
  providers = {
    aws = aws.apse1
  }
  source           = "../modules/api_gateway"
  common           = local.common
  cauth_invoke_arn = module.lambda_functions.lambda_invoke_arns["cauth_token"]
  apigw_lambda_list = [
    {
      function_name   = "transaction_history",
      route_key       = "POST /v1/api/transactions",
      integration_uri = module.lambda_functions.lambda_arns["transaction_history_logs"]
      requires_auth   = true
    },
    {
      function_name   = "transaction_view",
      route_key       = "GET /v1/api/transactions/{retRefNo}",
      integration_uri = module.lambda_functions.lambda_arns["transaction_view"]
      requires_auth   = true
    },
    {
      function_name   = "generate_cauth_token",
      route_key       = "POST /v1/api/generate_token",
      integration_uri = module.lambda_functions.lambda_arns["generate_cauth_token"]
      requires_auth   = false
    },
    
  ]
}

module "secrets" {
  providers = {
    aws = aws.apse1
  }

  source                        = "../modules/secrets"
  common                        = local.common
  redshift_lambda_user_username = var.redshift_lambda_user_username
  redshift_lambda_user_password = var.redshift_lambda_user_password
  lambda_vpc_id                 = var.lambda_vpc_id
  lambda_vpc_subnet_ids         = var.lambda_vpc_subnet_ids
  lambda_security_group_ids     = var.lambda_security_group_ids
}

module "dynamodb" {
  providers = {
    aws = aws.apse1
  }

  source = "../modules/dynamodb"
  common = local.common
}

module "lambda_functions" {
  providers = {
    aws = aws.apse1
  }

  source                          = "../modules/lambda"
  common                          = local.common
  apigw_execution_arn             = module.api_gateway.apigw_execution_arn
  redshift_lambda_user_secret_arn = module.secrets.redshift_lambda_user_secret_arn
  redshift_arn                    = var.redshift_arn
  lambda_vpc_id                   = var.lambda_vpc_id
  lambda_vpc_subnet_ids           = var.lambda_vpc_subnet_ids
  lambda_security_group_ids       = var.lambda_security_group_ids

  runtime = "python3.11" # Change this depending on runtime

  keep_alive_lambda_list = [
    { function_name = "transaction_history_logs" },
    { function_name = "transaction_view" },
  ]

  lambda_layer_list = [
    {
      name = "redshift-api-layer-v1"
    }
  ]

  lambdas_with_redshift_list = [
    {
      name = "transaction_history_logs"
    }
  ]

  lambdas_with_secrets_manager_list = [
    {
      name = "transaction_history_logs"
    },
  ]

  lambda_function_list = [
    {
      stack_name    = "transaction_history_logs",
      function_name = "cauth_token",
      description   = "Redshift API Custom Authorizer Function"
      role          = "${local.common.project_name}-cauth-lambda-role-${local.common.environment}"
      handler       = "handlers.cauth.lambda_handler",
      runtime       = "python3.11",
      memory_size   = 128,
      timeout       = 29,
      layers        = ["redshift-api-layer-v1"], # Change this depending on layer
      vpc_config = {
        subnet_ids         = var.lambda_vpc_subnet_ids
        security_group_ids = var.lambda_security_group_ids
      },
      variables = {
        CAUTH_TOKENS_DDB = "${module.dynamodb.dynamodb_cauth_token_table}"
        TZ               = "Asia/Manila"
      }
    },
    {
      stack_name    = "transaction_history_logs",
      function_name = "generate_cauth_token",
      description   = "Redshift API Generate Custom Authorizer Token Function"
      role          = "${local.common.project_name}-gen_cauth_token-lambda-role-${local.common.environment}"
      handler       = "handlers.gen_cauth_token.lambda_handler",
      runtime       = "python3.11",
      memory_size   = 128,
      timeout       = 29,
      layers        = ["redshift-api-layer-v1"], # Change this depending on layer
      vpc_config = {
        subnet_ids         = var.lambda_vpc_subnet_ids
        security_group_ids = var.lambda_security_group_ids
      },
      variables = {
        CAUTH_TOKENS_DDB = "${module.dynamodb.dynamodb_cauth_token_table}"
        TZ               = "Asia/Manila"
      }
    },
    {
      stack_name    = "transaction_history_logs",
      function_name = "transaction_history_logs",
      description   = "Redshift API Transaction History function"
      role          = "${local.common.project_name}-transaction_history-lambda-role-${local.common.environment}"
      handler       = "handlers.get_transactions.lambda_handler",
      runtime       = "python3.11",
      memory_size   = 1536,
      timeout       = 120,
      layers        = ["redshift-api-layer-v1"], # Change this depending on layer
      vpc_config = {
        subnet_ids         = var.lambda_vpc_subnet_ids
        security_group_ids = var.lambda_security_group_ids
      },
      variables = {
        REDSHIFT_ENDPOINT       = var.redshift_endpoint
        REDSHIFT_DATABASE_NAME  = var.redshift_database_name
        REDSHIFT_WORKGROUP_NAME = var.redshift_workgroup_name
        REDSHIFT_SECRET_NAME    = "${module.secrets.redshift_lambda_user_secret_name}"
        TZ                      = "Asia/Manila"
      }
    },
    {
      stack_name    = "transaction_history_logs",
      function_name = "transaction_view",
      description   = "Redshift API Transaction View function",
      role          = "${local.common.project_name}-transaction_view-lambda-role-${local.common.environment}",
      handler       = "handlers.get_transaction_view.lambda_handler",
      runtime       = "python3.11",
      memory_size   = 512,
      timeout       = 120,
      layers        = ["redshift-api-layer-v1"],
      vpc_config = {
        subnet_ids         = var.lambda_vpc_subnet_ids
        security_group_ids = var.lambda_security_group_ids
      },
      variables = {
        REDSHIFT_ENDPOINT       = var.redshift_endpoint
        REDSHIFT_DATABASE_NAME  = var.redshift_database_name
        REDSHIFT_WORKGROUP_NAME = var.redshift_workgroup_name
        REDSHIFT_SECRET_NAME    = "${module.secrets.redshift_lambda_user_secret_name}"
        TZ                      = "Asia/Manila"
      }
    },
  ]
}
