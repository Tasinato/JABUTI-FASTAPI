# Arquitetura de Cache — JABUTI FastAPI

Este documento descreve a arquitetura, estratégias e funcionamento do sistema de cache da API JABUTI FastAPI, incluindo cache de listagem e cache individual por usuário.

O cache utiliza Redis como camada de armazenamento em memória e segue estratégias modernas de consistência, desempenho e resiliência.

---

## 1. Objetivo do Cache

O cache é utilizado para:

* reduzir latência das requisições
* diminuir carga no PostgreSQL
* evitar consultas repetidas
* melhorar escalabilidade horizontal
* manter consistência controlada de leitura
* manter disponibilidade mesmo com falhas do Redis

---

## 2. Estratégia Geral de Cache

O sistema utiliza duas estratégias combinadas:

* Cache-Aside (Lazy Loading)
* Write-Through

---

### 2.1 Cache-Aside (Lazy Loading)

O cache é consultado primeiro.

Se não existir, o dado é buscado no banco e armazenado no Redis.

Fluxo:

1. aplicação consulta Redis
2. se existir → retorna cache (HIT)
3. se não existir → consulta banco (MISS)
4. salva resultado no Redis
5. retorna resposta

---

### 2.2 Write-Through

Toda operação de escrita atualiza o cache imediatamente após persistência no banco.

Isso garante:

* consistência forte de leitura
* ausência de dados obsoletos
* sincronização banco ↔ cache

---

## 3. Tipos de Cache Implementados

O sistema possui dois níveis de cache:

1. cache de listagem de usuários
2. cache individual por usuário

---

# 4. Cache de Listagem de Usuários

Armazena resultados paginados e ordenados da listagem de usuários.

## Endpoint

GET /usuarios

---

## Chave Redis

Formato:

usuarios:list:{limit}:{offset}:{sort}

Exemplo:

usuarios:list:10:0:nome

---

## Comportamento

| Operação       | Ação                       |
| -------------- | -------------------------- |
| GET lista      | cache-aside                |
| POST usuário   | invalida cache de listagem |
| PUT usuário    | invalida cache de listagem |
| DELETE usuário | invalida cache de listagem |

---

## Invalidação de Cache

Após qualquer modificação de usuário:

await cache_delete_prefix("usuarios:list:")

Isso remove todas as páginas armazenadas.

---

# 5. Cache por ID (User Detail Cache)

Além do cache de listagem, o sistema mantém cache individual por usuário.

Isso reduz consultas repetidas ao banco para leitura de um único registro, melhorando latência e reduzindo carga no PostgreSQL.

---

## Endpoint

GET /usuarios/{id}

---

## Chave Redis

Formato:

usuarios:id:{uuid}

Exemplo:

usuarios:id:08e7bb88-a963-4a4a-adcb-7175060932d1

---

## Estratégia de Cache

O sistema utiliza Cache-Aside + Write-Through.

| Operação              | Comportamento   |
| --------------------- | --------------- |
| GET /usuarios/{id}    | Read-through    |
| POST /usuarios        | Write-through   |
| PUT /usuarios/{id}    | Write-through   |
| DELETE /usuarios/{id} | Remove do cache |

---

## Fluxo de Leitura (Read-Through)

1. verifica Redis
2. se existir → retorna cache
3. se não existir → consulta PostgreSQL
4. armazena no Redis com TTL
5. retorna resposta

---

## Fluxo de Escrita (Write-Through)

Após qualquer modificação no usuário:

* cache de listagem é invalidado
* cache individual do usuário é atualizado ou removido

Garantias:

* consistência entre banco e cache
* leitura rápida
* ausência de dados obsoletos

---

## 6. TTL do Cache

Tempo de expiração padrão:

CACHE_TTL = 60 segundos

Após esse período, o registro expira automaticamente no Redis.

---

## 7. Teste Manual do Cache

Listar chaves:

docker compose exec cache redis-cli keys "usuarios:*"

Ver valor:

docker compose exec cache redis-cli get "usuarios:id:{uuid}"

Ver TTL:

docker compose exec cache redis-cli ttl "usuarios:id:{uuid}"

---

## 8. Comportamento em Caso de Falha do Redis

Se o Redis estiver indisponível:

* cache é desabilitado automaticamente
* aplicação continua funcional
* leituras vão diretamente ao banco
* logs registram modo degradado

Isso garante alta disponibilidade da API.

---

## 9. Benefícios da Arquitetura

* redução significativa de latência
* diminuição da carga no banco
* consistência controlada
* invalidação automática
* suporte a escalabilidade horizontal
* tolerância a falhas do Redis

---

## 10. Evoluções Futuras Recomendadas

* métricas de cache hit ratio
* cache warming automático
* compressão de payload
* observabilidade Prometheus / Grafana
* circuit breaker Redis
* políticas de invalidação por domínio
* benchmark antes / depois do cache

---

## Autor

Rafael Tasinato
AI & Software Engineer
