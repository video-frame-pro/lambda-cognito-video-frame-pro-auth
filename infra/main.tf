provider "aws" {
  region = var.aws_region
}

# Função Lambda
resource "aws_lambda_function" "create_user" {
  function_name = "user_auth_function" # Nome fixo da função Lambda

  handler = "lambda_function.lambda_handler"
  runtime = "python3.8"
  role    = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.COGNITO_USER_POOL_ID
      COGNITO_CLIENT_ID    = var.COGNITO_CLIENT_ID
    }
  }

  # Caminho para o código da função Lambda
  filename         = "../lambda/lambda_function.zip"
  source_code_hash = filebase64sha256("../lambda/lambda_function.zip")  # Garante que a Lambda seja atualizada quando o código mudar
}


# Role para Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"  # Nome fixo da role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Política de Permissões do Cognito para Lambda
resource "aws_iam_policy" "lambda_cognito_policy" {
  name        = "lambda_cognito_policy"
  description = "Permissões necessárias para a Lambda registrar usuários no Cognito"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "cognito-idp:SignUp"
        ]
        Effect   = "Allow"
        Resource = var.COGNITO_USER_POOL_ARN
      },
    ]
  })
}

# Anexar a política à role da Lambda
resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name       = "lambda-policy-attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.lambda_cognito_policy.arn
}