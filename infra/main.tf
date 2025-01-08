provider "aws" {
  region = var.aws_region
}

# Função Lambda
resource "aws_lambda_function" "create_user" {
  function_name = "create_user_function"

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
  source_code_hash = filebase64sha256("../lambda/lambda_function.zip")

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

  lifecycle {
    create_before_destroy = true
    prevent_destroy = false  # Removendo a proteção de destruição
  }
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

  lifecycle {
    create_before_destroy = true
    prevent_destroy = false  # Removendo a proteção de destruição
  }
}


# Anexar a política à role da Lambda
resource "aws_iam_policy_attachment" "lambda_policy_attachment" {
  name       = "lambda-policy-attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = aws_iam_policy.lambda_cognito_policy.arn
}

# Output da Lambda Function ARN
output "lambda_function_arn" {
  value = aws_lambda_function.create_user.arn
}
