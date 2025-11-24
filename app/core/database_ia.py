from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_IA = os.getenv("DATABASE_URL_IA")

if not DATABASE_URL_IA:
    raise ValueError("❌ ERRO: Variável DATABASE_URL_IA não encontrada no .env")

# ================================================================
#  ENGINE — OTIMIZADA PARA POSTGRES + PGVECTOR + FASTAPI
# ================================================================
engine_ia = create_engine(
    DATABASE_URL_IA,
    pool_pre_ping=True,          # evita desconexões
    future=True,                 # modo SQLAlchemy 2.0 (recomendado)
    pool_size=5,                 # conexões mínimas
    max_overflow=10,             # conexões extras quando necessário
)

# ================================================================
#  SESSION
# ================================================================
SessionIA = sessionmaker(
    bind=engine_ia,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False       # evita reconsultas desnecessárias
)

# Base para models
BaseIA = declarative_base()


# ================================================================
#  DEPENDÊNCIA DO FASTAPI
# ================================================================
def get_db_ia():
    db = SessionIA()
    try:
        yield db
    finally:
        db.close()
