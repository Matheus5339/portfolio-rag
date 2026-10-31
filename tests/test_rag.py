"""Testa o RAG e a API com um cliente Gemini falso (sem gastar cota)."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import main, rag
from app.indice import Indice, dividir

INDICE = Indice(
    dividir("api-go", "# api-go\nAPI HTTP escrita em Go com net/http, Docker multi-stage e deploy no Azure.")
    + dividir("planilhas", "# planilhas\nAutomação de relatórios de vendas em Excel com pandas e openpyxl.")
)


class ClienteFalso:
    def __init__(self):
        self.prompts = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.prompts.append(contents)
        return SimpleNamespace(text="Usa Go [1].")


def test_prompt_leva_trechos_numerados_e_fontes_voltam():
    cliente = ClienteFalso()
    saida = rag.responder("qual projeto usa Go?", INDICE, cliente=cliente)
    assert saida["resposta"] == "Usa Go [1]."
    assert saida["fontes"][0]["repo"] == "api-go"
    assert "[1] api-go" in cliente.prompts[0]
    assert "Pergunta: qual projeto usa Go?" in cliente.prompts[0]


def test_sem_trecho_relevante_nao_chama_modelo():
    cliente = ClienteFalso()
    saida = rag.responder("receita de bolo de cenoura", INDICE, cliente=cliente)
    assert saida == {"resposta": rag.SEM_RESPOSTA, "fontes": []}
    assert cliente.prompts == []


api = TestClient(main.app)


def test_api_basica():
    assert api.get("/").status_code == 200
    assert api.get("/health").json()["trechos"] > 0
    assert len(api.get("/api/repos").json()) >= 5
    assert api.get("/api/buscar", params={"q": "Docker"}).status_code == 200


def test_sem_chave_503(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert api.post("/api/perguntar", json={"pergunta": "usa Go?"}).status_code == 503


def test_limite_e_validacao(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "teste")
    monkeypatch.setattr(main, "LIMITE_POR_HORA", 1)
    monkeypatch.setattr(main, "_chamadas", main.deque())
    monkeypatch.setattr(main.rag, "responder", lambda p, i: {"resposta": "ok", "fontes": []})
    assert api.post("/api/perguntar", json={"pergunta": "x" * 301}).status_code == 422
    assert api.post("/api/perguntar", json={"pergunta": "usa Go?"}).status_code == 200
    assert api.post("/api/perguntar", json={"pergunta": "usa Go?"}).status_code == 429
