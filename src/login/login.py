import json
import boto3
import os
import re
from botocore.exceptions import ClientError

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o ID do Pool de Usuários a partir das variáveis de ambiente
USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']

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
    username = body.get('username')
    password = body.get('password')
    email = body.get('email')

    if not (username or email):
        return generate_error_response(400, 'Missing parameter: username or email')

    if not password:
        return generate_error_response(400, 'Missing parameter: password')

    # Validar formato de email
    if email and not is_valid_email(email):
        return generate_error_response(400, 'Invalid email format')

    try:
        # Tentar login utilizando o username ou email
        login_identifier = email if email else username
        auth_response = cognito_client.initiate_auth(
            ClientId=os.environ['COGNITO_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': login_identifier,  # Utiliza email ou username
                'PASSWORD': password
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful',
                'auth_response': auth_response
            })
        }

    except ClientError as e:
        error_message = e.response['Error'].get('Message', 'Unknown error')
        return generate_error_response(500, f'Error: {error_message}')