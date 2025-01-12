import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Defina as variáveis de ambiente **antes** da importação
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['COGNITO_USER_POOL_ID'] = 'fake_id'
os.environ['COGNITO_CLIENT_ID'] = 'fake_client_id'

from src.login.login import lambda_handler, cognito_client

class TestLogin(TestCase):

    @patch('src.login.login.boto3.client')  # Mock do boto3.client para interceptar a criação do cognito_client
    @patch('src.login.login.cognito_client.initiate_auth')  # Mock para a função initiate_auth
    def test_successful_login(self, mock_initiate_auth, mock_boto_client):
        # Mockando o cliente Cognito retornado pelo boto3
        mock_cognito = MagicMock()
        mock_boto_client.return_value = mock_cognito
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

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_missing_username_or_email(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: username or email', response['body'])

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_missing_password(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'username': 'testuser'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: password', response['body'])

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_invalid_email_format(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'email': 'invalidemail',
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid email format', response['body'])

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_client_error(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
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
