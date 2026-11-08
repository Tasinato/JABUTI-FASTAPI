# Cache

Leituras consultam Redis e, na ausência de valor, consultam SQLAlchemy e armazenam o resultado. Chaves: `usuarios:list:{limit}:{offset}:{sort}` e `usuarios:id:{uuid}`. O TTL padrão é 60 segundos, configurável em `CACHE_TTL`.

Após confirmar uma escrita no banco, o controller invalida as listas e atualiza ou remove o registro individual. Banco e Redis não participam de uma transação conjunta: falhas e concorrência podem produzir valores desatualizados até o TTL. Não há garantia de consistência forte.

Redis é opcional: `CACHE_ENABLED=false` evita conexão. Falha na conexão inicial desabilita cache até reiniciar o processo; falhas posteriores são tratadas como indisponibilidade do cache. O banco continua sendo necessário. Latência e escalabilidade ainda precisam de medição.

Para inspeção local: `docker compose exec cache redis-cli --scan --pattern "usuarios:*"`. Evite comandos de limpeza global em instâncias compartilhadas.
