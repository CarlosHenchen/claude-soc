"""Small CLI used by the container entrypoint (seed / re-seed)."""
from __future__ import annotations

import sys

from .database import SessionLocal
from .ingest import run_seed


def seed() -> None:
    db = SessionLocal()
    try:
        summary = run_seed(db)
        print(f"[seed] {summary}", flush=True)
    finally:
        db.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if cmd == "seed":
        seed()
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
