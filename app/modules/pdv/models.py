from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database_pdv import BasePDV


# =========================
# TABELA: endereco
# =========================
class Endereco(BasePDV):
    __tablename__ = "endereco"

    id = Column(Integer, primary_key=True, index=True)
    bairro = Column(String(80))
    cep = Column(String(9))
    cidade = Column(String(80))
    logradouro = Column(String(120))
    uf = Column(String(2))

    clientes = relationship("Cliente", back_populates="endereco")
    usuarios = relationship("Usuario", back_populates="endereco")


# =========================
# TABELA: cliente
# =========================
class Cliente(BasePDV):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    complemento = Column(String(60))
    cpf = Column(String(11))
    email = Column(String(100))
    nome = Column(String(100))
    numero = Column(String(10))
    telefone = Column(String(11))

    endereco_id = Column(Integer, ForeignKey("endereco.id"))
    endereco = relationship("Endereco", back_populates="clientes")

    pedidos = relationship("Pedido", back_populates="cliente")


# =========================
# TABELA: usuario
# =========================
class Usuario(BasePDV):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    complemento = Column(String(100))
    email = Column(String(100))
    nome = Column(String(80))
    numero = Column(String(10))
    perfil = Column(String(20))
    senha = Column(String(255))

    endereco_id = Column(Integer, ForeignKey("endereco.id"))
    endereco = relationship("Endereco", back_populates="usuarios")


# =========================
# TABELA: categoria
# =========================
class Categoria(BasePDV):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255))
    nome = Column(String(100))

    produtos = relationship("Produto", back_populates="categoria")


# =========================
# TABELA: produto
# =========================
class Produto(BasePDV):
    __tablename__ = "produto"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(500))
    nome = Column(String(100))
    preco = Column(Numeric(10, 2))
    quantidade_estoque = Column(Integer)
    categoria_id = Column(Integer, ForeignKey("categoria.id"))
    foto = Column(String(255))

    categoria = relationship("Categoria", back_populates="produtos")
    itens = relationship("ItensPedido", back_populates="produto")


# =========================
# TABELA: pedido
# =========================
class Pedido(BasePDV):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    data_pedido = Column(DateTime)
    status = Column(String(255))
    id_cliente = Column(Integer, ForeignKey("cliente.id"))

    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("ItensPedido", back_populates="pedido")


# =========================
# TABELA: itens_pedido
# =========================
class ItensPedido(BasePDV):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    desconto = Column(Numeric(10, 2))
    quantidade = Column(Integer)
    valor_venda = Column(Numeric(10, 2))

    id_pedido = Column(Integer, ForeignKey("pedido.id"))
    id_produto = Column(Integer, ForeignKey("produto.id"))

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens")
