# iam.tf

# user_service_user
resource "aws_iam_user" "user_service_user" {
  name = "user_service_user"
}

resource "aws_iam_policy" "users_table_access" {
  name        = "UsersTableAccess"
  description = "Policy allowing access only to the users DynamoDB table"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ],
        Resource = [
          aws_dynamodb_table.users_table.arn
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "user_service_policy_attach" {
  user       = aws_iam_user.user_service_user.name
  policy_arn = aws_iam_policy.users_table_access.arn
}


# subscription_service_user
resource "aws_iam_user" "subscription_service_user" {
  name = "subscription_service_user"
}

resource "aws_iam_policy" "subscriptions_table_access" {
  name        = "SubscriptionsTableAccess"
  description = "Policy allowing access only to the subscriptions DynamoDB table"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ],
        Resource = [
          aws_dynamodb_table.subscriptions_table.arn
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "subscrition_service_policy_attach" {
  user       = aws_iam_user.subscription_service_user.name
  policy_arn = aws_iam_policy.subscriptions_table_access.arn
}