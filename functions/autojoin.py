import subprocess
from pathlib import Path

def handle_request(request):
    # Caminho absoluto para o script
    script_path = Path(__file__).parent.parent / "main.py"

    # Executa o script Python e captura o output
    result = subprocess.run(
        ["python3", str(script_path), "--max-pages", "5", "--verbose"],
        capture_output=True,
        text=True
    )

    # Retorna o resultado como resposta HTTP
    return {
        "status": 200,
        "body": result.stdout + "\n" + result.stderr
    }
