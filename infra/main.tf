provider "aws" {
  region = var.aws_region
}

# Função Lambda para Registro de Usuário
resource "aws_lambda_function" "register_user" {
  function_name = "user_register_function"

  handler = "register.lambda_handler"
  runtime = "python3.8"
  role    = aws_iam_role.lambda_register_role.arn  # Atualizado para usar a role específica

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.COGNITO_USER_POOL_ID
      COGNITO_CLIENT_ID    = var.COGNITO_CLIENT_ID
    }
  }

  filename         = "../lambda/register/register_lambda_function.zip"
  source_code_hash = filebase64sha256("../lambda/register/register_lambda_function.zip")
}

# Função Lambda para Login de Usuário
resource "aws_lambda_function" "login_user" {
  function_name = "user_login_function"

  handler = "login.lambda_handler"
  runtime = "python3.8"
  role    = aws_iam_role.lambda_login_role.arn  # Atualizado para usar a role específica

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.COGNITO_USER_POOL_ID
      COGNITO_CLIENT_ID    = var.COGNITO_CLIENT_ID
    }
  }

  filename         = "../lambda/login/login_lambda_function.zip"
  source_code_hash = filebase64sha256("../lambda/login/login_lambda_function.zip")
}

# Role para Lambda de Registro
resource "aws_iam_role" "lambda_register_role" {
  name = "lambda_register_user_role"

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

# Role para Lambda de Login
resource "aws_iam_role" "lambda_login_role" {
  name = "lambda_login_user_role"

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
  description = "Permissões necessárias para as Lambdas interagirem com o Cognito"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "cognito-idp:SignUp",
          "cognito-idp:InitiateAuth",
          "cognito-idp:AdminCreateUser",
          "cognito-idp:RespondToAuthChallenge",
          "lambda:GetFunction"
        ]
        Effect   = "Allow"
        Resource = var.COGNITO_USER_POOL_ARN
      },
      {
        Action = [
          "cognito-idp:AdminConfirmSignUp",
          "cognito-idp:AdminSetUserPassword",
          "cognito-idp:AdminGetUser"
        ]
        Effect   = "Allow"
        Resource = var.COGNITO_USER_POOL_ARN
      }
    ]
  })
}

# Anexar a política à role da Lambda de Registro
resource "aws_iam_role_policy_attachment" "register_policy_attachment" {
  role       = aws_iam_role.lambda_register_role.name
  policy_arn = aws_iam_policy.lambda_cognito_policy.arn
}

# Anexar a política à role da Lambda de Login
resource "aws_iam_role_policy_attachment" "login_policy_attachment" {
  role       = aws_iam_role.lambda_login_role.name
  policy_arn = aws_iam_policy.lambda_cognito_policy.arn
}
