import json
import os
from unittest import TestCase
from unittest.mock import patch
from botocore.exceptions import ClientError

os.environ['COGNITO_USER_POOL_ID'] = 'us-east-1_ZL87UW5Jl'

from src.login.login import lambda_handler, cognito_client

class TestLogin(TestCase):

    def setUp(self):
        # Configurar as variáveis de ambiente para cada teste individualmente
        os.environ['COGNITO_USER_POOL_ID'] = 'your_user_pool_id'
        os.environ['COGNITO_CLIENT_ID'] = 'your_client_id'

    @patch('src.login.login.cognito_client.initiate_auth')  # Corrigir o caminho do mock
    def test_successful_login(self, mock_initiate_auth):
        mock_initiate_auth.return_value = {'AuthenticationResult': 'some_auth_token'}
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Login successful', response['body'])

    @patch('src.login.login.cognito_client.initiate_auth')  # Corrigir o caminho do mock
    def test_missing_username_or_email(self, mock_initiate_auth):
        event = {
            'body': json.dumps({
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: username or email', response['body'])

    @patch('src.login.login.cognito_client.initiate_auth')  # Corrigir o caminho do mock
    def test_missing_password(self, mock_initiate_auth):
        event = {
            'body': json.dumps({
                'username': 'testuser'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: password', response['body'])

    @patch('src.login.login.cognito_client.initiate_auth')  # Corrigir o caminho do mock
    def test_invalid_email_format(self, mock_initiate_auth):
        event = {
            'body': json.dumps({
                'email': 'invalidemail',
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid email format', response['body'])

    @patch('src.login.login.cognito_client.initiate_auth')  # Corrigir o caminho do mock
    def test_client_error(self, mock_initiate_auth):
        mock_initiate_auth.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect username or password'}},
            operation_name='InitiateAuth'
        )
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Incorrect username or password', response['body'])
