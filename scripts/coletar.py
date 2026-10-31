"""Baixa os READMEs dos repositórios públicos do GitHub para data/readmes/.

Uso: python scripts/coletar.py [usuario]
Usa só a API pública do GitHub (sem token). Forks e o repositório de perfil
ficam de fora.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

USUARIO = sys.argv[1] if len(sys.argv) > 1 else "Matheus5339"
DESTINO = Path(__file__).resolve().parent.parent / "data" / "readmes"


def _get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "portfolio-rag"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    repos = json.loads(_get(f"https://api.github.com/users/{USUARIO}/repos?per_page=100"))
    salvos = 0
    for repo in repos:
        if repo["fork"] or repo["name"].lower() == USUARIO.lower():
            continue
        try:
            texto = _get(
                f"https://api.github.com/repos/{USUARIO}/{repo['name']}/readme",
                accept="application/vnd.github.raw+json",
            ).decode("utf-8")
        except urllib.error.HTTPError as erro:
            print(f"pulado {repo['name']}: HTTP {erro.code}")
            continue
        (DESTINO / f"{repo['name']}.md").write_text(texto, encoding="utf-8")
        salvos += 1
        print(f"ok {repo['name']}")
    print(f"{salvos} READMEs em {DESTINO}")


if __name__ == "__main__":
    main()
