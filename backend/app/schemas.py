from pydantic import BaseModel
from typing import Optional


# ── Categoria ──────────────────────────────────────────────

class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(CategoriaBase):
    pass


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


# ── Produto ────────────────────────────────────────────────

class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    quantidade: int = 0
    categoria_id: int


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(ProdutoBase):
    pass


class ProdutoResponse(ProdutoBase):
    id: int

    class Config:
        from_attributes = True
