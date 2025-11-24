from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI
import datetime

client = OpenAI()


# ======================================================
# 🟩 GERAÇÃO DE EMBEDDING
# ======================================================
def gerar_embedding(texto: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding


# ======================================================
# 🟦 SYNC CLIENTES
# ======================================================
def sync_clientes(pdv_db: Session, ia_db: Session):
    print("🔵 [SYNC] Carregando clientes do PDV...")

    clientes = pdv_db.execute(text(
        "SELECT id, nome, email, cpf, telefone FROM cliente"
    )).fetchall()

    total = 0

    for c in clientes:
        existe = ia_db.execute(text(
            "SELECT id FROM clientes_ia WHERE id = :id"
        ), {"id": c.id}).fetchone()

        if existe:
            ia_db.execute(text("""
                UPDATE clientes_ia
                SET nome=:nome, email=:email, cpf=:cpf, telefone=:telefone, atualizado_em=NOW()
                WHERE id=:id
            """), {
                "id": c.id,
                "nome": c.nome,
                "email": c.email,
                "cpf": c.cpf,
                "telefone": c.telefone
            })

        else:
            ia_db.execute(text("""
                INSERT INTO clientes_ia (id, nome, email, cpf, telefone)
                VALUES (:id, :nome, :email, :cpf, :telefone)
            """), {
                "id": c.id,
                "nome": c.nome,
                "email": c.email,
                "cpf": c.cpf,
                "telefone": c.telefone
            })

        total += 1

    ia_db.commit()
    return total


# ======================================================
# 🟦 SYNC PRODUTOS
# ======================================================
def sync_produtos(pdv_db: Session, ia_db: Session):
    print("🔵 [SYNC] Carregando produtos do PDV...")

    produtos = pdv_db.execute(text("""
        SELECT id, nome, descricao, preco, categoria_id
        FROM produto
    """)).fetchall()

    total = 0

    for p in produtos:
        texto = f"{p.nome}. {p.descricao}"
        embedding = gerar_embedding(texto)

        existe = ia_db.execute(text(
            "SELECT id FROM produtos_ia WHERE id=:id"
        ), {"id": p.id}).fetchone()

        if existe:
            ia_db.execute(text("""
                UPDATE produtos_ia
                SET nome=:nome, descricao=:descricao, preco=:preco, 
                    categoria_id=:categoria_id, embedding=:embedding,
                    atualizado_em=NOW()
                WHERE id=:id
            """), {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "preco": p.preco,
                "categoria_id": p.categoria_id,
                "embedding": embedding
            })

        else:
            ia_db.execute(text("""
                INSERT INTO produtos_ia (id, nome, descricao, preco, categoria_id, embedding)
                VALUES (:id, :nome, :descricao, :preco, :categoria_id, :embedding)
            """), {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "preco": p.preco,
                "categoria_id": p.categoria_id,
                "embedding": embedding
            })

        total += 1

    ia_db.commit()
    return total


# ======================================================
# 🟩 FUNÇÃO PRINCIPAL —
# ======================================================
def sincronizar_pdv_ia(pdv_db: Session, ia_db: Session):
    print("\n===========================================")
    print("🔵 INICIANDO SINCRONIZAÇÃO COMPLETA PDV → IA")
    print("===========================================\n")

    total_clientes = sync_clientes(pdv_db, ia_db)
    total_produtos = sync_produtos(pdv_db, ia_db)

    msg = f"{total_clientes} clientes e {total_produtos} produtos sincronizados."
    print("🟢", msg)

    return msg
