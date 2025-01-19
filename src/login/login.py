import json
import boto3
import os
import re
from botocore.exceptions import ClientError

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o Client ID do Cognito a partir das variáveis de ambiente
CLIENT_ID = os.environ['cognito_client_id']

def is_valid_email(email):
    """Valida o formato do email"""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def generate_error_response(status_code, message):
    """Gera uma resposta de erro padrão"""
    return {
        'statusCode': status_code,
        'body': json.dumps({'error': message})
    }

def lambda_handler(event, context):
    # Parse do corpo da requisição
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError:
        return generate_error_response(400, 'Invalid JSON in request body')

    # Recuperar parâmetros obrigatórios
    login_identifier = body.get('username') or body.get('email')
    password = body.get('password')

    # Validações básicas
    if not login_identifier:
        return generate_error_response(400, 'Missing parameter: username or email')
    if not password:
        return generate_error_response(400, 'Missing parameter: password')
    if body.get('email') and not is_valid_email(body['email']):
        return generate_error_response(400, 'Invalid email format')

    try:
        # Tentar autenticar o usuário
        auth_response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': login_identifier,
                'PASSWORD': password
            }
        )

        # Retornar sucesso com tokens relevantes
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful',
                'access_token': auth_response['AuthenticationResult']['AccessToken'],
                'id_token': auth_response['AuthenticationResult']['IdToken'],
                'refresh_token': auth_response['AuthenticationResult']['RefreshToken']
            })
        }

    except cognito_client.exceptions.NotAuthorizedException:
        return generate_error_response(401, 'Incorrect username or password')
    except cognito_client.exceptions.UserNotConfirmedException:
        return generate_error_response(403, 'User is not confirmed. Please confirm your email.')
    except cognito_client.exceptions.UserNotFoundException:
        return generate_error_response(404, 'User does not exist')
    except ClientError as e:
        error_message = e.response['Error'].get('Message', 'Unknown error')
        return generate_error_response(500, f'Error: {error_message}')
