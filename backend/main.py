from fastapi import FastAPI
from db import engine
from sqlmodel import SQLModel
from models import *

app = FastAPI()
SQLModel.metadata.create_all(bind=engine)
