# Testes

Execute `poetry install`, `poetry run pytest -q` e `poetry run ruff check src migrations tests`.

A suíte cobre autenticação nas rotas de usuários, CRUD, conflitos de e-mail, validação, paginação/ordenação, cache com falha e migração inicial com reversão. Usa SQLite temporário e Redis simulado; PostgreSQL e Redis reais precisam de validação de integração separada. Não há benchmark de desempenho.
