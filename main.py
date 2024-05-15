from fastapi import FastAPI

from . import models
from .database import engine
from .routes import router as log_router

# Crée les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    pass 

@app.on_event("shutdown")
async def shutdown():
    pass  

app.include_router(log_router)
