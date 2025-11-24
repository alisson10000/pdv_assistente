# app/modules/assistente/services/service.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import traceback
import uuid

from app.modules.assistente.kernel.agent_hibrido import agente_hibrido
from app.modules.assistente.kernel.agent_rag import recuperar_contexto_rag
from app.modules.assistente.services.service_sugestivo import executar_sugestivo

from app.modules.assistente.models.model import ChatMessage
from app.core.openai_client import gerar_embedding

# ================================================================
# ANSI COLORS
# ================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def log_info(msg):    print(f"{BLUE}[SERVICE][INFO]{RESET} {msg}")
def log_warn(msg):    print(f"{YELLOW}[SERVICE][WARN]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[SERVICE][OK]{RESET} {msg}")
def log_error(msg):   print(f"{RED}[SERVICE][ERRO]{RESET} {msg}")


# ================================================================
# 🧩 Função interna — obtém ou cria um session_id
# ================================================================
def obter_ou_criar_session_id(db_ia: Session, vendedor_id: int) -> str:
    try:
        row = db_ia.execute(
            text("""
                SELECT session_id
                FROM chat_messages
                WHERE vendedor_id = :v
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"v": vendedor_id}
        ).fetchone()

        if row and row.session_id:
            log_info(f"Reutilizando session_id existente: {row.session_id}")
            return row.session_id

        novo = str(uuid.uuid4())
        log_info(f"Criando novo session_id: {novo}")
        return novo

    except Exception:
        log_error("Erro ao obter/criar session_id:")
        print(RED + traceback.format_exc() + RESET)
        return str(uuid.uuid4())


# ================================================================
# SERVIÇO PRINCIPAL DO ASSISTENTE
# ================================================================
def processar_mensagem(
    vendedor_id: int,
    mensagem: str,
    db_ia: Session,
    cliente_id: int | None = None   # ⭐ AJUSTE FINO
):
    log_info("Iniciando processamento da mensagem...")

    # Criar ou recuperar session_id
    session_id = obter_ou_criar_session_id(db_ia, vendedor_id)

    # 1️⃣ Registrar a mensagem recebida
    try:
        emb = gerar_embedding(mensagem)
        msg_reg = ChatMessage(
            session_id=session_id,
            vendedor_id=vendedor_id,
            sender="vendedor",
            message=mensagem,
            embedding=emb
        )
        db_ia.add(msg_reg)
        db_ia.commit()
        db_ia.refresh(msg_reg)

        log_success(f"Mensagem registrada (ID={msg_reg.id}, session={session_id})")

    except Exception:
        db_ia.rollback()
        log_error("Falha ao registrar a mensagem:")
        print(RED + traceback.format_exc() + RESET)
        raise Exception("Erro ao registrar mensagem")

    # 2️⃣ Agente Híbrido
    try:
        log_info("Chamando agente híbrido...")

        resposta_final = agente_hibrido(
            db_ia=db_ia,
            vendedor_id=vendedor_id,
            pergunta=mensagem,
            recuperar_contexto_rag=recuperar_contexto_rag
        )

        log_success("Resposta híbrida gerada com sucesso.")

    except Exception:
        log_error("Erro dentro do agente híbrido:")
        print(RED + traceback.format_exc() + RESET)
        resposta_final = "Não consegui gerar uma resposta agora."

    # 3️⃣ Registrar resposta do assistente
    try:
        emb_resp = gerar_embedding(resposta_final)

        msg_assist = ChatMessage(
            session_id=session_id,
            vendedor_id=vendedor_id,
            sender="assistente",
            message=resposta_final,
            embedding=emb_resp
        )
        db_ia.add(msg_assist)
        db_ia.commit()
        db_ia.refresh(msg_assist)

        log_success(f"Resposta do assistente registrada (ID={msg_assist.id})")

    except Exception:
        db_ia.rollback()
        log_error("Erro ao registrar resposta do assistente:")
        print(RED + traceback.format_exc() + RESET)

    # 4️⃣ Agente Sugestivo — ⭐ agora passa o cliente_id corretamente
    try:
        executar_sugestivo(
            db_ia=db_ia,
            vendedor_id=vendedor_id,
            pergunta=mensagem,
            resposta_llm=resposta_final,
            chat_message_id=msg_reg.id,
            cliente_id=cliente_id   # ⭐ AGORA É REPASSADO
        )

        log_success("Agente sugestivo executado.")

    except Exception:
        log_error("Falha ao executar agente sugestivo:")
        print(RED + traceback.format_exc() + RESET)

    return resposta_final
