# Agente de compras de restaurante

Agente de IA que sugere a **lista de compras da semana por fornecedor** de um
restaurante pequeno e **explica o porquê** de cada item.

> **Dados fictícios.** Estoque, consumo, preços e fornecedores foram inventados.
> A rotina que o agente imita é real: fui sócio-administrador de um restaurante
> por 7 anos, com 4 fornecedores e equipe de 7 pessoas, e fazer o pedido semanal
> era uma das tarefas que mais tomavam tempo.

**Demo no ar:** _(link após o deploy)_

## O que ele faz

- Página web: você pergunta ("monte a lista da semana", "por que tanta batata?",
  "algum fornecedor ficou abaixo do pedido mínimo?") e o agente responde,
  mostrando quais ferramentas usou.
- API:
  - `POST /api/sugerir` `{"pergunta": "..."}` → resposta do agente + rastro das ferramentas
  - `GET /api/lista` → lista calculada só pelas regras, **sem IA** (para conferir o agente)
  - `GET /api/estoque` · `GET /health`

## Como funciona

```
pergunta ──► Gemini (decide qual ferramenta chamar)
               │  function calling
               ▼
           ferramentas em Python ──► dados fictícios
           (estoque, previsão, compra, lista por fornecedor)
               │  resultado
               ▼
           Gemini explica ──► resposta + rastro das ferramentas
```

Ferramentas (`app/ferramentas.py`):

| Ferramenta | O que faz |
|---|---|
| `listar_fornecedores` | pedido mínimo e dias de entrega |
| `consultar_estoque` | estoque atual (por fornecedor, opcional) |
| `prever_consumo` | média ponderada das 4 últimas semanas (pesos 1-2-3-4) |
| `calcular_compra` | previsão + estoque de segurança − estoque, arredondado na embalagem |
| `montar_lista_compras` | tudo agrupado por fornecedor, com aviso de pedido mínimo |

## Decisões

- **A IA não faz conta.** Toda a aritmética fica em Python, testada. O modelo
  só escolhe as ferramentas e explica. LLM erra conta e não é auditável; aqui
  qualquer número da resposta pode ser conferido em `/api/lista`.
- **Loop do agente manual** (`app/agente.py`), sem a chamada automática de
  funções do SDK, para registrar e mostrar cada ferramenta usada. Limite de 8 passos.
- **Regras de negócio de restaurante:** perecível (tomate, alface, carne) não
  leva estoque de segurança, porque estraga; compra-se em múltiplos da
  embalagem do fornecedor; avisa quando o pedido fica abaixo do mínimo.
- **Custo zero:** Gemini no plano gratuito; hospedagem no Azure Container Apps
  (Azure for Students) com escala para zero; imagem no GitHub Container Registry.
- **Proteção da cota:** limite global de chamadas por hora (`LIMITE_POR_HORA`,
  padrão 30) e pergunta com no máximo 500 caracteres.
- **Chave fora do código:** `GEMINI_API_KEY` vem de variável de ambiente (`.env`
  local, que não vai para o Git; segredo do Container App em produção).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env            # e coloque sua chave grátis do Google AI Studio
pytest -q
uvicorn app.main:app --reload     # http://localhost:8000
```

Com Docker:

```bash
docker build -t agente-compras .
docker run -p 8080:8080 --env-file .env agente-compras
```

## Testes e CI

`pytest` cobre as regras de cálculo, o loop do agente (com um cliente Gemini
falso, sem gastar cota) e a API (sem chave → 503, limite → 429, pergunta longa → 422).
O GitHub Actions roda os testes e publica a imagem em
`ghcr.io/matheus5339/agente-compras-restaurante`.

## Limitações

- Dados fixos em código; num caso real viriam do sistema de PDV/estoque.
- Previsão simples (média ponderada); não considera feriados, clima ou eventos.
- O limite de uso fica em memória e zera quando o contêiner reinicia.
- O plano gratuito do Gemini tem cota baixa e o Google pode usar os dados
  enviados para melhorar os produtos dele; por isso só dados fictícios vão para a IA.
- Com escala para zero, o primeiro acesso depois de um tempo parado demora alguns segundos.

## Autoria

Construído com apoio de IA (Claude, da Anthropic) sob minha direção: eu defini
o problema, as regras de negócio a partir da minha experiência no restaurante e
os critérios de custo e segurança; a IA gerou boa parte do código.

Matheus de Oliveira Pereira · [github.com/Matheus5339](https://github.com/Matheus5339)
