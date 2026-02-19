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
│   ├── controllers/              # Camada de rotas (controllers)
│   │   └── user_controller.py
│   │
│   ├── core/                     # Configurações e infraestrutura
│   │   ├── settings.py
│   │   ├── logging_config.py
│   │   ├── middlewares.py
│   │   └── request_context.py
│   │
│   ├── models/                   # Modelos ORM e conexão DB
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
- Alembic
- Uvicorn

---

## ⚙️ Execução Local com Poetry

Instalar dependências:

```bash
poetry install
```

Ativar ambiente virtual:

```bash
poetry shell
```

Executar aplicação:

```bash
uvicorn jabuti.main:app --reload
```

---

## 🐳 Execução com Docker

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

---

## 📄 Documentação Automática

Após subir a aplicação:

- Swagger UI:  
  http://localhost:8015/docs

- ReDoc:  
  http://localhost:8015/redoc

---

## 🔒 Variáveis de Ambiente

Criar um arquivo `.env` baseado no modelo:

```bash
cp .env.example .env
```

⚠️ O arquivo `.env` não deve ser versionado.

---

## 🏗️ Padrão Arquitetural

O projeto segue princípios de:

- Separação por camadas (API → Service → Model)
- Organização modular
- Containerização para portabilidade
- Preparação para escalabilidade
- Versionamento de banco com Alembic

---

## 📦 Objetivo

Estrutura base para backend profissional com foco em:

- Organização enterprise-ready
- Boas práticas de desenvolvimento
- Base sólida para evolução do produto

---

## 👤 Autor

**Rafael Tasinato**  
AI & Software Engineer
