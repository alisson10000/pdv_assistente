from fastapi import FastAPI
from sqlalchemy import text

# Engines dos dois bancos
from app.core.database_pdv import engine_pdv
from app.core.database_ia import engine_ia

# CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Assistente PDV",
    description="API do Assistente Inteligente do PDV integrado ao banco do sistema e ao banco IA.",
    version="1.0.0"
)

# ======================================================
# CORS – NECESSÁRIO PARA O FRONT (React em localhost:3000)
# ======================================================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # libera seu front
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, OPTIONS...
    allow_headers=["*"],        # Authorization, Content-Type, etc.
)

# ======================================================
# IMPORTS E INCLUSÃO DE ROUTERS (após o CORS)
# ======================================================

from app.modules.assistente.router.router import router as assistente_router
app.include_router(assistente_router)

from app.modules.pdv.router import router as pdv_router
app.include_router(pdv_router)

# ======================================================
# ENDPOINT: Testar banco do sistema (PDV)
# ======================================================

@app.get("/teste-banco", tags=["Sistema PDV"])
def testar_conexao():
    try:
        with engine_pdv.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            return {
                "status": "✅ Conectado ao banco PDV!",
                "banco": result.scalar()
            }
    except Exception as e:
        return {
            "status": "❌ Erro na conexão PDV",
            "detalhe": str(e)
        }

# ======================================================
# ENDPOINT: Testar banco IA (pgvector)
# ======================================================

@app.get("/teste-banco-ia", tags=["IA"])
def testar_conexao_ia():
    try:
        with engine_ia.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            return {
                "status": "✅ Conectado ao banco IA!",
                "banco": result.scalar()
            }
    except Exception as e:
        return {
            "status": "❌ Erro na conexão IA",
            "detalhe": str(e)
        }

# ======================================================
# ROTA PRINCIPAL
# ======================================================

@app.get("/", tags=["Info"])
def home():
    return {
        "message": "Assistente PDV rodando com sucesso!",
        "testes": {
            "banco_sistema": "/teste-banco",
            "banco_ia": "/teste-banco-ia"
        }
    }
