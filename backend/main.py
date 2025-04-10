from fastapi import FastAPI
from db import engine
from sqlmodel import SQLModel
from routes import router
import models

app = FastAPI()
SQLModel.metadata.create_all(bind=engine)

app.include_router(router)
