from fastapi import FastAPI
from . import models
from .database import engine
from .routes import router  # Assurez-vous d'importer le routeur correctement

# Crée les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    pass 

@app.on_event("shutdown")
async def shutdown():
    pass  

app.include_router(router)  # Incluez le routeur une seule fois
