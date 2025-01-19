import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from datetime import datetime
import boto3  # Importando boto3 para garantir que o mock da região seja configurado

# Defina as variáveis de ambiente **antes** da importação
os.environ['aws_region'] = 'us-east-1'
os.environ['cognito_user_pool_id'] = 'fake_id'
os.environ['cognito_client_id'] = 'fake_client_id'

# Garanta que o boto3 use a região definida
boto3.setup_default_session(region_name=os.environ['AWS_REGION'])

# Import the functions from your module
from src.register.register import lambda_handler, cognito_client, is_valid_email, generate_error_response

class TestRegisterFunction(TestCase):

    @patch('src.register.register.boto3.client')  # Mock do boto3.client
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_username(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'password': '123456',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: username', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_password(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'username': 'testuser',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: password', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_email(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '123456'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: email', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_password_too_long(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '1234567',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Password must be exactly 6 characters long', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_invalid_email_format(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '123456',
                'email': 'invalidemail'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid email format', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_email_already_exists(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        mock_get_user.return_value = {'Username': 'testuser@example.com'}

        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '123456',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Email already exists', response['body'])

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    @patch('src.register.register.cognito_client.admin_create_user')
    @patch('src.register.register.cognito_client.admin_set_user_password')
    def test_successful_registration(self, mock_set_password, mock_create_user, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        mock_get_user.side_effect = cognito_client.exceptions.UserNotFoundException({"Error": {"Code": "UserNotFoundException"}}, 'AdminGetUser')

        event = {
            'body': json.dumps({
                'username': 'newuser',
                'password': '123456',
                'email': 'newuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('User created successfully', response['body'])
        self.assertIn('newuser', response['body'])

        mock_create_user.assert_called_once()
        mock_set_password.assert_called_once()

    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    @patch('src.register.register.cognito_client.admin_create_user')
    @patch('src.register.register.cognito_client.admin_set_user_password')
    def test_internal_server_error(self, mock_set_password, mock_create_user, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        mock_get_user.side_effect = cognito_client.exceptions.UserNotFoundException({"Error": {"Code": "UserNotFoundException"}}, 'AdminGetUser')
        mock_create_user.side_effect = ClientError(
            error_response={'Error': {'Code': 'InternalError', 'Message': 'Internal server error'}},
            operation_name='AdminCreateUser'
        )

        event = {
            'body': json.dumps({
                'username': 'newuser',
                'password': '123456',
                'email': 'newuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Cognito error: Internal server error', response['body'])


    @patch('src.register.register.boto3.client')
    @patch('src.register.register.cognito_client.admin_get_user')
    def test_username_already_exists(self, mock_get_user, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula o retorno de usuário já existente
        def side_effect(*args, **kwargs):
            if kwargs['Username'] == 'existinguser':
                return {'Username': 'existinguser'}
            else:
                raise cognito_client.exceptions.UserNotFoundException({"Error": {"Code": "UserNotFoundException"}}, 'AdminGetUser')

        mock_get_user.side_effect = side_effect

        event = {
            'body': json.dumps({
                'username': 'existinguser',
                'password': '123456',
                'email': 'newemail@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Username already exists', response['body'])

    @patch('src.register.register.boto3.client')
    def test_invalid_json_body(self, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula um evento com JSON inválido
        event = {
            'body': '{"username": "testuser", "password": "123456", '  # JSON incompleto (malformado)
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid JSON in request body', response['body'])

