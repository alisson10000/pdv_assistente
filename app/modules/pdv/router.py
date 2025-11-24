from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database_pdv import get_db_pdv
from app.modules.pdv import service
from app.modules.pdv.schemas import (
    ClienteResponse, ProdutoResponse, CategoriaResponse,
    PedidoResponse, ItensPedidoResponse
)

router = APIRouter(prefix="/pdv", tags=["PDV - Sistema Varejo"])


# ============================================================
#   🧍 CLIENTES
# ============================================================
@router.get("/clientes", response_model=list[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db_pdv)):
    return service.listar_clientes(db)


@router.get("/clientes/{cliente_id}", response_model=ClienteResponse | None)
def get_cliente(cliente_id: int, db: Session = Depends(get_db_pdv)):
    return service.get_cliente(db, cliente_id)


# ============================================================
#   📦 PRODUTOS
# ============================================================
@router.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db_pdv)):
    return service.listar_produtos(db)


@router.get("/produtos/{produto_id}", response_model=ProdutoResponse | None)
def get_produto(produto_id: int, db: Session = Depends(get_db_pdv)):
    return service.get_produto(db, produto_id)


@router.get("/produtos/buscar/{nome}", response_model=list[ProdutoResponse])
def buscar_produtos(nome: str, db: Session = Depends(get_db_pdv)):
    return service.buscar_produtos_por_nome(db, nome)


# ============================================================
#   🏷️ CATEGORIAS
# ============================================================
@router.get("/categorias", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db_pdv)):
    return service.listar_categorias(db)


# ============================================================
#   🧾 PEDIDOS
# ============================================================
@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse | None)
def get_pedido(pedido_id: int, db: Session = Depends(get_db_pdv)):
    return service.get_pedido(db, pedido_id)


@router.get("/clientes/{cliente_id}/pedidos", response_model=list[PedidoResponse])
def listar_pedidos_cliente(cliente_id: int, db: Session = Depends(get_db_pdv)):
    return service.listar_pedidos_cliente(db, cliente_id)


@router.get("/pedidos/dia", response_model=list[PedidoResponse])
def listar_pedidos_dia(db: Session = Depends(get_db_pdv)):
    return service.listar_pedidos_dia(db)


# ============================================================
#   🛒 ITENS DO PEDIDO
# ============================================================
@router.get("/pedidos/{pedido_id}/itens", response_model=list[ItensPedidoResponse])
def listar_itens_pedido(pedido_id: int, db: Session = Depends(get_db_pdv)):
    return service.listar_itens_pedido(db, pedido_id)


# ============================================================
#   📊 RELATÓRIOS (para o Assistente Inteligente)
# ============================================================
@router.get("/relatorios/vendas-hoje")
def total_vendas_hoje(db: Session = Depends(get_db_pdv)):
    return {"total_vendas_hoje": float(service.total_vendas_hoje(db))}


@router.get("/relatorios/produto-mais-vendido")
def produto_mais_vendido(db: Session = Depends(get_db_pdv)):
    dado = service.produto_mais_vendido(db)
    if not dado:
        return {"produto": None}
    return {"produto": dado[0], "quantidade": int(dado[1])}
