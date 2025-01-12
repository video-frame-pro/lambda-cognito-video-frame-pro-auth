from unittest.mock import patch, MagicMock
from unittest import TestCase
import json
from botocore.exceptions import ClientError
import os
from datetime import datetime

# Define the environment variable for testing
os.environ['COGNITO_USER_POOL_ID'] = 'us-east-1_ZL87UW5Jl'

# Import the functions from your module
from src.register.register import lambda_handler, cognito_client, is_valid_email, generate_error_response

class TestRegisterFunction(TestCase):

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_username(self, mock_get_user):
        event = {
            'body': json.dumps({
                'password': '123456',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: username', response['body'])

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_password(self, mock_get_user):
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: password', response['body'])

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_missing_email(self, mock_get_user):
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '123456'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: email', response['body'])

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_password_too_long(self, mock_get_user):
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': '1234567',
                'email': 'testuser@example.com'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Password must be at most 6 characters long', response['body'])

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_invalid_email_format(self, mock_get_user):
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

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_email_already_exists(self, mock_get_user):
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

    @patch('src.register.register.cognito_client.admin_get_user')
    @patch('src.register.register.cognito_client.admin_create_user')
    @patch('src.register.register.cognito_client.admin_set_user_password')
    def test_successful_registration(self, mock_set_password, mock_create_user, mock_get_user):
        # Simular UserNotFoundException para username e email
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

    @patch('src.register.register.cognito_client.admin_get_user')
    @patch('src.register.register.cognito_client.admin_create_user')
    @patch('src.register.register.cognito_client.admin_set_user_password')
    def test_internal_server_error(self, mock_set_password, mock_create_user, mock_get_user):
        # Simular falha no Cognito durante a criação do usuário
        mock_get_user.side_effect = cognito_client.exceptions.UserNotFoundException({"Error": {"Code": "UserNotFoundException"}}, 'AdminGetUser')
        mock_create_user.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'InternalError',
                    'Message': 'Internal server error'
                }
            },
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
        self.assertIn('Error: Internal server error', response['body'])

    @patch('src.register.register.cognito_client.admin_get_user')
    def test_username_already_exists(self, mock_get_user):
        # Simular que o username já existe
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
