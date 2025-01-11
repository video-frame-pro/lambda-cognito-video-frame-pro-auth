import json
import boto3
import os
from botocore.exceptions import ClientError
import re

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o ID do Pool de Usuários e o Client ID a partir das variáveis de ambiente
USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

def is_valid_email(email):
    """Função para validar o formato do email"""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def generate_error_response(status_code, message):
    """Função centralizada para retornar erros com formato padrão"""
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message})
    }

def lambda_handler(event, context):
    # Parse do corpo da requisição (POST)
    body = json.loads(event['body'])

    # Verificar se os parâmetros obrigatórios estão presentes
    username_or_email = body.get('username') or body.get('email')
    password = body.get('password')

    if not username_or_email:
        return generate_error_response(400, 'Missing parameter: username or email')

    if not password:
        return generate_error_response(400, 'Missing parameter: password')

    # Validar formato de email, se for fornecido como username
    if username_or_email and is_valid_email(username_or_email):
        # Validar se o email fornecido tem o formato correto
        if not is_valid_email(username_or_email):
            return generate_error_response(400, 'Invalid email format')

    try:
        # Tentando fazer o login, considerando o email ou username
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,  # Recuperado da variável de ambiente
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username_or_email,
                'PASSWORD': password
            }
        )

        # Retorna o token de autenticação
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful',
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token
            })
        }
    except ClientError as e:
        # Tratamento de erro para falhas de autenticação
        error_message = e.response['Error'].get('Message', 'Unknown error')
        if "NotAuthorizedException" in error_message:
            return generate_error_response(401, 'Invalid username or password')
        return generate_error_response(500, f'Error: {error_message}')
