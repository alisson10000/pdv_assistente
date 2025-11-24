# app/modules/assistente/kernel/agent_sugestivo.py

from sqlalchemy.orm import Session
import traceback

# modelos — agora compatíveis com o banco real
from app.modules.assistente.models.model import (
    InteracaoCliente,
    PreferenciaCliente,
    RecomendacaoRegistrada,
)

# recomendador híbrido corrigido
from app.modules.assistente.kernel.recomendador_hibrido import (
    recomendar_produtos_para_cliente
)

# ====================================================================
# ANSI
# ====================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
MAGENTA = "\033[95m"
RESET  = "\033[0m"


def log_info(msg):     print(f"{BLUE}[SUGESTIVO][INFO]{RESET} {msg}")
def log_warn(msg):     print(f"{YELLOW}[SUGESTIVO][WARN]{RESET} {msg}")
def log_ok(msg):       print(f"{GREEN}[SUGESTIVO][OK]{RESET} {msg}")
def log_error(msg):    print(f"{RED}[SUGESTIVO][ERRO]{RESET} {msg}")


# ====================================================================
# 🚀 AGENTE SUGESTIVO — com recomendador híbrido integrado
# ====================================================================
class SugestivoService:

    # -------------------------------------------------------------
    # 1) Registrar Interação
    # -------------------------------------------------------------
    def registrar_interacao(
        self,
        db: Session,
        chat_message_id: int,
        cliente_id: int | None,
        vendedor_id: int | None,
        tipo: str,
        detalhe: str
    ):
        log_info("Registrando interação...")

        if not chat_message_id:
            log_error("chat_message_id ausente — ignorando interação.")
            return None

        try:
            interacao = InteracaoCliente(
                chat_message_id=chat_message_id,
                cliente_id=cliente_id,
                vendedor_id=vendedor_id,
                tipo=tipo or "indefinido",
                detalhe=detalhe or "",
            )

            db.add(interacao)
            db.commit()
            db.refresh(interacao)

            log_ok(f"Interação registrada (ID={interacao.id})")
            return interacao

        except Exception:
            db.rollback()
            log_error("Falha ao registrar interação")
            print(RED + traceback.format_exc() + RESET)
            return None

    # -------------------------------------------------------------
    # 2) Registrar Preferência
    # -------------------------------------------------------------
    def registrar_preferencia(
        self,
        db: Session,
        cliente_id: int,
        chave: str,
        valor: str,
        fonte: str = "ia",
        peso: float = 1.0,
    ):
        log_info("Registrando preferência...")

        if not cliente_id:
            log_warn("cliente_id=None → preferência ignorada.")
            return None

        try:
            pref = PreferenciaCliente(
                cliente_id=cliente_id,
                chave=chave,
                valor=valor,
                fonte=fonte,
                peso=peso
            )

            db.add(pref)
            db.commit()
            db.refresh(pref)

            log_ok(f"Preferência registrada (ID={pref.id})")
            return pref

        except Exception:
            db.rollback()
            log_error("Erro ao registrar preferência")
            print(RED + traceback.format_exc() + RESET)
            return None

    # -------------------------------------------------------------
    # 3) Registrar Recomendação
    # -------------------------------------------------------------
    def registrar_recomendacao(
        self,
        db: Session,
        cliente_id: int | None,
        vendedor_id: int | None,
        produto_id: int | None,
        motivo: str,
        score: float
    ):
        log_info(f"Registrando recomendação (produto_id={produto_id})...")

        try:
            rec = RecomendacaoRegistrada(
                cliente_id=cliente_id,
                vendedor_id=vendedor_id,
                produto_id=produto_id,
                motivo=motivo[:500],
                score=score,
            )

            db.add(rec)
            db.commit()
            db.refresh(rec)

            log_ok(f"Recomendação salva (ID={rec.id})")
            return rec

        except Exception:
            db.rollback()
            log_error("Erro ao registrar recomendação")
            print(RED + traceback.format_exc() + RESET)
            return None


# ====================================================================
# 🔥 Função principal do Agente Sugestivo
# ====================================================================
def processar_resposta_sugestiva(
    db_ia: Session,
    vendedor_id: int,
    pergunta: str,
    resposta_llm: str,
    chat_message_id: int,
    cliente_id: int | None
):
    log_info("Executando pós-processamento sugestivo...")

    servico = SugestivoService()

    try:
        # ---------------------------------------------------------
        # 1) Registrar interação da resposta
        # ---------------------------------------------------------
        servico.registrar_interacao(
            db=db_ia,
            chat_message_id=chat_message_id,
            cliente_id=cliente_id,
            vendedor_id=vendedor_id,
            tipo="resposta_llm",
            detalhe=pergunta
        )

        # ---------------------------------------------------------
        # 2) Registrar preferência detectada na resposta
        # ---------------------------------------------------------
        if "gost" in resposta_llm.lower() or "prefere" in resposta_llm.lower():
            servico.registrar_preferencia(
                db_ia,
                cliente_id=cliente_id,
                chave="afinidade",
                valor=resposta_llm[:200]
            )

        # ---------------------------------------------------------
        # 3) Identificar intenção de recomendação
        # ---------------------------------------------------------
        gatilhos = [
            "recomende", "sugira", "indique", "recomendações",
            "sugestões", "produtos para", "sugerir", "indicar"
        ]

        if any(g in pergunta.lower() for g in gatilhos):
            log_info("Intenção de RECOMENDAÇÃO detectada → chamando motor híbrido...")

            recomendacoes = recomendar_produtos_para_cliente(
                db_ia=db_ia,
                cliente_id=cliente_id,
                limite=5
            )

            # Registrar recomendações
            for rec in recomendacoes:
                # 🟢 CORREÇÃO 3.3: Usa o motivo retornado pelo recomendador (se houver), caso contrário usa default.
                motivo_final = rec.motivo if hasattr(rec, "motivo") else "similaridade_embeddings"

                servico.registrar_recomendacao(
                    db=db_ia,
                    cliente_id=cliente_id,
                    vendedor_id=vendedor_id,
                    produto_id=rec.id if hasattr(rec, "id") else None,
                    motivo=motivo_final,
                    score=float(rec.score) if hasattr(rec, "score") else 0.5
                )

        log_ok("Agente Sugestivo finalizado com sucesso.")

    except Exception:
        log_error("Falha geral no agente sugestivo:")
        print(RED + traceback.format_exc() + RESET)