# app/modules/assistente/services/service_sugestivo.py

from sqlalchemy.orm import Session
import traceback

# núcleo do agente sugestivo
from app.modules.assistente.kernel.agent_sugestivo import (
    processar_resposta_sugestiva
)

# ================================================================
# ANSI COLORS
# ================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def log_info(msg):    print(f"{BLUE}[SVC-SUGESTIVO][INFO]{RESET} {msg}")
def log_warn(msg):    print(f"{YELLOW}[SVC-SUGESTIVO][WARN]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[SVC-SUGESTIVO][OK]{RESET} {msg}")
def log_error(msg):   print(f"{RED}[SVC-SUGESTIVO][ERRO]{RESET} {msg}")


# ================================================================
# WRAPPER — Camada intermediária entre service.py e agent_sugestivo
# ================================================================
def executar_sugestivo(
    db_ia: Session,
    vendedor_id: int,
    pergunta: str,
    resposta_llm: str,
    chat_message_id: int,
    cliente_id: int | None
):
    log_info("Executando módulo sugestivo...")

    try:
        processar_resposta_sugestiva(
            db_ia=db_ia,
            vendedor_id=vendedor_id,
            pergunta=pergunta,
            resposta_llm=resposta_llm,
            chat_message_id=chat_message_id,
            cliente_id=cliente_id
        )

        log_success("Módulo sugestivo finalizado com sucesso.")

    except Exception as e:
        log_error(f"Erro ao executar módulo sugestivo: {e}")
        print(RED + traceback.format_exc() + RESET)
