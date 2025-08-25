from fastapi import FastAPI, Request
from pydantic import BaseModel
import main


async def on_fetch(request, env):
    main.main()