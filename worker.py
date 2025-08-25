from workers import handler
from main import main  # Certifica-te de que a função main() está corretamente importada

@handler
async def on_scheduled(controller, env, ctx):
    print("Cron Trigger acionado")
    main()  # Executa o teu código principal
    print("Execução do main.py concluída")
