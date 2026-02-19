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

A arquitetura segue o padrão Controller → Service → Repository/Model, com camada opcional de cache.

```mermaid
sequenceDiagram
  autonumber
  participant C as Client
  participant CTRL as Controller
  participant SVC as Service
  participant M as Repository
  participant DB as PostgreSQL
  participant R as Redis

  C->>CTRL: HTTP Request
  CTRL->>SVC: Encaminha regra de negócio
  SVC->>R: Verifica cache

  alt Cache HIT
    R-->>SVC: Retorna dados
  else Cache MISS
    SVC->>M: Query/Command
    M->>DB: SQL (async)
    DB-->>M: Resultado
    M-->>SVC: Entidade
    SVC->>R: Atualiza cache
  end

  SVC-->>CTRL: DTO Response
  CTRL-->>C: HTTP Response
```

---

## 📐 Estrutura do Projeto

```text
JABUTI-FASTAPI/
│
├── migrations/
│   └── versions/                 # Arquivos de migração (Alembic)
│
├── src/
│   ├── main.py                   # Entry point da aplicação
│   │
│   ├── controllers/              # Camada de rotas
│   │   └── user_controller.py
│   │
│   ├── core/                     # Configurações e infraestrutura
│   │   ├── settings.py
│   │   ├── logging_config.py
│   │   ├── middlewares.py
│   │   └── request_context.py
│   │
│   ├── models/                   # Modelos ORM e conexão com banco
│   │   ├── database.py
│   │   └── user_model.py
│   │
│   ├── schemas/                  # Schemas Pydantic
│   │   └── user_schema.py
│   │
│   └── cache/                    # Integração com Redis
│       └── redis_client.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
└── .env.example
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
