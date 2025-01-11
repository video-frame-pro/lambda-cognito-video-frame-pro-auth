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

    if not username:
        return generate_error_response(400, 'Missing parameter: username')

    if not password:
        return generate_error_response(400, 'Missing parameter: password')

    if not email:
        return generate_error_response(400, 'Missing parameter: email')

    # Validar formato de email
    if not is_valid_email(email):
        return generate_error_response(400, 'Invalid email format')

    try:
        # Verificar se o email ou username já existe
        cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=email  # Verifica se o email já está em uso
        )
        return generate_error_response(400, 'Email already exists')
    except cognito_client.exceptions.UserNotFoundException:
        pass  # O usuário não existe, então podemos continuar

    try:
        cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=username  # Verifica se o username já está em uso
        )
        return generate_error_response(400, 'Username already exists')
    except cognito_client.exceptions.UserNotFoundException:
        pass  # O username não existe, então podemos continuar

    try:
        # Criar o usuário no Cognito via sign_up
        response = cognito_client.sign_up(
            ClientId=os.environ['COGNITO_CLIENT_ID'],  # Usamos o ClientId aqui para referir ao app client
            Username=username,  # Usamos o username para o cadastro
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'preferred_username', 'Value': username}  # Adicionando o username também
            ]
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User created successfully',
                'username': username,
                'user_attributes': response
            })
        }
    except ClientError as e:
        # Tratamento de erro para falhas no Cognito
        error_message = e.response['Error'].get('Message', 'Unknown error')
        return generate_error_response(500, f'Error: {error_message}')
