# Jurídico SaaS — Captação DJEN + Produtividade

[![CI](https://github.com/Matheus5339/juridico-saas/actions/workflows/ci.yml/badge.svg)](https://github.com/Matheus5339/juridico-saas/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SaaS **multi-tenant** para escritórios e sociedades de advogados, com dois núcleos:

1. **Captação automatizada** de publicações e intimações dos diários de justiça (DJEN), por
   **OAB + UF** do advogado ou da sociedade.
2. **Dashboard de produtividade**: processos ganhos, perdidos e em andamento, por advogado e
   por escritório.

> **Princípio de produto:** automatiza-se a **coleta**; onde há consequência jurídica (prazo,
> desfecho), a automação **propõe** e um humano **confirma**.

| | |
|---|---|
| **Isolamento entre clientes** | PostgreSQL **Row Level Security** (`ENABLE` + `FORCE`), com **3 testes negativos cross-tenant** |
| **Testes** | **87 testes automatizados** (Pytest), todos passando |
| **Decisões documentadas** | **10 ADRs** em [`DECISIONS.md`](DECISIONS.md) |
| **Migrations** | **7**, versionadas com Alembic |
| **Segurança em CI** | `bandit` (SAST) + `pip-audit` (SCA) + `gitleaks` (histórico completo) |
| **Stack** | Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy · Alembic · RQ + Redis · React + Vite |

---

## Fluxo do sistema

```
  DJEN / Comunica API
          │
          ▼
   adapter fino            <- contrato verificado por sondagem da API real,
  (comunica_client)           não pela documentação
          │
          ▼
  ingestão idempotente     <- ancorada no `id` real da fonte (ADR-007):
   (poller + parser)          rodar duas vezes não duplica
          │
          ▼
  enriquecimento DataJud
   + reconciliação
          │
          ▼
  motor de classificação   <- regras; IA com egress bloqueado para
   (desfecho do processo)     dado sigiloso (ADR-009)
          │
          ▼
    revisão humana         <- a automação propõe, o advogado confirma
          │
          ▼
  cálculo de prazo         <- calendário injetável (ADR-008)
   + alerta
```

---

## Por que RLS no banco, e não `WHERE tenant_id = ?` na aplicação

Esta é a decisão central do projeto (ADR-002 e ADR-006).

Filtrar por tenant na camada de aplicação funciona **até a primeira consulta em que alguém
esquece o filtro**. Não existe aviso: a query roda, retorna dados de outro cliente, e o bug só
aparece quando o cliente errado enxerga o processo do concorrente. Em software jurídico, isso
não é um bug de severidade média — é violação de sigilo profissional.

A escolha aqui foi empurrar o isolamento para **dentro do banco**, onde ele não depende da
disciplina de quem escreve a query:

```sql
ALTER TABLE publicacoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE publicacoes FORCE  ROW LEVEL SECURITY;   -- vale inclusive para o dono da tabela

CREATE POLICY tenant_isolation ON publicacoes
  USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid);
```

Três detalhes que separam RLS que protege de RLS que dá falsa sensação de segurança:

- **`FORCE ROW LEVEL SECURITY`** — sem ele, o *dono da tabela* atravessa a política
  silenciosamente. `ENABLE` sozinho não basta.
- **Dois papéis de banco separados** (ADR-006) — o runtime conecta como `juridico_app`
  (`NOSUPERUSER`, sujeito à RLS) e as migrations como `juridico` (dono do schema). O
  superusuário do Postgres **ignora RLS mesmo com `FORCE`**; se a aplicação rodasse como
  superusuário, todo o isolamento seria decorativo. Isso não veio da teoria: os testes negativos
  falharam até os papéis serem separados.
- **`set_config('app.current_tenant', :tid, true)`** — o `true` (`is_local`) prende o valor ao
  **escopo da transação**. Com `false`, o tenant vazaria para a próxima requisição que
  reutilizasse a mesma conexão do pool: um usuário veria os dados de outro escritório.

E o que garante que isso continua verdade: **`backend/tests/test_rls_cross_tenant.py`**, com três
testes **negativos** — que provam o que o sistema *não* deixa acontecer:

| Teste | O que prova |
|---|---|
| `test_leitura_isolada_entre_tenants` | O tenant A não lê dado do tenant B |
| `test_insercao_cross_tenant_bloqueada` | O tenant A não consegue **gravar** dado no tenant B |
| `test_sem_tenant_nao_le_nada` | Sem contexto de tenant, a consulta devolve **zero linhas** — não o banco inteiro |

O terceiro é o que define o comportamento em caso de falha: se alguém esquecer de injetar o
contexto do tenant, o sistema falha **fechado** (não mostra nada) em vez de falhar aberto
(mostrar tudo). Testar que algo *não* acontece é o que impede uma regressão silenciosa de virar
vazamento.

---

## Como rodar o ambiente local

Pré-requisitos: Docker + Docker Compose.

```bash
# 1. copie o exemplo de variáveis de ambiente
cp infra/.env.example .env        # Windows PowerShell: Copy-Item infra/.env.example .env

# 2. suba os serviços (API + Postgres + Redis)
docker compose up --build

# 3. healthcheck
curl http://localhost:8000/health
# -> {"status":"ok",...}
```

Documentação OpenAPI (dev): http://localhost:8000/docs

### Migrations e testes

```bash
docker compose up -d db
docker compose run --rm api sh -c "pip install -r requirements-dev.txt && alembic upgrade head && pytest -q"
```

### Fluxo de uso (Fase 1)

```bash
# 1. onboarding de escritório (operação de plataforma, exige setup token)
curl -X POST localhost:8000/admin/tenants -H "X-Setup-Token: dev-setup-token-trocar" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Meu Escritorio","slug":"meu-esc","admin_email":"admin@x.com","admin_senha":"senhaForte123"}'

# 2. login (tenant_slug + email + senha; OTP quando MFA habilitado)
curl -X POST localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"tenant_slug":"meu-esc","email":"admin@x.com","senha":"senhaForte123"}'

# 3. usar o token retornado em Authorization: Bearer <token> nas rotas /advogados, /processos
```

### Captação agendada (RQ)

```bash
docker compose up -d worker scheduler                     # worker (executa) + rqscheduler (cron)
docker compose run --rm api python -m scheduler.agendar    # cron diário (CAPTACAO_CRON, padrão 06:00)
docker compose run --rm api python -m scheduler.run_poller 2026-06-01 2026-06-28   # disparo manual
```

Idempotente: reprocessar a mesma janela não duplica (ancorado no `id` real do DJEN).

---

## Estrutura

```
juridico-saas/
├── DECISIONS.md              # 10 ADRs — decisões de arquitetura e alternativas descartadas
├── docs/                     # domínio, contratos de API, regras de classificação, segurança
├── backend/
│   ├── app/
│   │   ├── api/              # routers FastAPI
│   │   ├── core/             # config, segurança, autenticação
│   │   ├── db/               # sessão e contexto de tenant (set_config)
│   │   ├── domain/           # regras de negócio (prazo, desfecho)
│   │   ├── models/           # modelos SQLAlchemy
│   │   ├── services/         # camada de serviços
│   │   ├── ingest/           # adapters DJEN/DataJud, poller, parser, reconciliação
│   │   ├── classifier/       # motor de classificação + egress guard
│   │   └── jobs/             # tarefas assíncronas (RQ)
│   ├── scheduler/            # agendamento da captação diária
│   ├── scripts/              # sondagem das APIs reais (Comunica, DataJud)
│   ├── db/migrations/        # 7 migrations Alembic
│   └── tests/                # 87 testes, incl. test_rls_cross_tenant.py
├── frontend/                 # SPA React + Vite (ver "Limitações conhecidas")
└── infra/                    # docker, postgres-init (papel de runtime), backup/restore
```

---

## Segurança

- **Isolamento multi-tenant** por RLS com `FORCE` + papel de runtime sem privilégio
- **Autenticação JWT com MFA (TOTP)** e RBAC
- **Trilha de auditoria append-only**
- **Egress guard** no classificador — dado sigiloso é bloqueado antes de chegar à IA (ADR-009)
- **Backup criptografado** e script de restore (`infra/backup.sh`, `infra/restore.sh`)
- **CI de segurança**: `bandit` (SAST), `pip-audit` (SCA) e `gitleaks` com `fetch-depth: 0`
  varrendo o histórico completo do repositório
- Modelo de ameaças e plano de resposta a incidente em `docs/seguranca.md`

Nenhum segredo é versionado: apenas `infra/.env.example`, com `.gitignore` cobrindo segredos e
PII de sondagem.

---

## Limitações conhecidas

Registradas de propósito — um README que só lista acertos não ajuda ninguém a avaliar o projeto.

- **O frontend é mínimo.** São dois arquivos com lógica real (`frontend/src/App.jsx` e
  `frontend/src/api.js`): uma SPA funcional que exercita a API ponta a ponta, e nada além disso.
  Sem gerenciamento de estado, sem testes de UI, sem design system. O esforço do projeto está no
  backend; o frontend existe para provar que a API fecha o fluxo.
- **Fase 1 de 2.** O núcleo está entregue — multi-tenant com RLS, auth com MFA, RBAC, CRUD de
  advogado e processo, ingestão, classificação, dashboard e CI. Os itens marcados
  `VERIFICAR` em `docs/fontes-api.md` são pré-requisito da Fase 2.
- **Cobertura limitada ao que o DJEN expõe.** Tribunais fora do Diário de Justiça Eletrônico
  Nacional não são captados.
- **Sem deploy público.** O projeto roda via Docker Compose local; não há ambiente hospedado.
- **A classificação de desfecho é baseada em regras**, não em modelo treinado. Foi escolha
  deliberada (ADR-009): em contexto jurídico, uma regra errada é auditável e corrigível — um
  modelo errado, não. Toda classificação passa por revisão humana antes de virar prazo.

---

## Licença

[MIT](LICENSE)
