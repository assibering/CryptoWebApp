resource "aws_dynamodb_table" "users_table" {
  name           = "users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "email"

  attribute {
    name = "email"
    type = "S"
  }
}

resource "aws_dynamodb_table" "subscriptions_table" {
  name           = "subscriptions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "subscription_id"

  attribute {
    name = "subscription_id"
    type = "S"
  }
}
