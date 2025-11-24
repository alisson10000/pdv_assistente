from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ==========================================================
#  🚧  ENDERECO
# ==========================================================

class EnderecoBase(BaseModel):
    bairro: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    logradouro: Optional[str] = None
    uf: Optional[str] = None


class EnderecoResponse(EnderecoBase):
    id: int

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  CLIENTE
# ==========================================================

class ClienteBase(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None


class ClienteResponse(ClienteBase):
    id: int
    endereco: Optional[EnderecoResponse]

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  USUÁRIO (NÃO EXIBIMOS SENHA por segurança)
# ==========================================================

class UsuarioBase(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    perfil: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    endereco: Optional[EnderecoResponse]

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  CATEGORIA
# ==========================================================

class CategoriaBase(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  PRODUTO
# ==========================================================

class ProdutoBase(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    quantidade_estoque: Optional[int] = None
    foto: Optional[str] = None


class ProdutoResponse(ProdutoBase):
    id: int
    categoria: Optional[CategoriaResponse]

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  ITENS PEDIDO
# ==========================================================

class ItensPedidoBase(BaseModel):
    quantidade: int
    desconto: Optional[float]
    valor_venda: float


class ItensPedidoResponse(ItensPedidoBase):
    id: int
    produto: Optional[ProdutoResponse]

    class Config:
        orm_mode = True


# ==========================================================
#  🚧  PEDIDO
# ==========================================================

class PedidoBase(BaseModel):
    status: Optional[str] = None
    data_pedido: Optional[datetime] = None


class PedidoResponse(PedidoBase):
    id: int
    cliente: Optional[ClienteResponse]
    itens: List[ItensPedidoResponse] = []

    class Config:
        orm_mode = True
