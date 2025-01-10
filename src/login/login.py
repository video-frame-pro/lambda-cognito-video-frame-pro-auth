import json
import boto3
import os
from botocore.exceptions import ClientError

# Configuração do Cognito
cognito_client = boto3.client('cognito-idp')

# Recuperar o ID do Pool de Usuários e o Client ID a partir das variáveis de ambiente
USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']
CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

def lambda_handler(event, context):
    # Parse do corpo da requisição (POST)
    body = json.loads(event['body'])

    # Verificar se os parâmetros obrigatórios estão presentes
    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required parameters'})
        }

    try:
        # Realizar a autenticação no Cognito via initiate_auth
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
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
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Invalid username or password'})
        }
