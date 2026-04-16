resource "aws_vpc_endpoint" "redshift_data" {
  vpc_id       = var.lambda_vpc_id
  service_name = "com.amazonaws.${var.common.region}.redshift-data"
  subnet_ids = var.lambda_vpc_subnet_ids
  security_group_ids = var.lambda_security_group_ids
  vpc_endpoint_type = "Interface"
  private_dns_enabled = false

  tags = var.common.default_tags
}