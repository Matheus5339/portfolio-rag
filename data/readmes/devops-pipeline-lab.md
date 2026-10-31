# DevOps Pipeline Lab

[![CI/CD Pipeline](https://github.com/Matheus5339/devops-pipeline-lab/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Matheus5339/devops-pipeline-lab/actions/workflows/ci-cd.yml)

Projeto DevOps desenvolvido com FastAPI, Docker, GitHub Actions e Railway.

## Tecnologias Utilizadas

- Python 3.11
- FastAPI
- Docker
- GitHub Actions
- Railway
- Pytest

---

## Funcionalidades

- API REST com FastAPI
- Health Check
- Métricas básicas
- Testes automatizados
- CI/CD com GitHub Actions
- Deploy automatizado no Railway
- Container Docker

---

## Endpoints

### Root

GET /

### Health Check

GET /health

### Metrics

GET /metrics

### Item por ID

GET /items/{item_id}

---

## Rodando localmente

### Criar ambiente virtual

```bash
python -m venv venv
```

### Ativar ambiente virtual

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Rodar aplicação

```bash
uvicorn app.main:app --reload
```

---

## Rodando com Docker

### Build da imagem

```bash
docker build -t devops-pipeline-lab .
```

### Rodar container

```bash
docker run -p 8000:8000 devops-pipeline-lab
```

---

## Testes

```bash
pytest tests/ -v
```

---

## CI/CD

O projeto utiliza GitHub Actions para:

- execução automática de testes
- validação do build Docker
- integração contínua

---

## Deploy

Deploy realizado no Railway.

### Health Check Online

https://devops-pipeline-lab-production.up.railway.app/health

### Swagger Online

https://devops-pipeline-lab-production.up.railway.app/docs

---

## Autor

Matheus Pereira