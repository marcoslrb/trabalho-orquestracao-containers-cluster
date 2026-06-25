"""
main.py – Ponto de entrada da aplicação FastAPI.

Integra:
- Rotas de Categorias e Produtos (CRUD).
- Logger que envia logs ao Grafana Loki via HTTP.
- Middleware para registrar cada requisição (método, rota, status, tempo).
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import Categoria, Produto  # noqa: F401 – necessário para create_all
from app.logger import log_startup, log_request, log_db_error
from app.routes.categorias import router as categorias_router
from app.routes.produtos import router as produtos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Evento de startup/shutdown da aplicação."""
    # ── Startup ──
    try:
        Base.metadata.create_all(bind=engine)
        print("[STARTUP] Tabelas criadas/verificadas no PostgreSQL.")
    except Exception as e:
        print(f"[STARTUP] Erro ao conectar no PostgreSQL: {e}")
        await log_db_error(str(e))

    await log_startup()
    print("[STARTUP] Aplicação FastAPI iniciada.")

    yield

    # ── Shutdown ──
    print("[SHUTDOWN] Aplicação FastAPI encerrada.")


app = FastAPI(
    title="Catálogo de Produtos e Categorias",
    description="API REST para gerenciamento de produtos e categorias – Grupo 2, Tema 2",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware de logging ──
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Registra cada requisição no Loki."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    await log_request(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response


# ── Rotas ──
app.include_router(categorias_router, prefix="/api")
app.include_router(produtos_router, prefix="/api")


@app.get("/api/health")
def health_check():
    """Endpoint de health check."""
    return {"status": "ok", "service": "catalogo-backend"}
