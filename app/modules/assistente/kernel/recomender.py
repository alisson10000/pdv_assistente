# app/modules/assistente/kernel/recomender.py

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text

# ================================================================
# ANSI LOG
# ================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def log_info(msg):    print(f"{BLUE}[RECOMENDER][INFO]{RESET} {msg}")
def log_warn(msg):    print(f"{YELLOW}[RECOMENDER][WARN]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[RECOMENDER][OK]{RESET} {msg}")
def log_error(msg):   print(f"{RED}[RECOMENDER][ERRO]{RESET} {msg}")


# ================================================================
# 🔹 RECOMENDA PRODUTOS SEMELHANTES A PARTIR DE EMBEDDING
# ================================================================
def recomendar_por_embedding(db_ia: Session, embedding_vector, limite=5):
    log_info("Iniciando recomendação por similaridade de embedding...")

    if embedding_vector is None:
        log_warn("Embedding vazio → nenhuma recomendação possível.")
        return []

    try:
        vetor = np.array(embedding_vector, dtype=float)
        norma = np.linalg.norm(vetor)

        if norma > 0:
            vetor = vetor / norma

        literal = "[" + ",".join(f"{x:.6f}" for x in vetor.tolist()) + "]"

        log_info("Consultando pgvector...")
        resultados = db_ia.execute(
            text("""
                SELECT id, nome, descricao, preco,
                       (1 - (embedding <#> :emb)) AS score
                FROM produtos_ia
                ORDER BY embedding <#> :emb
                LIMIT :k
            """),
            {"emb": literal, "k": limite}
        ).fetchall()

        log_success(f"{len(resultados)} produtos recomendados.")
        return resultados

    except Exception as e:
        log_error("Erro na recomendação por embedding.")
        print(RED + str(e) + RESET)
        return []


# ================================================================
# 🔹 RECOMENDA CLIENTES PARECIDOS
# ================================================================
def recomendar_clientes_parecidos(db_ia: Session, embedding_vector, limite=5):
    log_info("Buscando clientes semanticamente semelhantes...")

    if embedding_vector is None:
        log_warn("Embedding vazio → ignorando comparação entre clientes.")
        return []

    try:
        vetor = np.array(embedding_vector, dtype=float)
        norma = np.linalg.norm(vetor)

        if norma > 0:
            vetor = vetor / norma

        literal = "[" + ",".join(f"{x:.6f}" for x in vetor.tolist()) + "]"

        resultados = db_ia.execute(
            text("""
                SELECT id, nome,
                       (1 - (embedding <#> :emb)) AS score
                FROM clientes_ia
                ORDER BY embedding <#> :emb
                LIMIT :k
            """),
            {"emb": literal, "k": limite}
        ).fetchall()

        log_success(f"{len(resultados)} clientes semelhantes encontrados.")
        return resultados

    except Exception as e:
        log_error("Erro ao comparar clientes.")
        print(RED + str(e) + RESET)
        return []
