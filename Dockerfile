FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# COOKIES: JSON string of SteamGifts cookies, e.g.:
#   docker run -e COOKIES='{"PHPSESSID":"...","steamLoginSecure":"..."}' ...
# Can also be supplied as a Docker secret or GitHub Actions secret.
ENV COOKIES=""

WORKDIR /app

# Dependências primeiro (melhor cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Código do projeto
COPY . /app

# Garante pastas esperadas (sem alterar estrutura)
RUN mkdir -p /app/data

# Copiar o script
COPY wait-for-fsr.sh /app/wait-for-fsr.sh

# Dar permissão de execução
RUN chmod +x /app/wait-for-fsr.sh

# Run as non-root user for security
RUN useradd -m -s /bin/sh botuser && chown -R botuser /app
USER botuser

ENTRYPOINT ["python", "main.py"]
CMD ["--max-pages", "5"]
