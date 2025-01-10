provider "aws" {
  region = var.aws_region
}

# Função Lambda para Registro de Usuário
resource "aws_lambda_function" "register_user" {
  function_name = "user_register_function"  # Nome fixo da função Lambda

  handler = "register.lambda_handler"  # Atualizado para o handler da função de registro
  runtime = "python3.8"
  role    = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.COGNITO_USER_POOL_ID
      COGNITO_CLIENT_ID    = var.COGNITO_CLIENT_ID
    }
  }

  # Caminho para o código da função Lambda
  filename         = "../src/register/lambda_function.zip"  # Novo caminho
  source_code_hash = filebase64sha256("../src/register/lambda_function.zip")
}

# Função Lambda para Login de Usuário
resource "aws_lambda_function" "login_user" {
  function_name = "user_login_function"  # Nome fixo da função Lambda

  handler = "login.lambda_handler"  # Atualizado para o handler da função de login
  runtime = "python3.8"
  role    = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.COGNITO_USER_POOL_ID
      COGNITO_CLIENT_ID    = var.COGNITO_CLIENT_ID
    }
  }

  # Caminho para o código da função Lambda
  filename         = "../src/login/lambda_function.zip"  # Novo caminho
  source_code_hash = filebase64sha256("../src/login/lambda_function.zip")
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
          "cognito-idp:SignUp",  # Para a função de registro
          "cognito-idp:InitiateAuth"  # Para a função de login
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
