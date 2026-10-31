FROM python:3.13-slim

# Sem .pyc e com log direto no stdout (o Azure lê o stdout).
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app

# Dependências antes do código: aproveita o cache de camadas do Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

# Roda como usuário sem privilégios de root.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
