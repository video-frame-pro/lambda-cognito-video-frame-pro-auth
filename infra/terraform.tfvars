######### PREFIXO DO PROJETO ###########################################
# Prefixo para nomear todos os recursos do projeto
prefix_name = "video-frame-pro"

######### AWS INFOS ####################################################
# Região AWS onde os recursos serão provisionados
aws_region = "us-east-1"

######### LAMBDA CONFIGURAÇÕES #########################################
# Nome da função Lambda de registro
lambda_register_name = "register"

# Nome da função Lambda de login
lambda_login_name = "login"

# Handler da função Lambda de registro
lambda_register_handler = "register.lambda_handler"

# Handler da função Lambda de login
lambda_login_handler = "login.lambda_handler"

# Runtime das funções Lambda
lambda_runtime = "python3.12"

# Caminho para o pacote ZIP da função Lambda de registro
lambda_register_zip_path = "../lambda/register/register.zip"

# Caminho para o pacote ZIP da função Lambda de login
lambda_login_zip_path = "../lambda/login/login.zip"

######### LOGS CLOUDWATCH ##############################################
# Número de dias para retenção dos logs no CloudWatch
log_retention_days = 7

######### SSM VARIABLES INFOS ##########################################
# Caminho no SSM para o ID do Pool de Usuários Cognito
cognito_user_pool_id_ssm = "/video-frame-pro/cognito/user_pool_id"

# Caminho no SSM para o ID do Cliente Cognito
cognito_client_id_ssm = "/video-frame-pro/cognito/client_id"

######### COGNITO ######################################################
# ARN do Cognito User Pool
cognito_user_pool_arn = "arn:aws:cognito-idp:us-east-1:522814708374:userpool/us-east-1_sCwO0vL7c"
