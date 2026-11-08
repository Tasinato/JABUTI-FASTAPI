# Docker

Siga a preparação de `.env` no [README](../../README.md). Execute `docker compose up --build`.

Apenas a API é publicada em `127.0.0.1:8015`. PostgreSQL (5432) e Redis (6379) são acessíveis apenas pela rede interna do Compose. A imagem usa Python 3.12 e usuário sem privilégios; aplica Alembic antes de iniciar o servidor.

O volume postgres_data preserva o banco. Não remova volumes sem backup. Alterar POSTGRES_PASSWORD não troca a senha de um banco já inicializado: use o procedimento próprio do PostgreSQL e atualize a configuração de forma coordenada.

Para múltiplas réplicas, retire as migrações do startup e execute-as uma vez por implantação. O Compose é destinado à demonstração local, não configura TLS nem uma plataforma de produção.
