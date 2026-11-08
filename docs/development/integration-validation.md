# Validação local com contêineres — 08/11/2026

## Ambiente

- Docker Engine 29.6.2, imagem da API construída pelo Dockerfile do projeto (Python 3.12).
- PostgreSQL 16.15 e Redis 7.4.12.
- Projeto Compose isolado `jabuti-validation-20261108`, banco e credenciais temporários, API publicada somente em 127.0.0.1:18015.
- A configuração principal e o arquivo .env do usuário não foram alterados.

## Resultados

20 verificações de integração aprovadas, abrangendo:

- Disponibilidade do banco e Redis; processo da API executando com UID 10001.
- Migração inicial executada na inicialização e `alembic check` sem diferenças de esquema.
- Autenticação obrigatória, criação, leitura, atualização e exclusão de usuários.
- Rejeição de e-mail duplicado (409) e idade inválida (422); consulta de registro excluído (404).
- Chaves individuais e de listagem presentes no Redis, TTL aplicado, invalidação de listas, atualização e exclusão do cache individual.
- Leitura e escrita disponíveis durante interrupção real do contêiner Redis; health check do banco continua em 200 e informa Redis indisponível.
- Recuperação do Redis, reinício da API e persistência do valor atualizado após expiração do cache.

Após o teste HTTP, a API foi parada e a migração passou por `alembic downgrade base`, `alembic upgrade head` e `alembic check`, exclusivamente no banco descartável de validação. Os contêineres e a rede desse projeto foram encerrados; o volume de teste foi preservado.

## Limitação observada

Na primeira execução, a comparação imediata após recuperação do Redis encontrou um valor antigo no cache. Isso confirma a limitação de consistência já descrita no README: uma escrita no PostgreSQL durante falha do Redis pode deixar uma entrada antiga até expirar. Não é falha de persistência do banco nem recuperação com consistência imediata.

A repetição usou TTL de 5 segundos apenas no ambiente de teste e confirmou o valor atualizado depois da expiração; o padrão do projeto permanece em 60 segundos. O teste não demonstra consistência forte, desempenho sob carga ou prontidão para produção.

A suíte automatizada local permanece com 34 testes aprovados. As verificações de contêineres desta página foram executadas localmente e não fazem parte do GitHub Actions atual.
