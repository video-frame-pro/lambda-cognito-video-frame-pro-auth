######### LAMBDA OUTPUTS ###############################################
# ARN da função Lambda de registro
output "lambda_register_function_arn" {
  value       = aws_lambda_function.register_user.arn
  description = "ARN da função Lambda de registro"
}

# ARN da função Lambda de login
output "lambda_login_function_arn" {
  value       = aws_lambda_function.login_user.arn
  description = "ARN da função Lambda de login"
}

# Nome da função Lambda de registro
output "lambda_register_function_name" {
  value       = aws_lambda_function.register_user.function_name
  description = "Nome da função Lambda de registro"
}

# Nome da função Lambda de login
output "lambda_login_function_name" {
  value       = aws_lambda_function.login_user.function_name
  description = "Nome da função Lambda de login"
}

######### IAM OUTPUTS ##################################################
# Nome da role da função Lambda de registro
output "lambda_register_role_name" {
  value       = aws_iam_role.lambda_register_role.name
  description = "Nome da role IAM associada à função Lambda de registro"
}

# Nome da role da função Lambda de login
output "lambda_login_role_name" {
  value       = aws_iam_role.lambda_login_role.name
  description = "Nome da role IAM associada à função Lambda de login"
}

# Nome da política IAM da função Lambda de registro
output "lambda_register_policy_name" {
  value       = aws_iam_policy.lambda_register_policy.name
  description = "Nome da política IAM associada à função Lambda de registro"
}

# Nome da política IAM da função Lambda de login
output "lambda_login_policy_name" {
  value       = aws_iam_policy.lambda_login_policy.name
  description = "Nome da política IAM associada à função Lambda de login"
}

# Nome do grupo de logs da Lambda de registro
output "lambda_register_log_group_name" {
  value       = aws_cloudwatch_log_group.lambda_register_log_group.name
  description = "Nome do grupo de logs no CloudWatch para a função Lambda de registro"
}

# Nome do grupo de logs da Lambda de login
output "lambda_login_log_group_name" {
  value       = aws_cloudwatch_log_group.lambda_login_log_group.name
  description = "Nome do grupo de logs no CloudWatch para a função Lambda de login"
}
