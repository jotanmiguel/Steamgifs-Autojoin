# SteamGifts Autojoin Bot

Um bot para automatizar a entrada em giveaways do [SteamGifts](https://www.steamgifts.com).

## Funcionalidades

- Carrega cookies da Steam/SteamGifts para manter a sessão ativa.
- Busca giveaways disponíveis.
- Verifica se já participaste ou se tens pontos suficientes.
- Entra automaticamente nos giveaways.
- Logs coloridos e detalhados na consola.

---

## 🐳 Docker (recomendado — funciona em qualquer lugar)

A forma mais simples de correr o bot é via Docker, passando os cookies como variável de ambiente.

### 1. Obter os cookies

Abre o browser, faz login no [SteamGifts](https://www.steamgifts.com) e exporta os cookies da sessão como JSON. O valor deve ter o seguinte formato:

```json
{"PHPSESSID": "...", "steamLoginSecure": "..."}
```

> Podes usar extensões como *Cookie-Editor* para exportar os cookies no formato JSON.

### 2. Correr o container

```bash
docker run --rm \
  -e COOKIES='{"PHPSESSID":"...","steamLoginSecure":"..."}' \
  ghcr.io/jotanmiguel/steamgifs-autojoin:main \
  --max-pages 5
```

#### Usando um ficheiro `.env`

```bash
# .env
COOKIES='{"PHPSESSID":"...","steamLoginSecure":"..."}'
```

```bash
docker run --rm --env-file .env ghcr.io/jotanmiguel/steamgifs-autojoin:main --all
```

#### Usando Docker Compose

```yaml
# docker-compose.yml
services:
  steamgifts-bot:
    image: ghcr.io/jotanmiguel/steamgifs-autojoin:main
    environment:
      - COOKIES={"PHPSESSID":"...","steamLoginSecure":"..."}
    command: ["--max-pages", "5"]
```

```bash
docker compose run --rm steamgifts-bot
```

### 3. Opções disponíveis

| Flag | Descrição | Default |
|------|-----------|---------|
| `--max-pages N` | Número máximo de páginas a buscar | `5` |
| `--all` | Busca todas as páginas (ignora `--max-pages`) | — |
| `--verbose` | Ativa logs detalhados (DEBUG) | — |
| `--local` | Usa cookies de ficheiro local em vez da env `COOKIES` | — |

### 4. GitHub Actions / CI

Guarda os cookies como um **secret** do repositório com o nome `COOKIES` e usa o workflow incluído:

```yaml
- name: Run bot
  env:
    COOKIES: ${{ secrets.COOKIES }}
  run: python main.py --all
```

---

## 🐍 Instalação local (Python)

### Requisitos

- Python 3.10+
- Pacotes: `requests`, `beautifulsoup4`, `colorama`

```bash
pip install -r requirements.txt
```

### Correr o bot com cookies de ficheiro local

```bash
# Guardar cookies no ficheiro cookies/steamgifts.json e depois:
python main.py --local --max-pages 5 --verbose
```

### Correr o bot com variável de ambiente

```bash
export COOKIES='{"PHPSESSID":"...","steamLoginSecure":"..."}'
python main.py --max-pages 5
```

---

## Estrutura do projeto

```
├── main.py               # Script principal
├── Dockerfile            # Imagem Docker
├── docker-compose.yml    # (opcional) exemplo Docker Compose
├── src/                  # Código fonte
│   ├── save_cookies.py
│   ├── session_manager.py
│   ├── get_giveaways.py
│   ├── join_giveaways.py
│   └── config.py
├── utils/                # Funções utilitárias
│   └── logger.py
├── data/                 # Dados dos giveaways recolhidos
└── requirements.txt
```

## Avisos

* O site pode bloquear requisições em excesso (HTTP 429). Use com moderação.
* O bot não garante ganhos; respeita os termos do SteamGifts.
* Nunca partilhes os teus cookies — dão acesso à tua conta.
