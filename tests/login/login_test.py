import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import boto3  # Importando boto3 para garantir que o mock da região seja configurado

# Defina as variáveis de ambiente **antes** da importação
os.environ['aws_region'] = 'us-east-1'
os.environ['cognito_user_pool_id'] = 'fake_id'
os.environ['cognito_client_id'] = 'fake_client_id'

# Garanta que o boto3 use a região definida
boto3.setup_default_session(region_name=os.environ['aws_region'])

from src.login.login import lambda_handler, cognito_client

class TestLogin(TestCase):

    @patch('src.login.login.boto3.client')  # Mock do boto3.client para interceptar a criação do cognito_client
    @patch('src.login.login.cognito_client.initiate_auth')  # Mock para a função initiate_auth
    def test_successful_login(self, mock_initiate_auth, mock_boto_client):
        # Mockando o cliente Cognito retornado pelo boto3
        mock_cognito = MagicMock()
        mock_boto_client.return_value = mock_cognito
        mock_initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'access_token_example',
                'IdToken': 'id_token_example',
                'RefreshToken': 'refresh_token_example'
            }
        }

        event = {
            'body': json.dumps({
                'user_name': 'testuser',
                'password': 'testpassword'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Login successful', response['body'])
        self.assertIn('access_token_example', response['body'])


    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_missing_user_name_or_email(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'password': 'testpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameter: user_name or email', response['body'])

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_missing_password(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        event = {
            'body': json.dumps({
                'user_name': 'testuser'
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
            error_response={'Error': {'Code': 'NotAuthorizedException', 'Message': 'Incorrect user_name or password'}},
            operation_name='InitiateAuth'
        )

        event = {
            'body': json.dumps({
                'user_name': 'testuser',
                'password': 'wrongpassword'
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Incorrect user_name or password', response['body'])

    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_incorrect_user_name_or_password(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula uma exceção NotAuthorizedException
        mock_initiate_auth.side_effect = cognito_client.exceptions.NotAuthorizedException(
            {"Error": {"Code": "NotAuthorizedException", "Message": "Incorrect user_name or password"}},
            'InitiateAuth'
        )

        event = {
            'body': json.dumps({
                'user_name': 'testuser',
                'password': 'wrongpassword'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 401)
        self.assertIn('Incorrect username or password', response['body'])


    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_user_not_confirmed(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula uma exceção UserNotConfirmedException
        mock_initiate_auth.side_effect = cognito_client.exceptions.UserNotConfirmedException(
            {"Error": {"Code": "UserNotConfirmedException", "Message": "User is not confirmed"}},
            'InitiateAuth'
        )

        event = {
            'body': json.dumps({
                'user_name': 'testuser',
                'password': 'testpassword'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 403)
        self.assertIn('User is not confirmed. Please confirm your email.', response['body'])


    @patch('src.login.login.boto3.client')
    @patch('src.login.login.cognito_client.initiate_auth')
    def test_user_not_found(self, mock_initiate_auth, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula uma exceção UserNotFoundException
        mock_initiate_auth.side_effect = cognito_client.exceptions.UserNotFoundException(
            {"Error": {"Code": "UserNotFoundException", "Message": "User does not exist"}},
            'InitiateAuth'
        )

        event = {
            'body': json.dumps({
                'user_name': 'nonexistentuser',
                'password': 'testpassword'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('User does not exist', response['body'])


    @patch('src.login.login.boto3.client')
    def test_invalid_json_body(self, mock_boto_client):
        mock_boto_client.return_value = MagicMock()

        # Simula um evento com JSON inválido
        event = {
            'body': '{"user_name": "testuser", "password": '  # JSON malformado
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid JSON in request body', response['body'])
