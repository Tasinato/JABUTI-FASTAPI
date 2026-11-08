# 📚 Documentação Técnica — JABUTI FastAPI

Este diretório contém toda a documentação técnica detalhada do sistema, organizada por domínio arquitetural e operacional.

---

## 🏛 Arquitetura

- Visão geral do sistema  
  → [System Overview](./architecture/system-overview.md)

- Arquitetura de cache Redis  
  → [Cache Architecture](./architecture/cache.md)

- Modelo de dados  
  → [Data Model](./architecture/data-model.md)

- Decisões arquiteturais (ADR)  
  → [Architecture Decisions](./architecture/decisions/001-use-redis.md)

---

## 🔌 API

- Endpoints documentados  
  → [API Endpoints](./api/endpoints.md)

---

## 🚀 Deploy

- Docker e containers  
  → [Docker Deployment](./deployment/docker.md)

- Variáveis de ambiente  
  → [Environment Variables](./deployment/environment.md)

---

## ⚙ Operação

- Monitoramento  
  → [Monitoring](./operations/monitoring.md)

- Troubleshooting  
  → [Troubleshooting](./operations/troubleshooting.md)

- Performance e tuning  
  → [Performance Tuning](./operations/performance.md)

---

## 👨‍💻 Desenvolvimento

- Setup local  
  → [Local Setup](./development/local-setup.md)

- Testes  
  → [Testing Guide](./development/testing.md)

---

## 🧭 Navegação Rápida

| Área | Descrição |
|---|---|
| Arquitetura | Estrutura do sistema e decisões técnicas |
| API | Contrato e endpoints REST |
| Deploy | Infraestrutura e execução |
| Operação | Monitoramento e suporte |
| Desenvolvimento | Setup e contribuição |

---

## 📌 Convenções de Documentação

- Todos documentos são versionados junto ao código
- ADRs seguem padrão Architecture Decision Record
- Diagramas usam Mermaid
- Configurações sempre documentadas via `.env.example`
- Documentação escrita para ambiente containerizado

---

## 👤 Autor

**Rafael Tasinato**  
AI & Software Engineer
