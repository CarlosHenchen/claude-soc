"""SOC Maturity — backend leve.

Guarda o estado da aplicação (organizações, ciclos, respostas, roadmap,
entregáveis, usuários) como um documento JSON no PostgreSQL. O frontend lê/grava
via GET/PUT /api/state; usa localStorage só como cache/fallback.

A chave do Claude NÃO passa por aqui (fica no navegador, por opção do usuário).
"""
from __future__ import annotations

import os
import time

import psycopg
from psycopg.types.json import Json
from fastapi import FastAPI, Request

DB_URL = os.environ.get("DATABASE_URL", "postgresql://soc:soc@db:5432/soc")

app = FastAPI(title="SOC Maturity API")


def connect():
    # Conexão por requisição (tráfego baixo, ferramenta interna). autocommit
    # evita a necessidade de COMMIT explícito.
    return psycopg.connect(DB_URL, autocommit=True, connect_timeout=5)


def init_db(retries: int = 30) -> None:
    """Cria a tabela, aguardando o Postgres ficar pronto (boot do compose)."""
    last_err = None
    for _ in range(retries):
        try:
            with connect() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS app_state ("
                    "  id INT PRIMARY KEY,"
                    "  data JSONB NOT NULL,"
                    "  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                    ")"
                )
            return
        except Exception as e:  # Postgres ainda subindo
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"banco indisponível após várias tentativas: {last_err}")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/state")
def get_state():
    """Retorna o documento de estado salvo, ou null se ainda não houver."""
    with connect() as conn:
        row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
    return row[0] if row else None


@app.put("/api/state")
async def put_state(req: Request):
    """Salva (upsert) o documento de estado inteiro."""
    data = await req.json()
    with connect() as conn:
        conn.execute(
            "INSERT INTO app_state (id, data, updated_at) VALUES (1, %s, now()) "
            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data, updated_at = now()",
            (Json(data),),
        )
    return {"ok": True}
