# Infrastructure Monitor

[![Infrastructure Monitor CI](https://github.com/Matheus5339/infrastructure-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/Matheus5339/infrastructure-monitor/actions/workflows/ci.yml)

Sistema de monitoramento utilizando Node.js, Prometheus e Grafana com Docker Compose.

## Tecnologias

- Node.js
- Express
- Prometheus
- Grafana
- Docker
- Docker Compose

---

## Funcionalidades

- API HTTP em Node.js
- Endpoint de métricas Prometheus
- Coleta automática de métricas
- Dashboard Grafana
- Multi-container com Docker Compose
- Observabilidade completa

---

## Estrutura do Projeto

```bash
infrastructure-monitor/
│
├── app/
├── prometheus/
├── grafana/
└── docker-compose.yml
```

---

## Como executar

### Subir containers

```bash
docker compose up --build -d
```

### Verificar containers

```bash
docker compose ps
```

### Parar containers

```bash
docker compose down
```

---

## URLs

### Aplicação

http://localhost:3000

### Prometheus

http://localhost:9090

### Grafana

http://localhost:3001

Usuário:
```bash
admin
```

Senha:
```bash
admin123
```

---

## Métricas

Endpoint Prometheus:

```bash
/metrics
```

---

## Objetivo

Projeto desenvolvido para estudos de:

- DevOps
- Observabilidade
- Containers
- Monitoramento
- Prometheus
- Grafana
- Docker Compose