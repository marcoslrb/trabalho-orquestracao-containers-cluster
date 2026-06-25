from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Retorna todas as categorias."""
    return db.query(Categoria).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Retorna uma categoria pelo ID."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.post("/", response_model=CategoriaResponse, status_code=201)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    """Cria uma nova categoria."""
    # Verifica duplicidade
    existente = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
    if existente:
        raise HTTPException(status_code=400, detail="Categoria com esse nome já existe")

    categoria = Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(categoria_id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma categoria existente."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    for campo, valor in dados.model_dump().items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=204)
def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Deleta uma categoria pelo ID."""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(categoria)
    db.commit()
    return None
