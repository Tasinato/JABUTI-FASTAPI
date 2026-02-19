# 🐢 JABUTI – FastAPI Backend

Backend desenvolvido com **FastAPI**, gerenciado com **Poetry** e containerizado com **Docker Compose**.  
A aplicação segue arquitetura modular com separação clara de responsabilidades, preparada para ambientes escaláveis e produção.

---

## 🏗️ Arquitetura Geral (Host × Docker)

A aplicação é executada via Docker Compose, com separação entre:

- Cliente externo
- Host (localhost)
- Ambiente containerizado
- Rede interna Docker

### 🔌 Mapeamento de Portas

- Host → `8015`
- FastAPI (container) → `8000`
- PostgreSQL → `5432`
- Redis → `6379`

```mermaid
flowchart LR

    %% Cliente
    Client[Cliente\nBrowser / Postman]

    %% Host
    subgraph Host[Host - localhost]
        Port[Port 8015]
    end

    %% Docker Environment
    subgraph Docker[Docker Environment]
        
        subgraph Network[Docker Internal Network]
            API[FastAPI Container\nUvicorn :8000]
            DB[(PostgreSQL\n:5432)]
            Redis[(Redis\n:6379)]
        end

    end

    %% Fluxo
    Client -->|HTTP :8015| Port
    Port -->|8015:8000| API
    API --> DB
    API --> Redis
```

---

## 🔄 Fluxo Interno da Aplicação

A arquitetura segue o padrão Controller → SQLAlchemy ORM → Database, com camada opcional de cache.

```mermaid
sequenceDiagram
  autonumber
  participant Client
  participant Controller
  participant Redis
  participant ORM
  participant DB

  Client->>Controller: HTTP Request

  alt READ operation
      Controller->>Redis: GET cache_key

      alt Cache HIT
          Redis-->>Controller: cached data
      else Cache MISS
          Controller->>ORM: Query
          ORM->>DB: SQL read
          DB-->>ORM: Result
          ORM-->>Controller: Entities
          Controller->>Redis: SET cache (TTL)
      end

  else WRITE operation
      Controller->>ORM: Persist change
      ORM->>DB: SQL write
      DB-->>ORM: OK
      Controller->>Redis: invalidate list cache
      Controller->>Redis: update/delete id cache
  end

  Controller-->>Client: Response

```

---

## 📐 Estrutura do Projeto

```text
JABUTI-FASTAPI/
│
├── migrations/
│   └── versions/
│
├── src/
│   ├── main.py
│   │
│   ├── controllers/
│   │   └── user_controller.py
│   │
│   ├── core/
│   │   ├── settings.py
│   │   ├── logging_config.py
│   │   ├── middlewares.py
│   │   └── request_context.py
│   │
│   ├── models/
│   │   ├── database.py
│   │   └── user_model.py
│   │
│   ├── schemas/
│   │   └── user_schema.py
│   │
│   └── cache/
│       └── redis_client.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── .env.example
└── .gitignore

```

---

## 🚀 Stack Tecnológica

### Backend
- Python 3.14
- FastAPI
- Uvicorn

### Persistência
- PostgreSQL
- SQLAlchemy (async)
- Alembic

### Cache
- Redis

### Infraestrutura
- Docker
- Docker Compose

### Gerenciamento de Dependências
- Poetry
---

## 🐳 Execução com Docker (Recomendado)

```bash
docker compose build
docker compose up
```

Parar containers:

```bash
docker compose down
```

Aplicação disponível em:

```
http://localhost:8015
```

Documentação automática:

- Swagger UI → http://localhost:8015/docs  
- ReDoc → http://localhost:8015/redoc  

---

## ⚙️ Execução Local com Poetry (Opcional)

```bash
poetry install
uvicorn src.main:app --reload --port 8015
```

---

## 🔐 Configuração de Ambiente

Crie um arquivo `.env` baseado no modelo:

```bash
cp .env.example .env
```

Depois:

```bash
docker compose up --build
```

⚠️ O arquivo `.env` não deve ser versionado.

---
## 🧪 Como Testar o Cache (Redis)

O projeto utiliza estratégia **Cache-Aside** com Redis.

A chave utilizada para listagem segue o padrão:

```
usuarios:list:{limit}:{offset}:{sort}
```

Exemplo real:

```
usuarios:list:10:0:nome
```

### 🔹 1️⃣ Limpar o Redis

```bash
docker compose exec cache redis-cli flushall
```

---

### 🔹 2️⃣ Monitorar comandos do Redis

Abra um terminal separado:

```bash
docker compose exec cache redis-cli monitor
```

---

### 🔹 3️⃣ Fazer duas chamadas iguais na API

```bash
curl "http://localhost:8015/usuarios/?limit=10&offset=0&sort=nome"
curl "http://localhost:8015/usuarios/?limit=10&offset=0&sort=nome"
```

---

### 🔎 Resultado esperado

#### Primeira chamada (Cache MISS)

```
GET usuarios:list:10:0:nome
SET usuarios:list:10:0:nome ... EX 60
```

Isso indica que:

- Não havia cache
- Dados foram buscados no banco
- Resultado foi armazenado no Redis com TTL de 60 segundos

---

#### Segunda chamada (Cache HIT)

```
GET usuarios:list:10:0:nome
```

Observe que **não aparece SET novamente**.

Isso significa que a resposta foi servida diretamente do cache.

---

### 🔹 4️⃣ Verificar chave manualmente

Listar chaves:

```bash
docker compose exec cache redis-cli keys "usuarios:list:*"
```

Verificar TTL:

```bash
docker compose exec cache redis-cli ttl "usuarios:list:10:0:nome"
```

Obter valor armazenado:

```bash
docker compose exec cache redis-cli get "usuarios:list:10:0:nome"
```

---

## 🔁 Invalidação de Cache

Após operações de escrita (POST, PUT, DELETE), o cache da listagem é invalidado automaticamente:

```python
await cache_delete_prefix("usuarios:list")
```

Isso garante consistência entre banco e cache.

---

## ⏱ TTL Configurado

O tempo de expiração padrão está definido como:

```python
CACHE_TTL = 60  # segundos
```

Após esse período, o cache expira automaticamente e a próxima requisição será um novo MISS.
---

## 🏛️ Padrão Arquitetural

- Separação por camadas (Controller → Service → Repository)
- Organização modular
- Containerização
- Versionamento de banco com Alembic
- Integração com Redis para cache
- Estrutura preparada para evolução e escalabilidade

---

## 📦 Objetivo

Base profissional para backend com:

- Organização enterprise-ready
- Boas práticas de desenvolvimento
- Arquitetura preparada para crescimento

---

## 👤 Autor

**Rafael Tasinato**  
AI & Software Engineer
