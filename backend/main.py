from fastapi import FastAPI
from db import engine
from sqlmodel import SQLModel
import models
from routes import transactions, user, auth

app = FastAPI()
SQLModel.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(user.router)