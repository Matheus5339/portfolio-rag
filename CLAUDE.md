# portfolio-rag

Projeto de portfólio do Matheus para a vaga iFood GenAI (trilha AI Builder), 31/10/2026.
Repositório: `github.com/Matheus5339/portfolio-rag` (público).

## Decisões
- Python 3.13 + FastAPI; busca TF-IDF em Python puro (`app/indice.py`); resposta com Gemini (`app/rag.py`).
- Base: READMEs públicos em `data/readmes/` (atualizar com `scripts/coletar.py`).
- Chave `GEMINI_API_KEY` só por variável de ambiente / segredo do Azure. `.env` no `.gitignore`.
- **Regra do Matheus: nada que custe dinheiro.** Gemini free tier; Azure for Students
  (Container Apps, min 0 / max 1, mesmo ambiente do go-api-lab); imagem no GHCR.

## Pendências
- Código escrito pelo Claude a pedido dele; ele vai estudar para defender em entrevista.

## Deploy atual (31/10/2026)
- Container App `portfolio-rag` no grupo `rg-go-api-lab`, ambiente `env-go-api-lab` (Brazil South, tipo **Express**).
- URL: https://portfolio-rag.calmwave-44962e56.brazilsouth.azurecontainerapps.io
- Chave: segredo `gemini-key` → variável `GEMINI_API_KEY=secretref:gemini-key`
  (cadastrado por `carreira/ferramentas/azure_segredo_gemini.py`, que lê o .env sem exibir).
- Ambiente Express não aceita `--revision-suffix` nem `revision restart`. Para publicar versão nova,
  troque a imagem pela tag do commit: `az containerapp update -n portfolio-rag -g rg-go-api-lab --image ghcr.io/matheus5339/portfolio-rag:<sha>`.
- Apagar só este app: `az containerapp delete -n portfolio-rag -g rg-go-api-lab`.
- 1º push no GHCR falhou com "denied" na tag (pacote novo); "Re-run failed jobs" resolveu.
