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
