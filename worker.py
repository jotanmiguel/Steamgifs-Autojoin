from workers import WorkerEntrypoint, Response
import main

class Default(WorkerEntrypoint):
    async def fetch(self,env, request):
        main.main(env=env)
        return Response("✅ Cron executed", status=200)