# Transaction History API

A serverless REST API built on AWS that queries transaction history data from Amazon Redshift. Deployed using Terraform with API Gateway v2 (HTTP API), Lambda (Python 3.11), and DynamoDB-backed custom JWT authentication.

## Architecture

```
Client → API Gateway (HTTP API) → Lambda Authorizer (cauth) → Lambda Handler → Redshift Serverless
                                                                    ↕
                                                               DynamoDB (tokens)
```

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [Docker](https://www.docker.com/) (for building Lambda layers)
- Python 3.11
- AWS SSO or IAM credentials with admin access

## Project Structure

```
├── dev/                        # Dev environment Terraform config
├── uat/                        # UAT environment Terraform config
├── modules/
│   ├── api_gateway/            # API Gateway v2 HTTP API + authorizer
│   ├── dynamodb/               # DynamoDB table for auth tokens
│   ├── lambda/
│   │   ├── layers/             # Lambda layer (dependencies)
│   │   └── src/
│   │       └── transaction_history_logs/
│   │           ├── handlers/       # Lambda function handlers
│   │           ├── models/         # Pydantic request/response models
│   │           ├── repositories/   # Redshift query logic
│   │           ├── utilities/      # Shared utilities
│   │           └── exceptions/     # Custom exceptions
│   └── secrets/                # Secrets Manager + VPC endpoints
└── .gitignore
```

## Setup

### 1. Configure AWS Credentials

```bash
aws configure sso
# or
export AWS_PROFILE=<your-profile>
```

### 2. Build Lambda Layer

```bash
cd modules/lambda/layers/redshift-api-layer-v1
chmod +x build_layer.sh
./build_layer.sh
```

This uses Docker to install Python dependencies for `linux/amd64` and outputs a zip file for the Lambda layer.

### 3. Create `terraform.tfvars`

Each environment (`dev/`, `uat/`) requires a `terraform.tfvars` file (git-ignored). Create one with:

```hcl
aws_account_id    = "<aws-account-id>"
aws_profile       = "<aws-cli-profile>"
aws_region        = "ap-southeast-1"
project_name      = "ppay-redshift-api"
environment       = "dev"

default_tags = {
  Project     = "palawanpay"
  Environment = "dev"
  Team        = "redshift"
}

redshift_lambda_user_username = "<redshift-username>"
redshift_lambda_user_password = "<redshift-password>"
redshift_endpoint             = "<redshift-serverless-endpoint>"
redshift_arn                  = "<redshift-workgroup-arn>"
redshift_database_name        = "<database-name>"
redshift_workgroup_name       = "<workgroup-name>"
lambda_vpc_id                 = "<vpc-id>"
lambda_vpc_subnet_ids         = ["<subnet-1>", "<subnet-2>"]
lambda_security_group_ids     = ["<sg-id>"]
```

## Deployment

### Deploy to Dev

```bash
cd dev
terraform init
terraform plan
terraform apply
```

### Deploy to UAT

```bash
cd uat
terraform init
terraform plan
terraform apply
```

## API Endpoints

All endpoints require a Bearer token in the `Authorization` header (except token generation).

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/api/generate_token` | Generate auth token (no auth required) |
| POST | `/v1/api/transactions` | Get transaction history |
| GET | `/v1/api/transactions/{retRefNo}` | Get transaction by reference number |
| POST | `/v1/api/wallet-transaction-history` | Get wallet transactions |
| POST | `/v1/api/remittance-transaction-history` | Get remittance transactions |
| POST | `/v1/api/qr-emvco-transaction-history` | Get QR EMVCO transactions |
| POST | `/v1/api/ibank-fund-transfer-history` | Get iBank fund transfer history |
| POST | `/v1/api/corporate-transaction-history` | Get corporate transactions |
| POST | `/v1/api/pesonet-transaction-history` | Get PESONet transactions |
| POST | `/v1/api/bulk-pepp-disbursement-history` | Get bulk PEPP disbursements |

## Authentication

### Generate Token

```bash
curl -X POST https://<api-url>/v1/api/generate_token \
  -H "Content-Type: application/json" \
  -d '{"sub": "agent", "aud": "your-app-name", "description": "My app token"}'
```

- `sub`: must be `"agent"` or `"corporate"`
- `aud`: application identifier
- `description`: token purpose description

### Use Token

```bash
curl -X POST https://<api-url>/v1/api/transactions \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "date_from": "2025-01-01", "date_to": "2025-01-31"}'
```

### Token Behavior

- Tokens expire after 365 days
- Re-requesting a token for the same `sub` + `aud` returns the existing valid token
- A new token is only generated after the existing one expires

## Date Filters

All date filter fields accept three formats:

| Format | Example |
|--------|---------|
| Date only | `2025-01-15` |
| Date + time | `2025-01-15 14:30:00` |
| ISO 8601 with timezone | `2025-01-15T14:30:00+08:00` |

All response dates are returned in ISO 8601 GMT+8 format: `2025-01-15T14:30:00+08:00`

## Error Responses

| Status Code | Cause |
|-------------|-------|
| 400 | Malformed JSON, missing required fields, constraint violations |
| 403 | Invalid/expired token, missing Authorization header |
| 422 | Request validation errors |
| 500 | Internal server error |

## Updating Lambda Layer Dependencies

1. Edit `modules/lambda/layers/redshift-api-layer-v1/requirements.txt`
2. Rebuild the layer:
   ```bash
   cd modules/lambda/layers/redshift-api-layer-v1
   ./build_layer.sh
   ```
3. Redeploy:
   ```bash
   cd dev
   terraform apply
   ```
