######### PREFIXO DO PROJETO ###########################################
# Prefixo para nomear todos os recursos do projeto
variable "prefix_name" {
  description = "Prefixo para nomear todos os recursos do projeto"
  type        = string
}

######### AWS INFOS ####################################################
# Região AWS onde os recursos serão provisionados
variable "aws_region" {
  description = "Região onde os recursos serão provisionados"
  type        = string
}

######### LAMBDA CONFIGURAÇÕES #########################################
# Nome da função Lambda de registro
variable "lambda_register_name" {
  description = "Nome da função Lambda de registro"
  type        = string
}

# Nome da função Lambda de login
variable "lambda_login_name" {
  description = "Nome da função Lambda de login"
  type        = string
}

# Handler da função Lambda de registro
variable "lambda_register_handler" {
  description = "Handler da função Lambda de registro"
  type        = string
}

# Handler da função Lambda de login
variable "lambda_login_handler" {
  description = "Handler da função Lambda de login"
  type        = string
}

# Runtime das funções Lambda
variable "lambda_runtime" {
  description = "Runtime das funções Lambda"
  type        = string
}

# Caminho para o pacote ZIP da função Lambda de registro
variable "lambda_register_zip_path" {
  description = "Caminho para o ZIP da função Lambda de registro"
  type        = string
}

# Caminho para o pacote ZIP da função Lambda de login
variable "lambda_login_zip_path" {
  description = "Caminho para o ZIP da função Lambda de login"
  type        = string
}

######### LOGS CLOUDWATCH ##############################################
# Número de dias para retenção dos logs no CloudWatch
variable "log_retention_days" {
  description = "Número de dias para retenção dos logs no CloudWatch"
  type        = number
}

######### SSM VARIABLES INFOS ##########################################
# Caminho no SSM para o ID do Pool de Usuários Cognito
variable "cognito_user_pool_id_ssm" {
  description = "Caminho no SSM para o ID do Pool de Usuários Cognito"
  type        = string
}

# Caminho no SSM para o ID do Cliente Cognito
variable "cognito_client_id_ssm" {
  description = "Caminho no SSM para o ID do Cliente Cognito"
  type        = string
}

######### COGNITO ######################################################
# ARN do Cognito User Pool
variable "cognito_user_pool_arn" {
  description = "ARN do Cognito User Pool"
  type        = string
}
