# app/modules/assistente/models/model.py

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database_ia import BaseIA


# ============================================================
# 1) ChatMessage  (OK — já existia no banco)
# ============================================================
class ChatMessage(BaseIA):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Text)
    vendedor_id = Column(Integer, index=True)
    sender = Column(Text)  # vendedor | assistente
    message = Column(Text, nullable=False)

    embedding = Column(Vector(1536), index=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# ============================================================
# 2) ClienteIA (tabela clientes_ia — está OK no dump)
# ============================================================
class ClienteIA(BaseIA):
    __tablename__ = "clientes_ia"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(Text, nullable=False)
    email = Column(Text)
    cpf = Column(Text)
    telefone = Column(Text)

    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# ============================================================
# 3) ProdutoIA (tabela produtos_ia — OK)
# ============================================================
class ProdutoIA(BaseIA):
    __tablename__ = "produtos_ia"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(Text, nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric)
    categoria_id = Column(Integer)

    embedding = Column(Vector(1536), index=True)

    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# ============================================================
# 4) InteracaoCliente  (tabela interacoes_clientes — OK)
# ============================================================
class InteracaoCliente(BaseIA):
    __tablename__ = "interacoes_clientes"

    id = Column(Integer, primary_key=True, index=True)
    chat_message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes_ia.id"))
    vendedor_id = Column(Integer)

    tipo = Column(Text)
    detalhe = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# ============================================================
# 5) RecomendacaoRegistrada (tabela recomendacoes_registradas — OK)
# ============================================================
class RecomendacaoRegistrada(BaseIA):
    __tablename__ = "recomendacoes_registradas"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes_ia.id"))
    vendedor_id = Column(Integer)
    produto_id = Column(Integer, ForeignKey("produtos_ia.id"))

    motivo = Column(Text)
    score = Column(Numeric)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# ============================================================
# 6) PreferenciaCliente (🔥 NOVA TABELA ADICIONADA — NÃO EXISTIA)
#     → necessária para agent_sugestivo e service_sugestivo
# ============================================================
class PreferenciaCliente(BaseIA):
    __tablename__ = "preferencias_cliente"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes_ia.id"), nullable=False)
    chave = Column(Text, nullable=False)
    valor = Column(Text)
    fonte = Column(Text, default="ia")   # ia | sistema | vendedor
    peso = Column(Numeric, default=1.0)

    criado_em = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
