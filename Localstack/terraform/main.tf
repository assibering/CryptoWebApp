provider "aws" {
  region                      = var.aws_default_region
  access_key                  = var.aws_access_key_ID
  secret_key                  = var.aws_secret_access_key
  skip_credentials_validation = var.environment == "local" ? true : false
  skip_metadata_api_check     = var.environment == "local" ? true : false
  skip_requesting_account_id  = var.environment == "local" ? true : false

  endpoints {
    dynamodb = var.aws_endpoint
    iam = var.aws_endpoint
  }
}
