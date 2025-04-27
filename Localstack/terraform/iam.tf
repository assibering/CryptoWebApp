# iam.tf
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
