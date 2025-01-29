import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import boto3  # Importando boto3 para garantir que o mock da região seja configurado

# Definir variáveis de ambiente antes da importação
os.environ["AWS_REGION"] = "us-east-1"
os.environ["COGNITO_USER_POOL_ID"] = "fake_id"
os.environ["COGNITO_CLIENT_ID"] = "fake_client_id"

# Garantir que boto3 use a região definida
boto3.setup_default_session(region_name=os.environ["AWS_REGION"])

# Importar funções do módulo
from src.login.login import (
    lambda_handler,
    cognito_client,
    create_response,
    normalize_body,
    validate_request,
)


class TestLogin(TestCase):

    @patch("src.login.login.cognito_client.initiate_auth")
    def test_successful_login(self, mock_initiate_auth):
        """Testa um login bem-sucedido"""
        mock_initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "access_token_example",
                "IdToken": "id_token_example",
                "RefreshToken": "refresh_token_example",
            }
        }

        event = {"body": json.dumps({"user_name": "testuser", "password": "testpassword", "email": "test@example.com"})}
        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Login successful", response["body"]["message"])
        self.assertIn("access_token", response["body"])


    def test_invalid_email_format(self):
        """Testa erro ao fornecer um e-mail inválido"""
        event = {"body": json.dumps({"user_name": "testuser", "password": "testpassword", "email": "invalidemail"})}
        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Invalid email format", response["body"]["message"])

    @patch("src.login.login.cognito_client.initiate_auth")
    def test_user_not_confirmed(self, mock_initiate_auth):
        """Testa erro quando o usuário não confirmou o e-mail"""
        mock_initiate_auth.side_effect = cognito_client.exceptions.UserNotConfirmedException(
            {"Error": {"Code": "UserNotConfirmedException", "Message": "User is not confirmed"}}, "InitiateAuth"
        )

        event = {"body": json.dumps({"user_name": "testuser", "password": "testpassword", "email": "test@example.com"})}
        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 403)
        self.assertIn("User is not confirmed", response["body"]["message"])

    @patch("src.login.login.cognito_client.initiate_auth")
    def test_user_not_found(self, mock_initiate_auth):
        """Testa erro quando o usuário não existe no Cognito"""
        mock_initiate_auth.side_effect = cognito_client.exceptions.UserNotFoundException(
            {"Error": {"Code": "UserNotFoundException", "Message": "User does not exist"}}, "InitiateAuth"
        )

        event = {"body": json.dumps({"user_name": "nonexistentuser", "password": "testpassword", "email": "test@example.com"})}
        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("User does not exist", response["body"]["message"])

    def test_validate_request_missing_password(self):
        """Testa erro ao chamar validate_request sem o campo obrigatório"""
        with self.assertRaises(ValueError) as context:
            validate_request({})
        self.assertEqual(str(context.exception), "Missing required fields: password")

    def test_normalize_body_valid_dict(self):
        """Testa se normalize_body retorna corretamente um dicionário"""
        event = {"body": {"email": "test@example.com"}}
        body = normalize_body(event)
        self.assertEqual(body, {"email": "test@example.com"})

    def test_normalize_body_invalid(self):
        """Testa se normalize_body levanta erro quando o body está ausente"""
        with self.assertRaises(ValueError) as context:
            normalize_body({"body": None})
        self.assertEqual(str(context.exception), "Request body is missing or invalid.")
