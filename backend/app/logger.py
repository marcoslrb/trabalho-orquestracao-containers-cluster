"""
logger.py – Módulo de envio de logs estruturados ao Grafana Loki via HTTP API.

Envia logs via POST /loki/api/v1/push usando httpx (async).
Cada log inclui labels (job, level, source) e timestamp em nanossegundos.
"""

import os
import time
import json
import httpx

LOKI_URL = os.getenv("LOKI_URL", "http://loki-service:3100")
LOKI_PUSH_ENDPOINT = f"{LOKI_URL}/loki/api/v1/push"

# Labels padrão para identificar a fonte dos logs
DEFAULT_LABELS = {
    "job": "catalogo-backend",
    "source": "fastapi",
}


def _timestamp_ns() -> str:
    """Retorna o timestamp atual em nanossegundos (string)."""
    return str(int(time.time() * 1e9))


async def send_log(message: str, level: str = "info", extra_labels: dict | None = None):
    """
    Envia um log ao Loki via HTTP POST (assíncrono).

    Args:
        message: Texto do log.
        level: Nível do log (info, warning, error).
        extra_labels: Labels adicionais opcionais.
    """
    labels = {**DEFAULT_LABELS, "level": level}
    if extra_labels:
        labels.update(extra_labels)

    payload = {
        "streams": [
            {
                "stream": labels,
                "values": [
                    [_timestamp_ns(), message]
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                LOKI_PUSH_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code not in (200, 204):
                print(f"[LOGGER] Loki retornou status {response.status_code}: {response.text}")
    except Exception as e:
        # Não quebra a aplicação se Loki estiver fora do ar
        print(f"[LOGGER] Erro ao enviar log para Loki: {e}")


async def log_startup():
    """Registra log de inicialização da aplicação."""
    await send_log(
        message="Aplicação FastAPI iniciada com sucesso.",
        level="info",
        extra_labels={"event": "startup"},
    )


async def log_request(method: str, path: str, status_code: int, duration_ms: float):
    """
    Registra log de cada requisição HTTP.

    Args:
        method: Método HTTP (GET, POST, PUT, DELETE).
        path: Rota acessada.
        status_code: Código de status da resposta.
        duration_ms: Tempo de processamento em milissegundos.
    """
    level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
    message = json.dumps({
        "method": method,
        "path": path,
        "status": status_code,
        "duration_ms": round(duration_ms, 2),
    })
    await send_log(
        message=message,
        level=level,
        extra_labels={"event": "request"},
    )


async def log_error(message: str):
    """Registra log de erro (ex.: falha de conexão com PostgreSQL)."""
    await send_log(
        message=message,
        level="error",
        extra_labels={"event": "error"},
    )


async def log_db_error(error: str):
    """Registra log específico de erro de conexão com PostgreSQL."""
    await send_log(
        message=f"Erro de conexão com PostgreSQL: {error}",
        level="error",
        extra_labels={"event": "db_error"},
    )
