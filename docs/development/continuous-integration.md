# Integração contínua (CI)

O workflow `.github/workflows/tests.yml` executa em push, Pull Request e acionamento manual pela aba Actions. Um exemplo concreto: alterar uma validação e enviar um commit faz o GitHub testar a alteração sem depender do computador do desenvolvedor.

## Jobs

1. `tests`: instala dependências do lock, confere o lock, executa Ruff e a suíte pytest (SQLite e simulações de cache).
2. `PostgreSQL + Redis integration`: constrói a imagem do Dockerfile, inicia os serviços definidos em `compose.ci.yml`, aplica a migração pela inicialização da API e executa 20 verificações HTTP/cache/banco. Também reverte e reaplica a migração no banco descartável.

Os jobs são independentes e podem executar em paralelo. Uma falha torna a execução vermelha; os logs mostram a etapa que falhou. Em sucesso, o relatório JSON fica disponível no artefato `integration-results`. A limpeza dos contêineres ocorre mesmo se um teste falhar. O workflow recebe apenas permissão de leitura do repositório e não utiliza segredos reais.

## O que a integração verifica

Autenticação, CRUD, conflitos e validações; cache individual e de listas, TTL e invalidação; leitura e escrita durante interrupção real do Redis, recuperação e leitura após a expiração; esquema Alembic alinhado aos modelos e processo sem privilégios root.

O TTL de teste é 5 segundos para acelerar a verificação da expiração; o padrão da aplicação permanece 60 segundos. Valores antigos após falha do Redis continuam possíveis até o TTL. Esse teste verifica o comportamento documentado, não consistência imediata.

## Reproduzir localmente

Requisitos: Docker com Compose e Python 3.12; o script usa apenas a biblioteca padrão.

```sh
docker compose -p jabuti-ci -f compose.ci.yml up -d --build --wait --wait-timeout 180
python integration/check_stack.py
docker compose -p jabuti-ci -f compose.ci.yml stop app
docker compose -p jabuti-ci -f compose.ci.yml run --rm --no-deps app sh -c 'alembic downgrade base && alembic upgrade head && alembic check'
docker compose -p jabuti-ci -f compose.ci.yml down --volumes --remove-orphans
```

Execute apenas com esse projeto descartável, sem dados importantes: a reversão apaga a tabela. O Compose de CI não utiliza `.env`; contém credenciais públicas exclusivas para testes, publica somente a API em 127.0.0.1:18015 e não expõe banco/cache. Não execute simultaneamente duas cópias locais com o mesmo nome/porta.

## CI, implantação e revisão

CI fornece evidências automatizadas para revisar mudanças. Este workflow não implanta o serviço, não testa carga e não transforma o projeto em produto pronto para produção. Os checks também não impedem, por si só, uma integração manual: isso exigiria regras de proteção da branch. Consulte o resultado dos dois jobs antes de integrar um Pull Request.
