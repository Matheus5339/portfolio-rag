# go-api-lab

API HTTP pequena em Go, feita para aprender e praticar back-end em Go:
roteamento, JSON, testes, contêiner e CI. Usa **só a biblioteca padrão**
(`net/http`, `encoding/json`), sem framework.

**No ar:** https://go-api-lab.calmwave-44962e56.brazilsouth.azurecontainerapps.io/health
(Azure Container Apps; a primeira requisição pode demorar alguns segundos,
porque o app escala para zero quando ninguém acessa).

## Endpoints

| Método e rota      | Resposta                                                   |
|--------------------|------------------------------------------------------------|
| `GET /health`      | `{"status":"ok","uptime_seconds":12.3}`                     |
| `GET /metrics`     | `{"requests_total":42}` (conta todas as requisições, inclusive esta) |
| `GET /items/{id}`  | `{"id":1,"name":"Teclado mecânico","price_cents":29990}`    |

Erros em `/items/{id}`:

- `400` se o id não for um inteiro positivo (`/items/abc`, `/items/0`)
- `404` se o item não existir (`/items/999`)

Qualquer outro método nas rotas (ex.: `POST /health`) recebe `405`.

## Como rodar

Requer Go 1.22+ (usa os padrões de rota com método e `{id}`).

```bash
go run .
curl http://localhost:8080/health
```

A porta vem da variável `PORT` (padrão `8080`).

### Com Docker

```bash
docker build -t go-api-lab .
docker run --rm -p 8080:8080 go-api-lab
```

O Dockerfile é multi-stage: compila numa imagem com Go e copia só o
binário estático para uma imagem `distroless` sem shell, rodando como
usuário não-root.

## Testes

```bash
go test -v -cover ./...
```

Os testes usam `net/http/httptest` para chamar os handlers sem abrir porta
de rede. Cobrem os três endpoints, os erros 400/404 e o 405.

O CI (GitHub Actions) roda `gofmt`, `go vet`, `go test -race` e o build da
imagem Docker a cada push na `main`, e publica a imagem em
`ghcr.io/matheus5339/go-api-lab` (GitHub Container Registry).

## Deploy (Azure Container Apps)

A imagem pública do GHCR roda no Azure Container Apps (região Brazil South),
com 0 a 1 réplica (0,25 vCPU, 0,5 GiB) e sem workspace de logs, para ficar
dentro da cota gratuita:

```bash
az group create --name rg-go-api-lab --location brazilsouth
az containerapp env create --name env-go-api-lab --resource-group rg-go-api-lab \
  --location brazilsouth --logs-destination none
az containerapp create --name go-api-lab --resource-group rg-go-api-lab \
  --environment env-go-api-lab --image ghcr.io/matheus5339/go-api-lab:latest \
  --ingress external --target-port 8080 --min-replicas 0 --max-replicas 1 \
  --cpu 0.25 --memory 0.5Gi
```

Para publicar uma versão nova depois de um push na `main`:

```bash
az containerapp update --name go-api-lab --resource-group rg-go-api-lab \
  --image ghcr.io/matheus5339/go-api-lab:<sha-do-commit>
```

## Decisões

- **Biblioteca padrão em vez de framework** (Gin, Echo): desde o Go 1.22 o
  `http.ServeMux` já faz roteamento por método e parâmetro de caminho.
- **Contador com `atomic.Int64`**: cada requisição roda numa goroutine própria;
  um `int` com `++` teria condição de corrida.
- **Preço em centavos (`int`)**: `float` tem erro de arredondamento com dinheiro.
- **Graceful shutdown**: ao receber SIGTERM (o que plataformas de contêiner
  como Azure Container Apps e Cloud Run fazem antes de parar o contêiner), o
  servidor termina as requisições em andamento.
- **Imagem no GHCR em vez do Azure Container Registry**: o GHCR é gratuito para
  repositórios públicos; o ACR cobra por dia mesmo sem uso.

## O que ficou de fora

- Banco de dados: os itens são fixos, em memória.
- Criar/editar/apagar itens (só leitura).
- Autenticação e limite de requisições (rate limiting).
- Métricas no formato Prometheus (o `/metrics` aqui é um JSON simples).
  O contador fica em memória e zera quando o app escala para zero.
- Deploy contínuo: o CI publica a imagem, mas a atualização no Azure é manual
  (`az containerapp update`).
