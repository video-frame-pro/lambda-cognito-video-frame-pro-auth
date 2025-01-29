<p align="center">
  <img src="https://i.ibb.co/zs1zcs3/Video-Frame.png" width="30%" />
</p>


---

Este repositório contém a implementação da **lógica de autenticação do usuário** para o sistema de **gerenciamento de vídeos**. A autenticação é realizada através do **Amazon Cognito**, que gerencia o **registro**, **login** e a emissão de **tokens JWT** para autenticação.

---

## Cobertura atual dos testes

![Coverage](tests/reports/coverage.svg)

## Funções

Este projeto é composto por duas funções Lambdas que lidam com a autenticação do usuário:

1. **Registro de Usuário**: A função Lambda responsável por criar um novo usuário no **Cognito User Pool** com os dados fornecidos (nome de usuário, email e senha).
2. **Login de Usuário**: A função Lambda responsável por realizar o login do usuário, validar as credenciais e retornar o **token JWT** que pode ser usado para autenticação em outros serviços.

## Tecnologias

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/AWS_Lambda-4B5A2F?logo=aws-lambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/AWS_Cognito-FF9900?logo=aws-cognito&logoColor=white" alt="AWS Cognito" />
  <img src="https://img.shields.io/badge/API_Gateway-0052CC?logo=amazon-api-gateway&logoColor=white" alt="API Gateway" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Terraform-7B42BC?logo=terraform&logoColor=white" alt="Terraform" />
  <img src="https://img.shields.io/badge/GitHub-ACTION-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
</p>

## Estrutura do Repositório

```
/src
├── login
│   ├── lambda_function.py        # Lógica de login de usuário
│   ├── requirements.txt          # Dependências do Python para login
│   ├── __init__.py               # Inicialização do pacote
│
├── register
│   ├── lambda_function.py        # Lógica de registro de usuário
│   ├── requirements.txt          # Dependências do Python para registro
│   ├── __init__.py               # Inicialização do pacote
│
/infra
├── main.tf                      # Definição dos recursos AWS com Terraform
├── outputs.tf                   # Outputs das funções e recursos Terraform
├── variables.tf                 # Definições de variáveis Terraform
├── terraform.tfvars             # Arquivo com variáveis de ambiente
/tests
├── test_register.py             # Testes unitários para a função de registro
├── test_login.py                # Testes unitários para a função de login
```

## Como Funciona

1. **Função Lambda de Registro**:
    - O usuário envia uma requisição POST para o endpoint `/auth/register` com os dados necessários para o registro (nome de usuário, email e senha).
    - A função Lambda recebe esses dados e usa o serviço **Cognito** para registrar o usuário no **User Pool**.
    - Não é necessário estar autenticado para usar este endpoint.

2. **Função Lambda de Login**:
    - O usuário envia uma requisição POST para o endpoint `/auth/login` com as credenciais (nome de usuário e senha).
    - A função Lambda valida as credenciais no **Cognito**.
    - Se as credenciais forem válidas, o **Cognito** gera um token JWT que é retornado como resposta.
    - Este token JWT pode ser utilizado para autenticar outras requisições em endpoints protegidos.

## Passos para Configuração

### 1. Pré-Requisitos

Certifique-se de ter as credenciais da AWS configuradas corretamente e o **AWS CLI** instalado, além de ter o **Terraform** e **Python** instalados para o deploy da infraestrutura e funções Lambda.

### 2. Configuração do Cognito

- **User Pool**: Utilize o serviço **Amazon Cognito** para criar um **User Pool** que gerenciará os usuários da sua aplicação.
- **App Client**: Configure um **App Client** no Cognito para permitir a autenticação via credenciais (email e senha).
- **Identity Pool** (Opcional): Para integrar com outros serviços da AWS que exijam autenticação.

### 3. Deploy da Infraestrutura

1. No diretório `infra`, configure as variáveis no arquivo `terraform.tfvars`:
    - **cognito_user_pool_id**: ID do **User Pool** do Cognito.
    - **cognito_user_pool_arn**: ARN do **User Pool**.
    - **cognito_client_id**: ID do **App Client** no Cognito.

2. Execute o **Terraform** para provisionar os recursos na AWS:

```bash
cd infra
terraform init
terraform apply -auto-approve
```

Isso criará:
- As funções **Lambda** de **registro** e **login**.
- O **API Gateway** com os endpoints `/auth/register` e `/auth/login`.
- O **IAM Role** para conceder permissões às Lambdas.
- As políticas necessárias para as Lambdas interagirem com o **Cognito**.

### 4. Funções Lambda

- **Registro (POST `/auth/register`)**: A função de registro cria um novo usuário no **Cognito User Pool**.
- **Login (POST `/auth/login`)**: A função de login valida as credenciais e retorna um token JWT do **Cognito**.

### 5. Configuração de CI/CD (GitHub Actions)

Este projeto também configura um **CI/CD pipeline** usando **GitHub Actions** para automação do processo de deploy com **Terraform** e empacotamento das funções **Lambda**.

- **Passos do CI/CD**:
    1. Instala as dependências de Python (se houver).
    2. Empacota o código das Lambdas em arquivos ZIP.
    3. Executa o Terraform para provisionar a infraestrutura.

### Testes

Para testar a integração:

1. **Registro**:
    - Faça uma requisição POST para `/auth/register` com os parâmetros `username`, `email`, e `password`.
    - Exemplo de payload:

   ```json
   {
     "username": "novo_usuario",
     "email": "usuario@dominio.com",
     "password": "SenhaSegura123"
   }
   ```

2. **Login**:
    - Faça uma requisição POST para `/auth/login` com os parâmetros `username` e `password`.
    - Exemplo de payload:

   ```json
   {
     "username": "novo_usuario",
     "password": "SenhaSegura123"
   }
   ```

    - Resposta:

   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJub3ZvdXN1YXJpbyIsImVtYWlsIjoi..."
   }
   ```

## Autenticação e Segurança

- O **registro** não exige autenticação.
- O **login** exige que o usuário forneça credenciais válidas (nome de usuário e senha) e recebe um **token JWT**.
- Para acessar outros serviços protegidos, o **token JWT** deve ser incluído no cabeçalho da requisição como um **Bearer Token**.


## Executando Testes Unitários

Execute os testes e gere o relatório de cobertura:

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

---

## Contribuindo

Se você deseja contribuir para este projeto, fique à vontade para fazer um **fork**, criar uma **branch** e enviar suas alterações via **pull request**.

## Licença

Este projeto é licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---