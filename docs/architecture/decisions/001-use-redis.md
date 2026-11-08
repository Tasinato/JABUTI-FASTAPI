# ADR 001 — Redis opcional

Status: aceito para demonstração.

## Contexto e decisão

Para exercitar cache de leituras repetidas, a API consulta Redis antes do banco e armazena resultados com TTL. Escritas invalidam listas e atualizam ou removem o registro individual após commit.

## Consequências

O desenho pode reduzir consultas repetidas, mas os ganhos ainda não foram medidos. Adiciona infraestrutura e riscos de invalidação; não garante consistência forte. Redis indisponível não deve impedir o CRUD no banco. O projeto pode executar sem cache com CACHE_ENABLED=false.

Cache em memória do processo seria mais simples, mas não compartilharia valores entre réplicas. Manter apenas o banco continua sendo uma opção válida para cargas pequenas; a adoção definitiva exige medições.
