"""API e página web do assistente de portfólio."""

import os
import time
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv()  # lê o .env local, se existir (no Azure, a chave vem dos segredos)

from app import rag  # noqa: E402  (depois do load_dotenv)
from app.indice import carregar  # noqa: E402

# Limite global simples para proteger a cota gratuita do Gemini.
LIMITE_POR_HORA = int(os.getenv("LIMITE_POR_HORA", "30"))
_chamadas: deque[float] = deque()

app = FastAPI(title="Assistente de portfólio (RAG)")
STATIC = Path(__file__).parent / "static"
indice = carregar()


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=3, max_length=300)


def _dentro_do_limite() -> bool:
    agora = time.time()
    while _chamadas and agora - _chamadas[0] > 3600:
        _chamadas.popleft()
    if len(_chamadas) >= LIMITE_POR_HORA:
        return False
    _chamadas.append(agora)
    return True


@app.get("/")
def pagina():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "trechos": len(indice.trechos), "ia_configurada": bool(os.getenv("GEMINI_API_KEY"))}


@app.get("/api/repos")
def repos():
    return indice.repos


@app.get("/api/buscar")
def buscar(q: str):
    """Só a etapa de busca, sem IA: mostra quais trechos seriam usados."""
    return [
        {"repo": t.repo, "secao": t.secao, "nota": nota, "texto": t.texto[:300]}
        for t, nota in indice.buscar(q)
    ]


@app.post("/api/perguntar")
def perguntar(p: Pergunta):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(503, "IA não configurada (falta GEMINI_API_KEY).")
    if not _dentro_do_limite():
        raise HTTPException(429, "Limite de uso da demo atingido. Tente mais tarde.")
    try:
        return rag.responder(p.pergunta, indice)
    except Exception as erro:  # erro do provedor (cota, rede): não vaza detalhes
        print(f"erro no RAG: {type(erro).__name__}: {erro}")
        raise HTTPException(502, "Falha ao consultar o modelo de IA. Tente de novo em instantes.")
