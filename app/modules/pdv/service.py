from sqlalchemy.orm import Session
from sqlalchemy import func

from app.modules.pdv.models import (
    Cliente, Usuario, Endereco, Categoria, Produto,
    Pedido, ItensPedido
)

from app.modules.pdv.schemas import (
    ClienteResponse, UsuarioResponse, EnderecoResponse,
    CategoriaResponse, ProdutoResponse,
    PedidoResponse, ItensPedidoResponse
)


# ============================================================
#  🧍 CLIENTE
# ============================================================
def get_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    return ClienteResponse.from_orm(cliente) if cliente else None


def listar_clientes(db: Session):
    clientes = db.query(Cliente).all()
    return [ClienteResponse.from_orm(c) for c in clientes]


# ============================================================
#  👤 USUÁRIO
# ============================================================
def get_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    return UsuarioResponse.from_orm(usuario) if usuario else None


# ============================================================
#  🏠 ENDEREÇO
# ============================================================
def get_endereco(db: Session, endereco_id: int):
    endereco = db.query(Endereco).filter(Endereco.id == endereco_id).first()
    return EnderecoResponse.from_orm(endereco) if endereco else None


# ============================================================
#  📦 PRODUTO
# ============================================================
def get_produto(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    return ProdutoResponse.from_orm(produto) if produto else None


def listar_produtos(db: Session):
    produtos = db.query(Produto).all()
    return [ProdutoResponse.from_orm(p) for p in produtos]


def buscar_produtos_por_nome(db: Session, nome: str):
    produtos = (
        db.query(Produto)
        .filter(Produto.nome.ilike(f"%{nome}%"))
        .all()
    )
    return [ProdutoResponse.from_orm(p) for p in produtos]


# ============================================================
#  🏷️ CATEGORIA
# ============================================================
def listar_categorias(db: Session):
    categorias = db.query(Categoria).all()
    return [CategoriaResponse.from_orm(c) for c in categorias]


# ============================================================
#  🧾 PEDIDO
# ============================================================
def get_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    return PedidoResponse.from_orm(pedido) if pedido else None


def listar_pedidos_cliente(db: Session, cliente_id: int):
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.id_cliente == cliente_id)
        .all()
    )
    return [PedidoResponse.from_orm(p) for p in pedidos]


def listar_pedidos_dia(db: Session):
    """
    Retorna vendas do dia usando a coluna data_pedido.
    """
    pedidos = (
        db.query(Pedido)
        .filter(func.DATE(Pedido.data_pedido) == func.CURRENT_DATE())
        .all()
    )
    return [PedidoResponse.from_orm(p) for p in pedidos]


# ============================================================
#  🛒 ITENS DO PEDIDO
# ============================================================
def listar_itens_pedido(db: Session, pedido_id: int):
    itens = (
        db.query(ItensPedido)
        .filter(ItensPedido.id_pedido == pedido_id)
        .all()
    )
    return [ItensPedidoResponse.from_orm(i) for i in itens]


# ============================================================
#  💰 RELATÓRIOS (para o Assistente Inteligente)
# ============================================================

def total_vendas_hoje(db: Session):
    """
    Soma total das vendas do dia.
    """
    total = (
        db.query(
            func.sum(ItensPedido.valor_venda * ItensPedido.quantidade)
        )
        .join(Pedido, Pedido.id == ItensPedido.id_pedido)
        .filter(func.DATE(Pedido.data_pedido) == func.CURRENT_DATE())
        .scalar()
    )
    return total or 0


def produto_mais_vendido(db: Session):
    """
    Retorna o produto com maior quantidade vendida.
    """
    result = (
        db.query(
            Produto.nome,
            func.sum(ItensPedido.quantidade).label("total_vendido")
        )
        .join(ItensPedido, Produto.id == ItensPedido.id_produto)
        .group_by(Produto.nome)
        .order_by(func.sum(ItensPedido.quantidade).desc())
        .first()
    )
    return result
