FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro (melhor cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Código do projeto
COPY . /app

# Garante pastas esperadas (sem alterar estrutura)
RUN mkdir -p /app/cookies /app/data

# Executa o teu script principal (mantém CLI)
ENTRYPOINT ["python", "main.py"]
CMD ["--all", "--local", "--verbose"]
