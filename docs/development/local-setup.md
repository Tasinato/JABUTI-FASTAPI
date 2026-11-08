# Desenvolvimento local

Veja o [README](../../README.md) para preparar `.env`, dependências, banco e migrações. Use `poetry install`, `poetry run alembic upgrade head` e `poetry run uvicorn src.main:app --reload --port 8015`.

Fora do Compose, substitua os hostnames internos db/cache por endereços acessíveis. A configuração padrão não publica esses serviços no host.
