# main.py
from fastapi import FastAPI
from routes import router  # Absolute import
from database import database  # Absolute import

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(router)
