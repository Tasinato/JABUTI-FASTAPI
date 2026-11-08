# Endpoints

Consulte a tabela e exemplos do [README](../../README.md) e o OpenAPI em `/docs`. Todas as rotas `/usuarios/` e `/usuarios/{id}` exigem `X-API-Key`. `/health` e a documentação são públicos.

PUT aceita atualização parcial; campos omitidos são preservados e null é rejeitado. POST requer nome, email e idade. E-mails duplicados retornam 409. A chave é compartilhada pelo serviço: não há identidade ou permissão por usuário.
