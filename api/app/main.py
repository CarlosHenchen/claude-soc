"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import admin, assessments, auth, frameworks, users

app = FastAPI(
    title="Viaconnect SOC Maturity",
    description="Avaliação de maturidade de SOC — instrumento Viaconnect Health Check.",
    version="1.0.0",
)

# Internal tool behind the same Nginx origin; CORS kept permissive for dev access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(frameworks.router)
app.include_router(assessments.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
