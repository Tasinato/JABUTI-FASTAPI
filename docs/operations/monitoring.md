# Monitoramento

`GET /health` é público e verifica conectividade do banco com SELECT 1. Retorna 200 com banco disponível e 503 sem banco. Redis pode aparecer como ok, disabled ou down e não torna o banco opcional. Esse endpoint não valida se as migrações estão atualizadas.

Logs e identificador de requisição ajudam na inspeção local. Métricas, alertas e testes de recuperação ainda precisam ser implementados para operação contínua.
