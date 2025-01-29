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
cognito_client = boto3.client("cognito-idp")

# Recuperar o ID do Pool de Usuários a partir das variáveis de ambiente
COGNITO_USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]

def create_response(status_code, message=None, data=None):
    """
    Gera uma resposta formatada.
    """
    response = {"statusCode": status_code, "body": {}}
    if message:
        response["body"]["message"] = message
    if data:
        response["body"].update(data)
    return response

def normalize_body(event):
    """
    Normaliza o corpo da requisição para garantir que seja um dicionário.
    """
    if isinstance(event.get("body"), str):
        return json.loads(event["body"])  # Desserializa string JSON para dicionário
    elif isinstance(event.get("body"), dict):
        return event["body"]  # Já está em formato de dicionário
    else:
        raise ValueError("Request body is missing or invalid.")

def validate_request(body):
    """
    Valida os campos obrigatórios na requisição.
    """
    required_fields = ["user_name", "password", "email"]
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # Valida o formato do email
    if not is_valid_email(body["email"]):
        raise ValueError("Invalid email format")

    # Valida tamanho da senha
    if len(body["password"]) != 6:
        raise ValueError("Password must be exactly 6 characters long")

def is_valid_email(email):
    """Função para validar o formato do email"""
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def lambda_handler(event, context):
    logger.info("Lambda function invoked")

    try:
        # Normalizar e validar o corpo da requisição
        body = normalize_body(event)
        validate_request(body)
        logger.info(f"Request body validated successfully: {body}")

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return create_response(400, str(ve))

    # Recuperar parâmetros obrigatórios
    username = body["user_name"]
    password = body["password"]
    email = body["email"]

    # Verificar se o email já existe
    try:
        logger.info(f"Checking if email {email} already exists in Cognito")
        cognito_client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email
        )
        return create_response(400, "Email already exists")
    except cognito_client.exceptions.UserNotFoundException:
        logger.info(f"Email {email} does not exist. Proceeding.")

    # Verificar se o username já existe
    try:
        logger.info(f"Checking if username {username} already exists in Cognito")
        cognito_client.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username
        )
        return create_response(400, "Username already exists")
    except cognito_client.exceptions.UserNotFoundException:
        logger.info(f"Username {username} does not exist. Proceeding.")

    try:
        # Obter a hora atual no formato Unix timestamp
        current_time = int(datetime.utcnow().timestamp())
        logger.info(f"Current timestamp: {current_time}")

        # Criar o usuário no Cognito via admin_create_user
        logger.info(f"Creating user {username} with email {email}")
        response = cognito_client.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            UserAttributes=[
                {"Name": "name", "Value": username},
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "True"},  # Marcar o email como verificado
                {"Name": "updated_at", "Value": str(current_time)}
            ],
            MessageAction="SUPPRESS",
        )
        logger.info(f"User creation response: {response}")

        # Definir a senha permanente para o usuário
        logger.info(f"Setting password for user {username}")
        cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            Password=password,
            Permanent=True
        )

        logger.info(f"User {username} created successfully")
        return create_response(
            200,
            "User created successfully",
            {"username": username}
        )

    except ClientError as e:
        error_message = e.response["Error"].get("Message", "Unknown error")
        logger.error(f"ClientError occurred: {error_message}")
        return create_response(500, f"Error: {error_message}")
