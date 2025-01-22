import json
import boto3
import os
import re
from botocore.exceptions import ClientError
from datetime import datetime
import logging

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o ID do Pool de Usuários a partir das variáveis de ambiente
cognito_user_pool_id = os.environ['cognito_user_pool_id']

def is_valid_email(email):
    """Função para validar o formato do email"""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def generate_error_response(status_code, message):
    """Função centralizada para retornar erros com formato padrão"""
    logger.error(f"Error response generated - Status: {status_code}, Message: {message}")
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message})
    }

def lambda_handler(event, context):
    logger.info("Lambda function invoked")

    # Parse do corpo da requisição (POST)
    try:
        body = json.loads(event['body'])
        logger.info(f"Request body parsed successfully: {body}")
    except json.JSONDecodeError:
        return generate_error_response(400, 'Invalid JSON in request body')

    # Verificar se os parâmetros obrigatórios estão presentes
    username = body.get('username')
    password = body.get('password')
    email = body.get('email')

    if not username:
        return generate_error_response(400, 'Missing parameter: username')

    if not password:
        return generate_error_response(400, 'Missing parameter: password')

    if len(password) != 6:
        return generate_error_response(400, 'Password must be exactly 6 characters long')

    if not email:
        return generate_error_response(400, 'Missing parameter: email')

    if not is_valid_email(email):
        return generate_error_response(400, 'Invalid email format')

    # Verificar se o email já existe
    try:
        logger.info(f"Checking if email {email} already exists in Cognito")
        cognito_client.admin_get_user(
            UserPoolId=cognito_user_pool_id,
            Username=email
        )
        return generate_error_response(400, 'Email already exists')
    except cognito_client.exceptions.UserNotFoundException:
        logger.info(f"Email {email} does not exist. Proceeding.")

    # Verificar se o username já existe
    try:
        logger.info(f"Checking if username {username} already exists in Cognito")
        cognito_client.admin_get_user(
            UserPoolId=cognito_user_pool_id,
            Username=username
        )
        return generate_error_response(400, 'Username already exists')
    except cognito_client.exceptions.UserNotFoundException:
        logger.info(f"Username {username} does not exist. Proceeding.")

    try:
        # Obter a hora atual no formato Unix timestamp
        current_time = int(datetime.utcnow().timestamp())
        logger.info(f"Current timestamp: {current_time}")

        # Criar o usuário no Cognito via admin_create_user
        logger.info(f"Creating user {username} with email {email}")
        response = cognito_client.admin_create_user(
            UserPoolId=cognito_user_pool_id,
            Username=username,
            UserAttributes=[
                {'Name': 'name', 'Value': username},
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'True'},  # Marcar o email como verificado
                {'Name': 'updated_at', 'Value': str(current_time)}
            ],
            MessageAction='SUPPRESS',
        )
        logger.info(f"User creation response: {response}")

        # Definir a senha permanente para o usuário
        logger.info(f"Setting password for user {username}")
        cognito_client.admin_set_user_password(
            UserPoolId=cognito_user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )

        logger.info(f"User {username} created successfully")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User created successfully.',
                'username': username
            })
        }
    except ClientError as e:
        error_message = e.response['Error'].get('Message', 'Unknown error')
        return generate_error_response(500, f'Error: {error_message}')
