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
    email = body.get('email')

    if not username or not password or not email:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required parameters'})
        }

    try:
        # Criar o usuário no Cognito via sign_up
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,  # ID do seu App Client
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}
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
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {e.response["Error"]["Message"]}'
            })
        }
