from app.indice import Indice, carregar, dividir, normalizar


def test_normalizar_tira_acento_e_stopwords():
    assert normalizar("Ele já usou a Integração com PostgreSQL") == ["integracao", "postgresql"]


def test_dividir_por_titulo_ignora_comentario_em_codigo():
    md = "# Projeto\nTexto de introdução bem explicado sobre o projeto e o objetivo dele.\n" \
         "## Como rodar\n```bash\n# instala as dependências do projeto\npip install -r requirements.txt\n```\n"
    trechos = dividir("repo", md)
    assert [t.secao for t in trechos] == ["Projeto", "Como rodar"]


def test_trecho_curto_e_descartado():
    assert dividir("repo", "# Licença\nMIT\n") == []


def test_busca_acha_o_repositorio_certo(tmp_path):
    (tmp_path / "api-go.md").write_text("# api-go\nAPI HTTP escrita em Go com net/http e testes automatizados com httptest no CI.", encoding="utf-8")
    (tmp_path / "site.md").write_text("# site\nPágina estática em HTML e CSS com carrossel de imagens animado.", encoding="utf-8")
    indice = carregar(tmp_path)
    achados = indice.buscar("qual projeto usa Go?")
    assert achados[0][0].repo == "api-go"
    assert achados[0][0].url == "https://github.com/Matheus5339/api-go"


def test_pergunta_sem_relacao_nao_acha_nada():
    indice = Indice(dividir("repo", "# repo\nAutomação de planilhas de vendas com pandas e openpyxl."))
    assert indice.buscar("receita de bolo de cenoura") == []


def test_base_real_carrega():
    indice = carregar()
    assert len(indice.repos) >= 5
