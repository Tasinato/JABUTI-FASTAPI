# 🐢 JABUTI – FastAPI Backend

Backend estruturado com **FastAPI**, gerenciado com **Poetry** e containerizado com **Docker**.  
Projeto organizado com arquitetura modular e preparado para escalar em ambiente profissional.

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

## 🚀 Tecnologias Utilizadas

- Python 3.14
- FastAPI
- Poetry
- Docker & Docker Compose
- PostgreSQL
- Redis
- Alembic
- Uvicorn

---

## 🐳 Execução com Docker (Recomendado)

Build da aplicação:

```bash
docker compose build
```

Subir containers:

```bash
docker compose up
```

Parar containers:

```bash
docker compose down
```

A aplicação ficará disponível em:

```
http://localhost:8015
```

Documentação automática:

- Swagger UI:  
  http://localhost:8015/docs

- ReDoc:  
  http://localhost:8015/redoc

---

## ⚙️ Execução Local com Poetry (Opcional)

Instalar dependências:

```bash
poetry install
```

Executar aplicação:

```bash
uvicorn src.main:app --reload --port 8015
```

---

## 🔐 Configuração de Ambiente (Docker)

O projeto utiliza Docker para gerenciamento do ambiente.

Crie um arquivo `.env` na raiz com base no modelo:

```bash
cp .env.example .env
```

Após isso, inicie os serviços:

```bash
docker compose up --build
```

O Docker será responsável por injetar as variáveis no container.

⚠️ O arquivo `.env` não deve ser versionado.

---

## 🏗️ Padrão Arquitetural

O projeto segue princípios de:

- Separação por camadas (Controller → Service → Model)
- Organização modular
- Containerização para portabilidade
- Preparação para escalabilidade
- Versionamento de banco com Alembic
- Integração com Redis para cache

---

## 📦 Objetivo

Estrutura base para backend profissional com foco em:

- Organização enterprise-ready
- Boas práticas de desenvolvimento
- Base sólida para evolução do produto
- Arquitetura preparada para crescimento

---

## 👤 Autor

**Rafael Tasinato**  
AI & Software Engineer
