import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import boto3  # Importando boto3 para garantir que o mock da região seja configurado

# Definir variáveis de ambiente antes da importação
os.environ["AWS_REGION"] = "us-east-1"
os.environ["COGNITO_USER_POOL_ID"] = "fake_id"

# Garantir que boto3 use a região definida
boto3.setup_default_session(region_name=os.environ["AWS_REGION"])

# Importar funções do módulo
from src.register.register import (
    lambda_handler,
    cognito_client,
    is_valid_email,
    normalize_body,
    validate_request,
    create_response,
)

class TestRegisterFunction(TestCase):

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_missing_user_name(self, mock_get_user):
        """Teste para quando `user_name` está ausente"""
        event = {"body": json.dumps({"password": "123456", "email": "testuser@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Missing required fields", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_missing_email(self, mock_get_user):
        """Teste para quando `email` está ausente"""
        event = {"body": json.dumps({"user_name": "testuser", "password": "123456"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Missing required fields", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_password_too_long(self, mock_get_user):
        """Teste para senha maior que 6 caracteres"""
        event = {"body": json.dumps({"user_name": "testuser", "password": "1234567", "email": "testuser@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Password must be exactly 6 characters long", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_invalid_email_format(self, mock_get_user):
        """Teste para email inválido"""
        event = {"body": json.dumps({"user_name": "testuser", "password": "123456", "email": "invalidemail"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Invalid email format", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_email_already_exists(self, mock_get_user):
        """Teste para email já cadastrado"""
        mock_get_user.return_value = {"user_name": "testuser@example.com"}

        event = {"body": json.dumps({"user_name": "testuser", "password": "123456", "email": "testuser@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Email already exists", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    @patch("src.register.register.cognito_client.admin_create_user")
    @patch("src.register.register.cognito_client.admin_set_user_password")
    def test_successful_registration(self, mock_set_password, mock_create_user, mock_get_user):
        """Teste para cadastro bem-sucedido"""
        mock_get_user.side_effect = cognito_client.exceptions.UserNotFoundException(
            {"Error": {"Code": "UserNotFoundException"}}, "AdminGetUser"
        )

        event = {"body": json.dumps({"user_name": "newuser", "password": "123456", "email": "newuser@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("User created successfully", response["body"]["message"])
        self.assertEqual(response["body"]["username"], "newuser")

        mock_create_user.assert_called_once()
        mock_set_password.assert_called_once()

    @patch("src.register.register.cognito_client.admin_get_user")
    @patch("src.register.register.cognito_client.admin_create_user")
    @patch("src.register.register.cognito_client.admin_set_user_password")
    def test_internal_server_error(self, mock_set_password, mock_create_user, mock_get_user):
        """Teste para erro interno no Cognito"""
        mock_get_user.side_effect = cognito_client.exceptions.UserNotFoundException(
            {"Error": {"Code": "UserNotFoundException"}}, "AdminGetUser"
        )
        mock_create_user.side_effect = ClientError(
            error_response={"Error": {"Code": "InternalError", "Message": "Internal server error"}},
            operation_name="AdminCreateUser",
        )

        event = {"body": json.dumps({"user_name": "newuser", "password": "123456", "email": "newuser@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Error: Internal server error", response["body"]["message"])

    @patch("src.register.register.cognito_client.admin_get_user")
    def test_user_name_already_exists(self, mock_get_user):
        """Teste para usuário já existente"""
        def side_effect(*args, **kwargs):
            if kwargs["Username"] == "existinguser":
                return {"username": "existinguser"}
            else:
                raise cognito_client.exceptions.UserNotFoundException(
                    {"Error": {"Code": "UserNotFoundException"}}, "AdminGetUser"
                )

        mock_get_user.side_effect = side_effect

        event = {"body": json.dumps({"user_name": "existinguser", "password": "123456", "email": "newemail@example.com"})}

        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("Username already exists", response["body"]["message"])

