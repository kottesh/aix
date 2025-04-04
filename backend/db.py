from fastapi import Depends
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from typing import Annotated 
import os

load_dotenv()


DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

db_dependency = Annotated[Session, Depends(get_session)]
