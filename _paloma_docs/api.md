# Documentação da API REST - Paloma Backend

**Versão da API**: 1.0  
**Autenticação**: Bearer Token (JWT via header `Authorization: Bearer <access_token>`)  
**Content-Type**: `application/json`

---

## Sumário
1. [Visão Geral & Convenção de Erros](#1-visão-geral--convenção-de-erros)
2. [Módulo: Autenticação & Usuários (`users`)](#2-módulo-autenticação--usuários-users)
3. [Módulo: Fazendas (`farms`)](#3-módulo-fazendas-farms)
4. [Módulo: Animais (`animals`)](#4-módulo-animais-animals)
5. [Módulo: Reprodução (`reproduction`)](#5-módulo-reprodução-reproduction)
6. [Módulo: Notificações (`notifications`)](#6-módulo-notificações-notifications)

---

## 1. Visão Geral & Convenção de Erros

### Headers Globais Exigidos
A menos que a rota seja explicitamente pública (`AllowAny`), todas as requisições devem enviar os seguintes cabeçalhos HTTP:

```http
Authorization: Bearer <seu_jwt_access_token>
Content-Type: application/json
```

### Formato Padrão de Respostas de Erro (DRF)

#### 1. Erros de Validação (HTTP 400 Bad Request)
Ocorrem quando os dados do payload enviado violam regras do modelo, tipos de dados ou regras de negócio do backend:
```json
{
  "nome_do_campo": [
    "Este campo é obrigatório."
  ],
  "outro_campo": [
    "Mensagem de validação específica."
  ]
}
```

#### 2. Erros de Autenticação (HTTP 401 Unauthorized)
Ocorrem quando o token não é enviado, expirou ou é inválido:
```json
{
  "detail": "As credenciais de autenticação não foram fornecidas."
}
```
ou
```json
{
  "detail": "O token é inválido ou expirou",
  "code": "token_not_valid"
}
```

#### 3. Erro de Permissão (HTTP 403 Forbidden)
Ocorrem quando o usuário autenticado tenta acessar ou modificar um recurso ao qual não tem direito:
```json
{
  "detail": "Você não tem permissão para executar esta ação."
}
```

#### 4. Recurso Não Encontrado (HTTP 404 Not Found)
Ocorrem quando o ID fornecido na URL não existe no banco de dados ou não pertence ao usuário/fazenda atual:
```json
{
  "detail": "Não encontrado."
}
```

---

## 2. Módulo: Autenticação & Usuários (`users`)

Prefixos das rotas: `/api/v1/` (ou caminho base de auth do seu projeto)

### 2.1 Cadastrar Novo Usuário
Cria uma nova conta no sistema.

* **URL**: `/register/`
* **Método**: `POST`
* **Permissão**: Pública (`AllowAny`)

#### Body (JSON):
```json
{
  "name": "João da Silva",
  "email": "joao@example.com",
  "password": "suaPasswordSegura123"
}
```

#### Respostas:
* **201 Created**:
  ```json
  {
    "message": "User created successfully."
  }
  ```
* **400 Bad Request**:
  ```json
  {
    "email": [
      "user com este email já existe."
    ],
    "password": [
      "Este campo é obrigatório."
    ]
  }
  ```

---

### 2.2 Autenticação / Login
Gera o par de tokens JWT (`access` e `refresh`) e retorna os dados do perfil do usuário com as suas fazendas associadas.

* **URL**: `/login/`
* **Método**: `POST`
* **Permissão**: Pública (`AllowAny`)

#### Body (JSON):
```json
{
  "email": "joao@example.com",
  "password": "suaPasswordSegura123"
}
```

#### Respostas:
* **200 OK**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_data": {
      "id": 1,
      "name": "João da Silva",
      "email": "joao@example.com",
      "farms": [
        {
          "id": 10,
          "name": "Fazenda Santa Maria",
          "image": null,
          "address": 5,
          "users": [1]
        }
      ]
    }
  }
  ```
* **401 Unauthorized**:
  ```json
  {
    "detail": "Nenhuma conta ativa encontrada com as credenciais fornecidas"
  }
  ```

---

### 2.3 Atualizar Access Token (Refresh)
Renova o token de acesso (`access`) expirado utilizando um `refresh` token válido.

* **URL**: `/token/refresh/`
* **Método**: `POST`
* **Permissão**: Pública (`AllowAny`)

#### Body (JSON):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Respostas:
* **200 OK**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
* **401 Unauthorized**:
  ```json
  {
    "detail": "O token é inválido ou expirou",
    "code": "token_not_valid"
  }
  ```

---

### 2.4 Logout (Invalidação do Refresh Token)
Insere o token de refresh na lista negra (blacklist), invalidando-o.

* **URL**: `/logout/`
* **Método**: `POST`
* **Permissão**: Pública (`AllowAny`) ou Autenticado

#### Body (JSON):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Respostas:
* **200 OK**:
  ```json
  {}
  ```

---

## 3. Módulo: Fazendas (`farms`)

### 3.1 Listar Fazendas do Usuário
Retorna apenas as fazendas vinculadas ao usuário logado.

* **URL**: `/farms/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`, `IsOwnerPermission`)

#### Respostas:
* **200 OK**:
  ```json
  [
    {
      "id": 10,
      "name": "Fazenda Santa Maria",
      "image": "http://servidor/media/farms/foto.jpg",
      "address": 5,
      "users": [1, 2]
    }
  ]
  ```

---

### 3.2 Criar Fazenda
Cria uma fazenda e define automaticamente o usuário autenticado como proprietário (`is_owner=True`).

* **URL**: `/farms/`
* **Método**: `POST`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Body (JSON):
```json
{
  "name": "Fazenda Bela Vista",
  "image": null,
  "address": {
    "street": "Rodovia BR-277",
    "number": "KM 10",
    "city": "Guarapuava",
    "state": "PR",
    "zip_code": "85000-000"
  }
}
```

#### Respostas:
* **201 Created**:
  ```json
  {
    "id": 11,
    "name": "Fazenda Bela Vista",
    "image": null,
    "address": 6,
    "users": [1]
  }
  ```

---

### 3.3 Obter, Atualizar ou Deletar Fazenda

* **Obter Detalhes**: `GET /farms/{id}/`
* **Atualizar Completo**: `PUT /farms/{id}/`
* **Atualizar Parcial**: `PATCH /farms/{id}/`
* **Remover**: `DELETE /farms/{id}/`

#### Resposta de Remoção (204 No Content):
Sem corpo na resposta.

---

### 3.4 Gerenciamento de Endereços (`addresses`)
O app disponibiliza um CRUD completo para o recurso de Endereços:
* `GET /addresses/` (Listar)
* `POST /addresses/` (Criar)
* `GET /addresses/{id}/` (Detalhar)
* `PUT /addresses/{id}/` ou `PATCH /addresses/{id}/` (Editar)
* `DELETE /addresses/{id}/` (Excluir)

---

## 4. Módulo: Animais (`animals`)

### 4.1 Listar e Filtrar Animais
Retorna os animais pertencentes às fazendas do usuário autenticado.

* **URL**: `/animals/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)
* **Query Parameters (Filtros - `AnimalFilter`)**:
  * `farm` (int): Filtrar por ID da fazenda.
  * `sex` (string): `female` ou `male`.
  * `status` (int): ID do status do animal.
  * `breed` (int): ID da raça.
  * `classification` (int): ID da classificação.
  * `is_active` (boolean): `true` ou `false`.
  * `is_alive` (boolean): `true` ou `false`.
  * `search` (string): Pesquisa no nome ou brinco/código do animal.

#### Respostas:
* **200 OK**:
  ```json
  [
    {
      "id": 45,
      "name": "Mimosa",
      "code": "BR-202",
      "sex": "female",
      "born_date": "2023-01-15",
      "farm": 10,
      "mother": 12,
      "father": null,
      "breed": 1,
      "classification": 3,
      "status": 1,
      "is_active": true,
      "is_alive": true
    }
  ]
  ```

---

### 4.2 Criar Animal
* **URL**: `/animals/`
* **Método**: `POST`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Body (JSON):
```json
{
  "name": "Mimosa",
  "code": "BR-202",
  "sex": "female",
  "born_date": "2023-01-15",
  "farm": 10,
  "mother": 12,
  "father": 15,
  "breed": 1,
  "classification": 3,
  "status": 1
}
```

#### Respostas:
* **201 Created**: Objeto do animal recém-criado.
* **400 Bad Request (Acesso negado à fazenda informada)**:
  ```json
  {
    "farm": "Você não tem permissão para criar animais nesta fazenda."
  }
  ```

---

### 4.3 Atualizar Animal
* **URL**: `/animals/{id}/`
* **Método**: `PUT` ou `PATCH`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Respostas:
* **200 OK**: Objeto atualizado.
* **400 Bad Request (Tentativa de alteração para fazenda não autorizada)**:
  ```json
  {
    "farm": "Você não tem permissão para mover animais para esta fazenda."
  }
  ```

---

### 4.4 Listar Matrizes e Touros Aprovados (`parents`)
Retorna apenas os animais das fazendas do usuário que estão ativos, vivos, de classificação reprodutível e com idade mínima de 1 ano (365 dias).

* **URL**: `/parents/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)
* **Query Parameters**:
  * `sex` (**obrigatório**): `female` (para buscar fêmeas aptas) ou `male` (para buscar machos aptos).

#### Exemplo de Requisição:
`GET /parents/?sex=female`

#### Respostas:
* **200 OK**:
  ```json
  [
    {
      "id": 12,
      "name": "Estrela",
      "code": "MAT-01",
      "sex": "female",
      "born_date": "2021-03-10"
    }
  ]
  ```
* **Nota**: Se o parâmetro `sex` não for informado ou for diferente de `female` ou `male`, a API retornará uma lista vazia `[]`.

---

### 4.5 Endpoints Auxiliares de Consulta (Somente Leitura - `ReadOnlyModelViewSet`)
Tabelas de domínio do sistema acessíveis via `GET`:

* **Raças**: `GET /breeds/` | `GET /breeds/{id}/`
* **Classificações**: `GET /classifications/` | `GET /classifications/{id}/`
* **Status**: `GET /statuses/` | `GET /statuses/{id}/`

---

## 5. Módulo: Reprodução (`reproduction`)

### 5.1 Doadoras / Doadores de Sêmen (`donors`)
Gerenciamento do catálogo de doadores de sêmen/palhetas para inseminação artificial (IA / IATF).

* `GET /donors/` (Listar)
* `POST /donors/` (Criar)
* `GET /donors/{id}/` (Detalhar)
* `PUT /donors/{id}/` ou `PATCH /donors/{id}/` (Editar)
* `DELETE /donors/{id}/` (Remover)

---

### 5.2 Listar e Filtrar Ciclos Reprodutivos
Retorna os ciclos de reprodução vinculados às fêmeas mantidas nas fazendas do usuário.

* **URL**: `/reproductions/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)
* **Query Parameters (Filtros - `ReproductionCycleFilter`)**:
  * `female_animal` (int): ID da matriz fêmea.
  * `male_animal` (int): ID do touro.
  * `type` (string): Tipo da cobertura/inseminação.
  * `status` (string): Status do ciclo (ex: `pending`, `confirmed`, `calved`).

#### Respostas:
* **200 OK**:
  ```json
  [
    {
      "id": 1,
      "female_animal": 12,
      "male_animal": 15,
      "semen_donor": null,
      "breeding_date": "2026-01-10",
      "predicted_calving_date": "2026-10-18",
      "actual_calving_date": null,
      "status": "confirmed",
      "calf_born": null
    }
  ]
  ```

---

### 5.3 Criar Ciclo Reprodutivo
Registra a cobertura/inseminação. Calcula e retorna a data estimada de parto (`predicted_calving_date`).

* **URL**: `/reproductions/`
* **Método**: `POST`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Body (JSON):
```json
{
  "female_animal": 12,
  "male_animal": 15,
  "semen_donor": null,
  "breeding_date": "2026-01-10",
  "notes": "Procedimento de IATF realizado com sucesso."
}
```

#### Respostas:
* **201 Created**:
  ```json
  {
    "id": 1,
    "female_animal": 12,
    "male_animal": 15,
    "semen_donor": null,
    "breeding_date": "2026-01-10",
    "predicted_calving_date": "2026-10-18",
    "actual_calving_date": null,
    "status": "pending",
    "calf_born": null,
    "message": "Ciclo reprodutivo criado com sucesso! Data prevista do parto: 2026-10-18"
  }
  ```
* **400 Bad Request (Validação de permissão da fazenda)**:
  ```json
  {
    "female_animal_id": "Você não tem permissão para gerenciar ciclos para esta fêmea."
  }
  ```
  ou
  ```json
  {
    "male_animal_id": "Você não tem permissão para utilizar este touro."
  }
  ```

---

### 5.4 Atualizar Ciclo Reprodutivo
* **URL**: `/reproductions/{id}/`
* **Método**: `PUT` ou `PATCH`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

Valida novamente se o usuário é proprietário da fazenda dos animais vinculados no payload (mesmo no envio parcial via `PATCH`).

---

## 6. Módulo: Notificações (`notifications`)

As notificações são geradas pelo backend e consumidas pelo usuário logado. O usuário pode alterar o estado de leitura das mensagens.

### 6.1 Listar Notificações do Usuário
Retorna **apenas** as notificações atribuídas ao usuário autenticado.

* **URL**: `/notifications/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)
* **Query Parameters**:
  * `is_read` (boolean): `true` (listar apenas lidas) ou `false` (listar apenas pendentes/não lidas).

#### Respostas:
* **200 OK**:
  ```json
  [
    {
      "id": 88,
      "user": 1,
      "farm": 10,
      "category": "reproduction",
      "category_display": "Reprodução e Partos",
      "priority": "high",
      "priority_display": "Alta / Crítica",
      "title": "Aviso de Parto Próximo: Mimosa",
      "message": "A fêmea Mimosa (BR-202) está prevista para parir em 12/09/2026.",
      "target_object_type": "animal",
      "target_object_id": 45,
      "is_read": false,
      "read_at": null,
      "created_at": "2026-09-06T10:30:00Z"
    }
  ]
  ```

---

### 6.2 Detalhar Notificação
* **URL**: `/notifications/{id}/`
* **Método**: `GET`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

---

### 6.3 Marcar Notificação Especifica como Lida (`mark_as_read`)
Altera o estado de leitura da notificação para `is_read=True` e preenche a data atual no campo `read_at`.

* **URL**: `/notifications/{id}/mark_as_read/`
* **Método**: `PATCH`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Respostas:
* **200 OK**:
  ```json
  {
    "status": "notificação lida"
  }
  ```

---

### 6.4 Marcar TODAS as Notificações como Lidas (`mark_all_as_read`)
Atualiza em lote todas as notificações não lidas (`is_read=False`) do usuário logado.

* **URL**: `/notifications/mark_all_as_read/`
* **Método**: `PATCH`
* **Permissão**: Requer Autenticação (`IsAuthenticated`)

#### Respostas:
* **200 OK**:
  ```json
  {
    "status": "todas as notificações foram marcadas como lidas"
  }
  ```