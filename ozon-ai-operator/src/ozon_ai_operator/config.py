from __future__ import annotations
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

def load_yaml(name: str) -> dict:
    with open(ROOT / "config" / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def database_url() -> str:
    return os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'ozon_ai_operator.db'}")
