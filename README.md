# portfolio-rag

Assistente que responde perguntas sobre os meus projetos usando **RAG**
(*retrieval-augmented generation*): busca os trechos mais relevantes nos
READMEs públicos do meu GitHub e pede ao Gemini uma resposta baseada **só**
neles, **citando a fonte** de cada informação.

**Demo no ar:** https://portfolio-rag.calmwave-44962e56.brazilsouth.azurecontainerapps.io (o primeiro acesso pode levar alguns segundos: o app desliga quando ninguém usa)

Construído do zero em um dia (31/10/2026).

## Como funciona

```
scripts/coletar.py ──► data/readmes/*.md      (API pública do GitHub)
                           │
                           ▼
app/indice.py: divide por título (#, ##, ###) ──► índice TF-IDF
                           │
pergunta ──► busca os 5 trechos mais parecidos (similaridade de cosseno)
                           │ nenhum trecho relevante? → "não encontrei" (nem chama a IA)
                           ▼
app/rag.py: prompt com trechos numerados [1]..[5] ──► Gemini ──► resposta com [n]
                           │
                           ▼
                 resposta + lista de fontes com link para o repositório
```

API:
- `POST /api/perguntar` `{"pergunta": "..."}` → resposta + fontes
- `GET /api/buscar?q=...` → só a etapa de busca, **sem IA** (para ver o que seria enviado)
- `GET /api/repos` · `GET /health`

## Decisões

- **TF-IDF em Python puro em vez de embeddings.** Para ~70 trechos curtos é
  suficiente, não gasta cota, roda em milissegundos e dá para explicar a conta.
  Com uma base maior, o próximo passo seria embeddings + banco vetorial.
- **Anti-alucinação:** o modelo recebe só os trechos, tem de citar `[n]` e tem
  uma frase fixa para quando não sabe; se a busca não acha nada, a IA nem é chamada.
- **Proteção contra prompt injection:** a instrução diz que os trechos são dados,
  não ordens.
- **Divisão por título do Markdown**, ignorando `#` dentro de blocos de código e
  descartando trechos muito curtos (ex.: "Licença: MIT"), que distorciam a busca.
- **Custo zero:** Gemini no plano gratuito; Azure Container Apps (Azure for
  Students) com escala para zero; imagem no GitHub Container Registry.
- **Proteção da cota:** limite global por hora (`LIMITE_POR_HORA`, padrão 30)
  e pergunta de até 300 caracteres.
- **Chave fora do código:** `GEMINI_API_KEY` vem de variável de ambiente (`.env`
  local, fora do Git; segredo do Container App em produção).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env            # e coloque sua chave grátis do Google AI Studio
python scripts/coletar.py         # opcional: atualiza os READMEs (outro usuário: passe o nome)
pytest -q
uvicorn app.main:app --reload     # http://localhost:8000
```

## Testes e CI

`pytest` cobre normalização, divisão em trechos, busca, montagem do prompt,
o caso "sem trecho relevante" (sem chamar a IA) e a API, tudo com cliente Gemini
falso. O GitHub Actions roda os testes e publica a imagem em
`ghcr.io/matheus5339/portfolio-rag`.

## Limitações

- TF-IDF não entende sinônimos ("banco de dados" × "PostgreSQL" só casa se a
  palavra aparecer no texto).
- A base é uma foto dos READMEs: para atualizar, rodar `scripts/coletar.py` e
  publicar de novo.
- O plano gratuito do Gemini tem cota baixa e o Google pode usar os dados
  enviados para melhorar os produtos dele; aqui só vão READMEs públicos.
- O limite de uso fica em memória e zera quando o contêiner reinicia.

## Autoria

Construído com apoio de IA (Claude, da Anthropic) sob minha direção: eu defini
o problema, as regras (citar fonte, não inventar, custo zero) e revisei o
resultado; a IA gerou boa parte do código.

Matheus de Oliveira Pereira · [github.com/Matheus5339](https://github.com/Matheus5339)
