import json
import boto3
import os
import re
from botocore.exceptions import ClientError
import logging

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o Client ID do Cognito a partir das variáveis de ambiente
COGNITO_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

def is_valid_email(email):
    """Valida o formato do email"""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def generate_error_response(status_code, message):
    """Gera uma resposta de erro padrão e registra o log"""
    logger.error(f"Error response generated - Status: {status_code}, Message: {message}")
    return {
        'statusCode': status_code,
        'body': json.dumps({'error': message})
    }

def lambda_handler(event, context):
    logger.info("Lambda function invoked")

    # Parse do corpo da requisição
    try:
        body = json.loads(event['body'])
        logger.info(f"Request body parsed successfully: {body}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return generate_error_response(400, 'Invalid JSON in request body')

    # Recuperar parâmetros obrigatórios
    login_identifier = body.get('user_name') or body.get('email')
    password = body.get('password')

    if not login_identifier:
        logger.warning("Missing parameter: user_name or email")
        return generate_error_response(400, 'Missing parameter: user_name or email')
    if not password:
        logger.warning("Missing parameter: password")
        return generate_error_response(400, 'Missing parameter: password')
    if body.get('email') and not is_valid_email(body['email']):
        logger.warning(f"Invalid email format: {body['email']}")
        return generate_error_response(400, 'Invalid email format')

    try:
        # Tentar autenticar o usuário
        logger.info(f"Attempting to authenticate user: {login_identifier}")
        auth_response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': login_identifier,
                'PASSWORD': password
            }
        )
        logger.info(f"Authentication successful for user: {login_identifier}")

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
        logger.warning(f"Incorrect username or password for user: {login_identifier}")
        return generate_error_response(401, 'Incorrect username or password')
    except cognito_client.exceptions.UserNotConfirmedException:
        logger.warning(f"User not confirmed: {login_identifier}")
        return generate_error_response(403, 'User is not confirmed. Please confirm your email.')
    except cognito_client.exceptions.UserNotFoundException:
        logger.warning(f"User does not exist: {login_identifier}")
        return generate_error_response(404, 'User does not exist')
    except ClientError as e:
        error_code = e.response['Error'].get('Code', 'UnknownCode')
        error_message = e.response['Error'].get('Message', 'Unknown error')
        logger.error(f"ClientError occurred - Code: {error_code}, Message: {error_message}")
        return generate_error_response(500, f'Error: {error_message}')
