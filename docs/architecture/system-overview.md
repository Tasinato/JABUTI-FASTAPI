# Arquitetura

Cliente → controller FastAPI → SQLAlchemy/PostgreSQL e Redis opcional.

Controllers executam consultas, coordenam transações e cache. Schemas Pydantic validam dados; models definem tabela e sessão; core reúne configuração, chave de API, middleware e logs. Não há Service ou Repository. O Alembic controla a evolução do esquema; a aplicação não chama create_all na inicialização.

Consulte o [README](../../README.md) para execução, limitações e decisões de segurança.
