from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)

    produtos = relationship("Produto", back_populates="categoria", cascade="all, delete-orphan")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    categoria = relationship("Categoria", back_populates="produtos")
