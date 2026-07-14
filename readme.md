# Paloma - Sistema de Gestão de Manejo de Gado Leiteiro

Este guia orienta o setup e a execução manual do ambiente de desenvolvimento do projeto Paloma em sistemas Ubuntu.

## Pré-requisitos

Certifique-se de ter o Python 3 (recomendado >= 3.10) e o gerenciador de pacotes `pip` instalados no seu sistema:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Configuração do Ambiente
Siga os passos abaixo para clonar, isolar o ambiente e rodar a aplicação:

### 1. Clonar o repositório e acessar o diretório
```Bash
git clone <url-do-repositorio>
cd paloma
```

### 2. Criar e ativar o ambiente virtual (virtualenv)
Utilizamos o módulo nativo venv para isolamento das dependências.

```Bash
python3 -m venv .venv
source .venv/bin/activate
```

(Para desativar o ambiente posteriormente, basta executar o comando deactivate).

### 3. Instalar as dependências do projeto
Com a venv ativa, instale os pacotes listados no requirements.txt:

```Bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Banco de Dados & Migrations
Antes de subir o servidor pela primeira vez (ou após alterações nos modelos do Django), é necessário preparar e aplicar as migrações para estruturar o banco de dados.

### 1. Criar os arquivos de migração (se houver alterações em models)
```Bash
python manage.py makemigrations
```

### 2. Aplicar as migrações no banco de dados
```Bash
python manage.py migrate
```

### 3. Criar um usuário administrador (Opcional/Recomendado)
Para acessar o Django Admin (/admin), crie um superusuário local:

```Bash
python manage.py createsuperuser
```

## Executando a Aplicação
Para iniciar o servidor de desenvolvimento interno do Django, execute:

```Bash
python manage.py runserver
```

Por padrão, a aplicação estará acessível localmente em: http://127.0.0.1:8000/

Troubleshooting Comum no Ubuntu
Erro ao instalar pacotes com extensões em C (ex: drivers de banco de dados):
Se o _pip install_ falhar ao compilar alguma dependência, instale os pacotes de desenvolvimento do Ubuntu:

```Bash
sudo apt install python3-dev build-essential
```

## Testando a aplicação

Para criar alguns registros como usuários, fazendas, animais e ciclos reprodutivos inclusive permissões a usuários, 
rode o command 

```Bash
python manage.py seed_data
```

