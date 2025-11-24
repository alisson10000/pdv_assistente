# app/modules/assistente/kernel/recomendador_hibrido.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import traceback

# IMPORTAÇÃO CORRETA
from app.core.database_pdv import SessionPDV


# ==================================================================
# ANSI
# ==================================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"


def log_info(msg):    print(f"{BLUE}[RECOM-HIBRIDO][INFO]{RESET} {msg}")
def log_warn(msg):    print(f"{YELLOW}[RECOM-HIBRIDO][WARN]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[RECOM-HIBRIDO][OK]{RESET} {msg}")
def log_error(msg):   print(f"{RED}[RECOM-HIBRIDO][ERRO]{RESET} {msg}")


# ==================================================================
# WRAPPER OFICIAL
# ==================================================================
def recomendar_produtos_para_cliente(db_ia: Session, cliente_id: int | None, limite: int = 5):
    return recomendar_produtos_hibrido(db_ia, cliente_id, limite)


# ==================================================================
# FUNÇÃO PRINCIPAL
# ==================================================================
def recomendar_produtos_hibrido(db_ia: Session, cliente_id: int | None, limite: int = 5):

    print("\n" + PURPLE + "============================================================")
    print("🔮 [RECOM-HIBRIDO] Iniciando recomendação híbrida")
    print("============================================================" + RESET)

    # 🟢 CORREÇÃO 1: Usar 'with' para garantir o fechamento da sessão PDV (Resource Leaks)
    try:
        with SessionPDV() as db_pdv:
            log_success("Conexão com PDV aberta.")

            # ===============================================================
            # 1) Cliente não identificado
            # ===============================================================
            if not cliente_id:
                log_warn("Cliente não informado → fallback genérico.")
                return recomendar_populares(db_pdv, limite)

            # ===============================================================
            # 2) Histórico do PDV
            # ===============================================================
            log_info("Buscando compras do cliente no PDV...")

            try:
                compras = db_pdv.execute(text("""
                    SELECT ip.id_produto
                    FROM itens_pedido ip
                    JOIN pedido p ON p.id = ip.id_pedido
                    WHERE p.id_cliente = :id
                """), {"id": cliente_id}).fetchall()

                produtos_comprados = [row[0] for row in compras]

            except Exception:
                log_error("Erro ao buscar compras.")
                print(RED + traceback.format_exc() + RESET)
                return recomendar_populares(db_pdv, limite)

            if not produtos_comprados:
                log_warn("Nenhuma compra encontrada → populares.")
                return recomendar_populares(db_pdv, limite)

            log_success(f"{len(produtos_comprados)} produtos comprados encontrados.")

            # ===============================================================
            # 3) Embeddings do IA
            # ===============================================================
            log_info("Buscando embeddings no IA...")

            try:
                produtos_emb = db_ia.execute(text("""
                    SELECT id, embedding
                    FROM produtos_ia
                    WHERE id = ANY(:lista)
                """), {"lista": produtos_comprados}).fetchall()

            except Exception:
                log_error("Erro ao buscar embeddings.")
                print(RED + traceback.format_exc() + RESET)
                return recomendar_populares(db_pdv, limite)

            if not produtos_emb:
                log_warn("Nenhum embedding → fallback.")
                return recomendar_populares(db_pdv, limite)

            # ===============================================================
            # 4) Embedding médio
            # ===============================================================
            try:
                vetor_medio = np.mean([np.array(p.embedding) for p in produtos_emb], axis=0)
                norma = np.linalg.norm(vetor_medio)
                if norma:
                    vetor_medio = vetor_medio / norma

                vetor_literal = "[" + ",".join(f"{x:.6f}" for x in vetor_medio.tolist()) + "]"
                log_success("Embedding médio calculado.")

            except Exception:
                log_error("Erro no cálculo do embedding médio.")
                print(RED + traceback.format_exc() + RESET)
                return recomendar_populares(db_pdv, limite)

            # ===============================================================
            # 5) Similaridade
            # ===============================================================
            log_info("Consultando similaridade via pgvector...")

            try:
                similares = db_ia.execute(text("""
                    SELECT id, nome, descricao, preco,
                           (1 - (embedding <#> :emb)) AS score,
                           'similaridade_embeddings' AS motivo -- Adiciona o motivo para consistência
                    FROM produtos_ia
                    WHERE id != ALL(:comprados)  -- 🟢 CORREÇÃO 2: Uso de != ALL() para listas (SQL NOT IN fix)
                    ORDER BY embedding <#> :emb
                    LIMIT :limite
                """), {
                    "emb": vetor_literal,
                    "comprados": produtos_comprados, # Passa a lista diretamente (sem tuple())
                    "limite": limite
                }).fetchall()

            except Exception:
                log_error("Erro ao buscar similares.")
                print(RED + traceback.format_exc() + RESET)
                similares = []

            if similares:
                log_success(f"{len(similares)} produtos semelhantes retornados.")
                return similares

            # ===============================================================
            # 6) Fallback
            # ===============================================================
            log_warn("Nenhum similar → populares.")
            return recomendar_populares(db_pdv, limite)

    except Exception:
        # Erro na abertura da sessão (SessionPDV()) ou erro crítico no fluxo principal
        log_error("Falha na abertura da conexão ou erro crítico na recomendação híbrida.")
        print(RED + traceback.format_exc() + RESET)
        return []


# ==================================================================
# FALLBACK
# ==================================================================
def recomendar_populares(db_pdv: Session, limite=5):

    log_info("Consultando produtos populares...")

    try:
        registros = db_pdv.execute(text("""
            SELECT p.id, p.nome, p.descricao, p.preco,
                   SUM(ip.quantidade) AS score,         -- 🟢 CORREÇÃO 3.1: Alias 'total' para 'score'
                   'popularidade' AS motivo             -- 🟢 CORREÇÃO 3.2: Adiciona o motivo
            FROM produto p
            JOIN itens_pedido ip ON ip.id_produto = p.id
            GROUP BY p.id
            ORDER BY score DESC                         -- Ordena por 'score' (antigo 'total')
            LIMIT :limite
        """), {"limite": limite}).fetchall()

        log_success(f"{len(registros)} itens populares retornados.")
        return registros

    except Exception:
        log_error("Erro ao consultar populares.")
        print(RED + traceback.format_exc() + RESET)
        return []