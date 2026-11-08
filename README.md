# JABUTI FastAPI

API didática de cadastro de usuários, desenvolvida por Rafael Tasinato para demonstrar FastAPI, persistência assíncrona, cache e conteinerização. Utiliza Python **3.12** no Docker; o projeto declara Python >=3.12,<4.0. As dependências resolvidas estão em `poetry.lock`.

## O que está implementado

- CRUD com UUID, paginação e ordenação; validação de nome, e-mail e idade.
- SQLAlchemy assíncrono e PostgreSQL; migração inicial e reversão com Alembic.
- Redis opcional para listas e registros; TTL configurável e invalidação após escritas.
- Chave de API compartilhada para proteger todos os endpoints de usuários.
- Health check de banco e cache; identificação de requisições e logs.
- Testes automatizados e verificação de código no GitHub Actions.

## Arquitetura atual

`cliente → FastAPI/controller → SQLAlchemy/PostgreSQL e Redis`

Os controllers coordenam as operações, consultas e cache. `schemas` valida entradas e respostas; `models` define tabela e sessão; `core` contém configuração, autenticação e middleware. **Não existem camadas Service e Repository**. Essa separação pode ser avaliada quando as regras de negócio crescerem.

## Executar com Docker

Requisitos: Docker com Compose e Python para gerar uma chave (ou outro gerador seguro).

1. Copie `.env.example` para `.env`.
2. Substitua a senha de exemplo em `POSTGRES_PASSWORD` e na `DATABASE_URL`. Codifique caracteres especiais da senha na URL.
3. Gere uma chave com `python -c "import secrets; print(secrets.token_urlsafe(32))"` e preencha `API_KEY` (mínimo de 32 caracteres). Não publique `.env`.
4. Execute `docker compose up --build`.

A API fica em http://127.0.0.1:8015; documentação em `/docs`. PostgreSQL e Redis ficam na rede interna, sem portas publicadas. A aplicação executa com usuário sem privilégios. O comando de inicialização aplica `alembic upgrade head` antes do Uvicorn.

No Swagger, clique em **Authorize** e informe a chave. Outros clientes devem enviar `X-API-Key: <sua-chave>`.

## API

| Método | Rota | Comportamento |
|---|---|---|
| GET | `/usuarios/` | Lista; `limit` 1–100, `offset` >=0, `sort` nome/email/idade, com `-` para decrescente |
| GET | `/usuarios/{id}` | Consulta por UUID |
| POST | `/usuarios/` | Cria; retorna 201 |
| PUT | `/usuarios/{id}` | Atualização parcial; campos omitidos são preservados |
| DELETE | `/usuarios/{id}` | Exclui; retorna 204 |
| GET | `/health` | Público; 200 com banco disponível, 503 sem banco |

Corpo de criação: `{"nome":"Ana","email":"ana@example.com","idade":30}`.
Nome: 1–100 caracteres após remover espaços nas extremidades; e-mail válido até 150 caracteres; idade inteira não negativa (sem conversão de texto ou booleano). Campos extras e valores nulos são rejeitados. Erros: 401 chave ausente/incorreta, 404 não encontrado, 409 e-mail duplicado, 422 validação; ordenação desconhecida retorna 400.

## Desenvolvimento e testes

```sh
poetry install
poetry run ruff check src migrations tests
poetry run pytest -q
```

Os testes usam SQLite temporário e simulam falhas do Redis; não precisam de serviços externos. Essa suíte não substitui testes de integração no PostgreSQL/Redis reais. A migração é exercitada com upgrade, comparação de metadados e downgrade.

Para executar fora do Docker, configure `.env` com um PostgreSQL acessível pelo host (a configuração padrão usa o hostname interno `db`), ajuste Redis ou defina `CACHE_ENABLED=false`, e execute:

```sh
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload --port 8015
```

## Migrações e bancos existentes

Em um banco novo, use `alembic upgrade head`. Para novas mudanças de modelo, gere uma revisão com `alembic revision --autogenerate -m "descricao"`, revise o SQL e teste a reversão antes de aplicar. `alembic downgrade base` remove a tabela e seus dados: use apenas em banco descartável.

Bancos criados pela versão antiga com `create_all` não têm histórico Alembic. Faça backup e compare o esquema com a revisão `0001` antes de adotar o histórico. **Somente se os esquemas forem equivalentes**, `alembic stamp 0001` registra a versão sem recriar tabelas; divergências exigem uma migração de transição. Não aplique stamp automaticamente.

## Limites e próximos passos

Este é um projeto de demonstração, **sem declaração de prontidão para produção**. A chave compartilhada não representa contas de usuários, autorização por perfil ou autenticação OAuth/OIDC. Antes de uma implantação pública, avaliar identidade e permissões, TLS, rotação e armazenamento de segredos, limites de requisição, backups e recuperação, observabilidade e testes com os serviços reais. Em múltiplas réplicas, executar migrações como etapa única de implantação.

O cache é de melhor esforço: falhas e concorrência podem causar leituras temporariamente desatualizadas até o TTL. Se Redis falhar no início, o processo segue sem cache até reiniciar. Não há garantia de consistência forte, alta disponibilidade ou ganho de desempenho medido.

[Documentação complementar](docs/README.md).
