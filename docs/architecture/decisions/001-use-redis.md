# ADR 001 — Uso de Redis como Camada de Cache

## Status
**Aceito**

---

## Contexto
O sistema possui alta frequência de leituras, especialmente em endpoints de listagem e consulta por ID.

Sem uma camada de cache, todas as requisições são direcionadas ao banco PostgreSQL, o que pode causar:

- aumento de latência
- sobrecarga do banco
- redução de escalabilidade

---

## Decisão
Utilizar **Redis** como camada de cache em memória, aplicando a estratégia:

**Cache-Aside (Lazy Loading)**

Fluxo adotado:

1. Aplicação consulta o cache
2. Se houver HIT → retorna imediatamente
3. Se MISS → consulta o banco
4. Armazena resultado no Redis
5. Retorna resposta

---

## Consequências

### Benefícios
- Redução significativa de latência
- Redução de carga no banco de dados
- Melhor escalabilidade horizontal
- Melhora do throughput da API

### Custos / Trade-offs
- Aumento da complexidade arquitetural
- Necessidade de política de invalidação de cache
- Dependência de infraestrutura adicional (Redis)

---

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|---|---|
| Cache em memória da aplicação | Não escalável em múltiplas instâncias |
| CDN | Não aplicável a dados dinâmicos |
| Sem cache | Alto custo de leitura no banco |

---

## Resultado Esperado

- Melhoria de performance em endpoints de leitura
- Redução do número de queries no PostgreSQL
- Base preparada para crescimento do tráfego
