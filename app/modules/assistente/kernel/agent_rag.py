# app/modules/assistente/kernel/agent_rag.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
from app.core.openai_client import gerar_embedding

# ================================================================
# ANSI COLORS
# ================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"

# ================================================================
# 🟪 RAG — Recuperação via pgvector (com logs coloridos)
# ================================================================
def recuperar_contexto_rag(db_ia: Session, vendedor_id: int, pergunta: str, k: int = 5):

    print(f"\n{PURPLE}==========================================================")
    print("🟪 [RAG][INIT] Recuperação RAG iniciada")
    print(f"🟪 [RAG][INPUT] vendedor_id={vendedor_id} | pergunta={pergunta}")
    print("==========================================================" + RESET)

    # ============================================================
    # 1) Embedding
    # ============================================================
    print(PURPLE + "🟪 [RAG][STEP1] Gerando embedding..." + RESET)
    try:
        emb = np.array(gerar_embedding(pergunta), dtype=float)
        print(PURPLE + "🟪 [RAG][STEP1-OK] Embedding gerado." + RESET)
    except Exception as e:
        print(f"{RED}❌ [RAG][STEP1-ERRO] Falha ao gerar embedding: {e}{RESET}")
        return "Nenhum contexto encontrado."

    # Normalização
    norm = np.linalg.norm(emb)
    emb_norm = emb / norm if norm else emb
    literal = "[" + ",".join(f"{x:.6f}" for x in emb_norm) + "]"

    print(PURPLE + "🟪 [RAG][STEP2] Embedding normalizado." + RESET)

    # ============================================================
    # 2) Consulta pgvector
    # ============================================================
    print(PURPLE + "🟪 [RAG][STEP3] Consultando pgvector..." + RESET)
    try:
        rows = db_ia.execute(
            text("""
                SELECT message, (1 - (embedding <#> :emb)) AS similarity
                FROM chat_messages
                WHERE vendedor_id = :vid
                ORDER BY embedding <#> :emb
                LIMIT :k;
            """),
            {"emb": literal, "vid": vendedor_id, "k": k}
        ).fetchall()

        print(PURPLE + "🟪 [RAG][STEP3-OK] Consulta concluída." + RESET)

    except Exception as e:
        print(f"{RED}❌ [RAG][STEP3-ERRO] Erro ao consultar pgvector: {e}{RESET}")
        return "Nenhum contexto encontrado."

    if not rows:
        print(f"{YELLOW}🟡 [RAG][INFO] Nenhum contexto encontrado.{RESET}")
        return "Nenhum contexto encontrado."

    # ============================================================
    # 3) Construção final do contexto
    # ============================================================
    print(PURPLE + "🟪 [RAG][STEP4] Processando resultados..." + RESET)
    try:
        contexto = "\n".join(
            f"- ({round(r.similarity, 3)}) {r.message}"
            for r in rows
        )
        print(GREEN + "🟢 [RAG][OK] Contexto gerado com sucesso." + RESET)

    except Exception as e:
        print(f"{RED}❌ [RAG][STEP4-ERRO] Falha ao montar contexto: {e}{RESET}")
        return "Nenhum contexto encontrado."

    return contexto
