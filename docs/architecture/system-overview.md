# 🏛 Visão Geral do Sistema

O JABUTI FastAPI é um backend containerizado com:

- FastAPI
- PostgreSQL
- Redis
- Docker Compose

---

## Componentes

| Componente | Função |
|---|---|
| FastAPI | API REST |
| PostgreSQL | Persistência |
| Redis | Cache |
| Docker | Isolamento |
| Uvicorn | ASGI server |

---

## Fluxo de Requisição

Client → FastAPI → Cache → Database → Response
