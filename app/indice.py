"""Índice de busca TF-IDF sobre os READMEs, em Python puro.

Decisão: TF-IDF em vez de embeddings. Para ~15 documentos curtos é suficiente,
não gasta cota da API, roda em milissegundos e dá para explicar a conta
linha a linha. Embeddings seriam o próximo passo se a base crescesse.
"""

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

USUARIO = "Matheus5339"
PASTA = Path(__file__).resolve().parent.parent / "data" / "readmes"
TAMANHO_MAX = 1200  # caracteres por trecho
TAMANHO_MIN = 60  # trechos menores (ex.: "Licença: MIT") só atrapalham a busca

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para pra com sem
e ou que se ao aos à às é ser foi são como mais mas seu sua seus suas ele ela
isso esse essa este esta the of and to in for is on with by it this that be are
qual quais quem onde quando porque ja tem ter usa usou usar fez feito
""".split())


@dataclass
class Trecho:
    repo: str
    secao: str
    texto: str

    @property
    def url(self) -> str:
        return f"https://github.com/{USUARIO}/{self.repo}"


def normalizar(texto: str) -> list[str]:
    """Minúsculas, sem acento, só palavras com 2+ caracteres e sem stopwords."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9#+.]{2,}", texto) if t.strip(".") not in STOPWORDS]


def dividir(repo: str, markdown: str) -> list[Trecho]:
    """Quebra o README por títulos (#, ##, ###); seções longas viram vários trechos."""
    trechos, secao, linhas = [], "início", []

    def fechar():
        corpo = "\n".join(linhas).strip()
        for i in range(0, len(corpo), TAMANHO_MAX):
            pedaco = corpo[i:i + TAMANHO_MAX].strip()
            if len(pedaco) >= TAMANHO_MIN:
                trechos.append(Trecho(repo, secao, pedaco))

    em_codigo = False
    for linha in markdown.splitlines():
        if linha.lstrip().startswith("```"):
            em_codigo = not em_codigo  # "# comentário" dentro de bloco de código não é título
        titulo = None if em_codigo else re.match(r"^#{1,3}\s+(.*)", linha)
        if titulo:
            fechar()
            secao, linhas = titulo.group(1).strip(), []
        else:
            linhas.append(linha)
    fechar()
    return trechos


class Indice:
    def __init__(self, trechos: list[Trecho]):
        self.trechos = trechos
        # O nome do repositório e da seção entram no texto indexado: ajudam
        # perguntas como "o que é o pico-db?".
        docs = [Counter(normalizar(f"{t.repo} {t.repo.replace('-', ' ')} {t.secao} {t.texto}")) for t in trechos]
        n = len(docs)
        df = Counter(termo for d in docs for termo in d)
        self.idf = {termo: math.log((1 + n) / (1 + f)) + 1 for termo, f in df.items()}
        self.vetores = [self._vetor(d) for d in docs]

    def _vetor(self, contagem: Counter) -> dict[str, float]:
        v = {t: (1 + math.log(c)) * self.idf.get(t, 0) for t, c in contagem.items()}
        norma = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norma for t, x in v.items()}

    def buscar(self, pergunta: str, k: int = 5) -> list[tuple[Trecho, float]]:
        q = self._vetor(Counter(normalizar(pergunta)))
        notas = [(sum(q.get(t, 0) * x for t, x in v.items()), i) for i, v in enumerate(self.vetores)]
        melhores = sorted((n for n in notas if n[0] > 0), reverse=True)[:k]
        return [(self.trechos[i], round(nota, 3)) for nota, i in melhores]

    @property
    def repos(self) -> list[str]:
        return sorted({t.repo for t in self.trechos})


def carregar(pasta: Path = PASTA) -> Indice:
    trechos = []
    for arquivo in sorted(pasta.glob("*.md")):
        trechos += dividir(arquivo.stem, arquivo.read_text(encoding="utf-8"))
    return Indice(trechos)
