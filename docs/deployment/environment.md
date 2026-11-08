# Configuração

O modelo é `.env.example`. Não publique `.env`.

| Variável | Finalidade |
|---|---|
| DATABASE_URL | Obrigatória; conexão SQLAlchemy assíncrona |
| POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB | Inicialização do banco no Compose; devem coincidir com a URL |
| API_KEY | Obrigatória, mínimo 32 caracteres; enviada em X-API-Key |
| REDIS_URL | Endereço do cache |
| CACHE_ENABLED | Habilitar tentativa de conexão; padrão true |
| CACHE_TTL | Expiração em segundos, mínimo 1; padrão 60 |
| APP_NAME / APP_ENV | Nome e identificação do ambiente |
| APP_DEBUG | Padrão false; não habilitar em serviço público |
| LOG_LEVEL | Nível dos logs; padrão INFO |

APP_ENV é informativo: não implementa políticas automáticas de segurança.
