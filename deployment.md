# 🚀 Paloma API — Guia de Deploy e Infraestrutura (GCP + Cloud Run + GitHub Actions)

Este documento registra a arquitetura de infraestrutura, os comandos de provisionamento e o histórico de resolução de problemas enfrentados na configuração do deploy contínuo da **Paloma API** no **Google Cloud Platform (GCP)**.

## 1. 🛠️ Arquitetura de Produção

- **Compute:** Google Cloud Run (Serverless, `southamerica-east1` — São Paulo).
- **Container Registry:** GCP Artifact Registry.
- **Build Engine:** Google Cloud Build.
- **Database:** PostgreSQL (Supabase).
- **CI/CD:** GitHub Actions com Google Cloud SDK e Service Accounts.

## 2. 📝 Configuração do Ambiente

### 2.1. Ativação de Serviços e Billing no GCP

Ajuste o projeto ativo e habilite as APIs necessárias.

#### 2.1.1. Definir o projeto ativo

```bash
gcloud config set project paloma-api-prod
```

#### 2.1.2. Habilitar as APIs principais

```bash
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### 2.2. Criar o Repositório Docker no Artifact Registry

```bash
gcloud artifacts repositories create paloma-repo \
  --repository-format=docker \
  --location=southamerica-east1 \
  --description="Imagens Docker da API Paloma"
```

### 2.3. Configurar Permissões de Build e Compute

Para permitir que o **Cloud Build** e a **Service Account padrão do Compute Engine** façam o push da imagem para o Artifact Registry, obtenha primeiro o número do projeto:

```bash
PROJECT_NUMBER=$(gcloud projects describe paloma-api-prod --format="value(projectNumber)")
```

#### 2.3.1. Permissão para a Service Account do Cloud Build

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

#### 2.3.2. Permissão para a Service Account padrão do Compute Engine

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

## 3. 🔐 Configuração do Pipeline de CI/CD (GitHub Actions)

### 3.1. Criar a Service Account Dedicada ao CI/CD

#### 3.1.1. Criar a conta de serviço

```bash
gcloud iam service-accounts create github-actions-deploy \
  --display-name="GitHub Actions Deploy SA"
```

#### 3.1.2. Atribuir as roles necessárias

Defina o e-mail da Service Account:

```bash
SA_EMAIL="github-actions-deploy@paloma-api-prod.iam.gserviceaccount.com"
```

Em seguida, atribua as permissões necessárias:

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/viewer"
```

### 3.2. Gerar a Chave JSON e Cadastrar nos Secrets do GitHub

Gere a chave JSON da Service Account:

```bash
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=github-actions-deploy@paloma-api-prod.iam.gserviceaccount.com
```

No GitHub, acesse **Settings → Secrets and variables → Actions** e cadastre os seguintes secrets:

| Secret | Descrição |
|---|---|
| `GCP_SA_KEY` | Conteúdo bruto do arquivo `gcp-key.json`. |
| `SECRET_KEY` | Chave secreta única do Django, gerada para produção. |
| `DATABASE_URL` | String de conexão do Supabase (`postgresql://...`). |

> **⚠️ Segurança:** nunca versione o arquivo `gcp-key.json` no repositório. Se ele for exposto, revogue a chave imediatamente.

### 3.3. Workflow de Deploy (`.github/workflows/deploy.yml`)

O workflow abaixo executa o build da imagem via Cloud Build e realiza o deploy no Cloud Run:

```yaml
name: CI/CD Pipeline - Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Build and Push Image via Cloud Build
        run: |
          gcloud builds submit . \
            --tag southamerica-east1-docker.pkg.dev/paloma-api-prod/paloma-repo/paloma-api:latest \
            --suppress-logs

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy paloma-api \
            --image=southamerica-east1-docker.pkg.dev/paloma-api-prod/paloma-repo/paloma-api:latest \
            --region=southamerica-east1 \
            --platform=managed \
            --allow-unauthenticated \
            --set-env-vars="DEBUG=False" \
            --set-env-vars="SECRET_KEY=${{ secrets.SECRET_KEY }}" \
            --set-env-vars="ALLOWED_HOSTS=*" \
            --set-env-vars="DATABASE_URL=${{ secrets.DATABASE_URL }}" \
            --set-env-vars="CSRF_TRUSTED_ORIGINS=https://paloma-api-783631601640.southamerica-east1.run.app" \
            --set-env-vars="SEED_ON_DEPLOY=false"
```

## 4. 📑 Ajustes no Código-Fonte do Django

### 4.1. Configuração do `CSRF_TRUSTED_ORIGINS` no `settings.py`

Essa configuração é necessária para evitar erros HTTP **403 — CSRF Verification Failed** no Django Admin quando a aplicação roda atrás do proxy reverso HTTPS do Cloud Run.

```python
import os

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'https://paloma-api-783631601640.southamerica-east1.run.app'
).split(',')
```

### 4.2. Gerar uma `SECRET_KEY` de Produção

A `SECRET_KEY` deve ser exclusiva para o ambiente de produção. Ela pode ser gerada localmente utilizando o comando abaixo:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 5. 💥 Diário de Bordo: Percalços e Soluções (Post-Mortem)

### 5.1. `ERROR: Invalid value for [source]: Dockerfile required when specifying --tag`

**Causa:** o comando `gcloud builds submit` foi executado em um diretório diferente da raiz onde estava localizado o `Dockerfile`, ou o contexto de build não foi informado corretamente.

**Solução:** navegar até a pasta raiz do projeto e especificar o diretório atual (`.`) como contexto:

```bash
gcloud builds submit . --tag ...
```

### 5.2. `denied: Permission "artifactregistry.repositories.uploadArtifacts" denied`

**Causa:** a Service Account do Cloud Build (`@cloudbuild.gserviceaccount.com`) e/ou a Service Account do Compute Engine não possuía permissão de escrita no Artifact Registry recém-criado.

**Solução:** atribuir explicitamente a role `roles/artifactregistry.writer` via IAM do projeto:

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### 5.3. `Forbidden (403) — CSRF verification failed` no Django Admin

**Causa:** versões modernas do Django validam o cabeçalho `Origin` em requisições POST. Como o Cloud Run realiza a terminação TLS/HTTPS no proxy reverso, a aplicação rejeita a requisição quando o domínio de origem não está na lista de origens confiáveis.

**Solução:** configurar `CSRF_TRUSTED_ORIGINS` no `settings.py`, lendo o valor a partir de uma variável de ambiente e incluindo explicitamente o protocolo (`https://`):

```python
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'https://paloma-api-783631601640.southamerica-east1.run.app'
).split(',')
```

### 5.4. Bloqueio no Git: `GH013: Repository rule violations found (Push Protection)`

**Causa:** o arquivo de credenciais sensíveis `gcp-key.json` foi commitado acidentalmente no histórico local do Git.

**Solução:**

1. Revogar/deletar a chave exposta no Console do GCP.
2. Adicionar `gcp-key.json` ao `.gitignore`.
3. Remover o arquivo do índice do Git:

```bash
git rm --cached gcp-key.json
```

4. Reescrever o último commit local:

```bash
git commit --amend
```

### 5.5. `The user is forbidden from accessing the bucket [paloma-api-prod_cloudbuild]`

**Causa:** a Service Account utilizada pelo GitHub Actions não possuía permissão para enviar o arquivo-fonte compactado (`.tgz`) para o bucket padrão do Cloud Build e consumir as APIs necessárias do GCP.

**Solução:** adicionar as roles `roles/storage.admin` e `roles/serviceusage.serviceUsageConsumer` à Service Account do CI/CD:

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

### 5.6. Trancamento de Logs no CLI: `This tool can only stream logs if you are Viewer/Owner`

**Causa:** o `gcloud builds submit` tenta fazer polling dos logs em tempo real durante o build. Se a Service Account não possuir acesso de leitura aos buckets/logs do Cloud Build, o comando pode sair com código de erro `1`.

**Solução:**

1. Adicionar a role `roles/viewer` à Service Account do GitHub Actions:

```bash
gcloud projects add-iam-policy-binding paloma-api-prod \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/viewer"
```

2. Adicionar a flag `--suppress-logs` ao comando do workflow para desativar a dependência do streaming de logs em um ambiente headless/CI.