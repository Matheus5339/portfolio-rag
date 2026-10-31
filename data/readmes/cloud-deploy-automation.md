Cloud Deploy Automation

![CI/CD](https://github.com/Matheus5339/cloud-deploy-automation/actions/workflows/deploy.yml/badge.svg)

CI/CD Pipeline

Projeto DevOps desenvolvido com FastAPI, Docker, GitHub Actions e automação de deploy com Bash Script.

---

Tecnologias Utilizadas
Python 3.11  
FastAPI  
Docker  
GitHub Actions  
Bash Script  
Railway (Deploy)

---

Funcionalidades
API REST com FastAPI  
Health Check  
Container Docker  
CI/CD com GitHub Actions  
Deploy automatizado por ambiente (staging e production)  
Automação de build com script Bash  
Deploy real em cloud (Railway)

---

Endpoints

Root  
GET /

Retorna status da aplicação

Health Check  
GET /health

Retorna status da aplicação e uptime + ambiente

---

Rodando localmente

Criar ambiente virtual
python -m venv venv

Ativar ambiente virtual

Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate

---

Instalar dependências
pip install -r requirements.txt

---

Rodar aplicação
uvicorn app.main:app --reload

Acesso:
http://localhost:8000
http://localhost:8000/health
http://localhost:8000/docs

---

Rodando com Docker

Build da imagem
docker build -t cloud-deploy-automation .

Rodar container
docker run -p 8000:8000 cloud-deploy-automation

---

CI/CD

O projeto utiliza GitHub Actions para:

- Execução automática de validação
- Build da imagem Docker
- Deploy por ambiente (staging e production)
- Automação de pipeline a cada push

Fluxo do pipeline:

Push no GitHub  
↓  
GitHub Actions  
↓  
Testes  
↓  
Build Docker  
↓  
Deploy staging (develop)  
↓  
Deploy production (main)

---

Deploy

Deploy realizado no Railway com CI/CD automatizado.

🔗 URL do projeto:
https://cloud-deploy-automation.railway.app

Health Check Online:
https://cloud-deploy-automation.railway.app/health

Swagger Online:
https://cloud-deploy-automation.railway.app/docs

---

O que este projeto demonstra

- CI/CD real com GitHub Actions
- Containerização com Docker
- Automação de deploy
- Integração com cloud (Railway)
- Estrutura de projeto DevOps profissional

---

Autor
Matheus Pereira