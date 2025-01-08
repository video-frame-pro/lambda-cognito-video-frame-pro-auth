output "lambda_function_name" {
  value = aws_lambda_function.create_user.function_name
}
# Output da Lambda Function ARN
output "lambda_function_arn" {
  value = aws_lambda_function.create_user.arn
}
