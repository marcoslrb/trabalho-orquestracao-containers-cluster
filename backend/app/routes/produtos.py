from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Produto, Categoria
from app.schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    """Retorna todos os produtos."""
    return db.query(Produto).all()


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Retorna um produto pelo ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post("/", response_model=ProdutoResponse, status_code=201)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto."""
    # Verifica se a categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    """Atualiza um produto existente."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verifica se a nova categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    for campo, valor in dados.model_dump().items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=204)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Deleta um produto pelo ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()
    return None
