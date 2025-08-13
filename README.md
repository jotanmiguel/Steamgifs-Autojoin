# SteamGifts Autojoin Bot

Um bot para automatizar a entrada em giveaways do [SteamGifts](https://www.steamgifts.com).
De momento só funciona para firefox. Se necessário posso criar versões para outros browsers (Chromium, etc...)

## Funcionalidades

- Carrega cookies da Steam/SteamGifts para manter a sessão ativa.
- Busca giveaways disponíveis.
- Verifica se já participaste ou se tens pontos suficientes.
- Entra automaticamente nos giveaways.
- Logs coloridos e detalhados na consola.

## Requisitos

- Python 3.10+
- Pacotes: `requests`, `beautifulsoup4`

Instalação das dependências:

```bash
pip install -r requirements.txt
```

Como usar
  Rodar o bot:
  ```bash
  python main.py --max-pages 5 --verbose
  ```
  >
  > --max-pages: número máximo de páginas de giveaways a buscar (default: 5)
  >
  > --verbose: ativa logs detalhados (DEBUG)

Estrutura do projeto:
```
├── main.py               # Script principal
├── src/                  # Código fonte
│   ├── save_cookies.py
│   ├── session_manager.py
│   ├── get_giveaways.py
│   ├── join_giveaways.py
│   └── config.py
├── utils/                # Funções utilitárias
│   └── logger.py
├── cookies/              # Cookies SteamGifts
├── data/                 # Dados dos giveaways recolhidos
└── requirements.txt

```

Avisos
* O site pode bloquear requisições em excesso (HTTP 429). Use com moderação.
* O bot não garante ganhos; respeita os termos do SteamGifts.
