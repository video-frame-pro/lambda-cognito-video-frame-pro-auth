######### PROVEDOR AWS #################################################
# Configuração do provedor AWS
provider "aws" {
  region = var.aws_region
}

######### DADOS AWS ####################################################
# Obter informações sobre a conta AWS (ID da conta, ARN, etc.)
data "aws_caller_identity" "current" {}

# Obter o ID do Pool de Usuários do Cognito
data "aws_ssm_parameter" "cognito_user_pool_id" {
  name = var.cognito_user_pool_id_ssm
}

# Obter o ID do Cliente do Cognito
data "aws_ssm_parameter" "cognito_client_id" {
  name = var.cognito_client_id_ssm
}

######### FUNÇÕES LAMBDA ###############################################
# Função Lambda para Registro de Usuário
resource "aws_lambda_function" "register_user" {
  function_name = "${var.prefix_name}-${var.lambda_register_name}-lambda"
  handler       = var.lambda_register_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_register_role.arn
  filename      = var.lambda_register_zip_path
  source_code_hash = filebase64sha256(var.lambda_register_zip_path)

  environment {
    variables = {
      COGNITO_USER_POOL_ID = data.aws_ssm_parameter.cognito_user_pool_id.value
      COGNITO_CLIENT_ID    = data.aws_ssm_parameter.cognito_client_id.value
    }
  }
}

# Função Lambda para Login de Usuário
resource "aws_lambda_function" "login_user" {
  function_name = "${var.prefix_name}-${var.lambda_login_name}-lambda"
  handler       = var.lambda_login_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_login_role.arn
  filename      = var.lambda_login_zip_path
  source_code_hash = filebase64sha256(var.lambda_login_zip_path)

  environment {
    variables = {
      COGNITO_USER_POOL_ID = data.aws_ssm_parameter.cognito_user_pool_id.value
      COGNITO_CLIENT_ID    = data.aws_ssm_parameter.cognito_client_id.value
    }
  }
}

######### GRUPOS DE LOGS ###############################################
# Grupo de logs no CloudWatch para a Lambda de Registro
resource "aws_cloudwatch_log_group" "lambda_register_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.register_user.function_name}"
  retention_in_days = var.log_retention_days
}

# Grupo de logs no CloudWatch para a Lambda de Login
resource "aws_cloudwatch_log_group" "lambda_login_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.login_user.function_name}"
  retention_in_days = var.log_retention_days
}

######### IAM: FUNÇÕES LAMBDA ##########################################
# Role IAM para a Lambda de Registro
resource "aws_iam_role" "lambda_register_role" {
  name = "${var.prefix_name}-${var.lambda_register_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Role IAM para a Lambda de Login
resource "aws_iam_role" "lambda_login_role" {
  name = "${var.prefix_name}-${var.lambda_login_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

######### POLÍTICAS IAM ###############################################
# Política de permissões do Cognito para a Lambda de Registro
resource "aws_iam_policy" "lambda_register_policy" {
  name = "${var.prefix_name}-${var.lambda_register_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["cognito-idp:*"],
        Effect   = "Allow",
        Resource = var.cognito_user_pool_arn
      }
    ]
  })
}

# Política de permissões do Cognito para a Lambda de Login
resource "aws_iam_policy" "lambda_login_policy" {
  name = "${var.prefix_name}-${var.lambda_login_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["cognito-idp:*"],
        Effect   = "Allow",
        Resource = var.cognito_user_pool_arn
      }
    ]
  })
}

######### POLÍTICAS DE LOGS ############################################
# Política de permissões para CloudWatch Logs da Lambda de Registro
resource "aws_iam_policy" "lambda_register_policy" {
  name = "${var.prefix_name}-${var.lambda_register_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${aws_lambda_function.register_user.function_name}:*"
      }
    ]
  })
}

# Política de permissões para CloudWatch Logs da Lambda de Login
resource "aws_iam_policy" "lambda_login_policy" {
  name = "${var.prefix_name}-${var.lambda_login_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${aws_lambda_function.login_user.function_name}:*"
      }
    ]
  })
}

######### ANEXAR POLÍTICAS ############################################
# Anexar políticas de Cognito e Logs à Lambda de Registro
resource "aws_iam_role_policy_attachment" "register_policy_attachment" {
  role       = aws_iam_role.lambda_register_role.name
  policy_arn = aws_iam_policy.lambda_register_policy.arn
}

resource "aws_iam_role_policy_attachment" "register_logging_policy_attachment" {
  role       = aws_iam_role.lambda_register_role.name
  policy_arn = aws_iam_policy.lambda_register_policy.arn
}

# Anexar políticas de Cognito e Logs à Lambda de Login
resource "aws_iam_role_policy_attachment" "login_policy_attachment" {
  role       = aws_iam_role.lambda_login_role.name
  policy_arn = aws_iam_policy.lambda_login_policy.arn
}

resource "aws_iam_role_policy_attachment" "login_logging_policy_attachment" {
  role       = aws_iam_role.lambda_login_role.name
  policy_arn = aws_iam_policy.lambda_login_policy.arn
}
