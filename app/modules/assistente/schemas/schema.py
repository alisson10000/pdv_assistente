# app/modules/assistente/schemas/schema.py

from pydantic import BaseModel
from typing import Optional, List

# ================================================================
# ANSI LOGS
# ================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def log_info(msg):    print(f"{BLUE}[SCHEMA][INFO]{RESET} {msg}")
def log_warn(msg):    print(f"{YELLOW}[SCHEMA][WARN]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[SCHEMA][OK]{RESET} {msg}")
def log_error(msg):   print(f"{RED}[SCHEMA][ERRO]{RESET} {msg}")


# ================================================================
# 🔹 MODELOS EXIGIDOS PELO ROUTER (NÃO REMOVER)
# ================================================================
class ChatRequest(BaseModel):
    vendedor_id: int
    mensagem: str


class ChatResponse(BaseModel):
    resposta: str


# ================================================================
# 🔹 SEUS MODELOS (mantidos, funcionando)
# ================================================================
class Msg(BaseModel):
    message: str


class AssistenteRequest(BaseModel):
    vendedor_id: int
    pergunta: str
    cliente_id: Optional[int] = None

    def log(self):
        log_info(f"Recebida pergunta do vendedor={self.vendedor_id}, cliente={self.cliente_id}")
        log_info(f"Pergunta: {self.pergunta}")


class AssistenteResponse(BaseModel):
    resposta: str

    def log(self):
        log_success("Resposta enviada ao vendedor.")
        log_info(self.resposta[:200] + ("..." if len(self.resposta) > 200 else ""))


# ================================================================
# 🔹 Estruturas de recomendação
# ================================================================
class RecomendacaoItem(BaseModel):
    produto_id: int
    nome: Optional[str]
    score: float


class ListaRecomendacoes(BaseModel):
    cliente_id: Optional[int]
    recomendacoes: List[RecomendacaoItem]
