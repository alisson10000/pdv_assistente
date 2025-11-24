from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL_SISTEMA = os.getenv("DATABASE_URL_SISTEMA")

engine_pdv = create_engine(DATABASE_URL_SISTEMA)

SessionPDV = sessionmaker(autocommit=False, autoflush=False, bind=engine_pdv)

BasePDV = declarative_base()

def get_db_pdv():
    db = SessionPDV()
    try:
        yield db
    finally:
        db.close()
