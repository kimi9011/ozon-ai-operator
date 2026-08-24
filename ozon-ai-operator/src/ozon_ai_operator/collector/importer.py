from __future__ import annotations
from pathlib import Path
import pandas as pd
from sqlalchemy import select
from ..db import SessionLocal, Product, MarketSnapshot, StoreMetric, Store, DEFAULT_STORE_ID, init_db

PRODUCT_COLS = {"product_id", "name", "category"}
MARKET_COLS = {"date", "product_id", "sales", "search_volume", "cart_additions", "seller_count", "lowest_price", "median_price"}
STORE_COLS = {"date", "offer_id", "impressions", "clicks", "cart_additions", "orders", "revenue", "returns", "price", "stock"}


def _read(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    return pd.read_excel(path) if path.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(path)


def _store_id(value: object) -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return DEFAULT_STORE_ID
    return str(value).strip()


def _ensure_store(session, store_id: str) -> None:
    obj = session.scalar(select(Store).where(Store.store_id == store_id))
    if not obj:
        session.add(Store(store_id=store_id, name=store_id))


def import_products(path: str | Path) -> int:
    init_db()
    df = _read(path)
    if not PRODUCT_COLS.issubset(df.columns):
        raise ValueError(f"Need columns {sorted(PRODUCT_COLS)}")
    n = 0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            obj = s.scalar(select(Product).where(Product.product_id == str(r["product_id"])))
            if not obj:
                obj = Product(product_id=str(r["product_id"]), name=str(r["name"]), category=str(r["category"]))
                s.add(obj)
                n += 1
            for k in [
                "offer_id", "subcategory", "brand", "created_at", "listed_at", "sku_count",
                "requires_certification", "restricted_category", "dangerous_goods", "brand_risk_high",
                "fragile", "battery", "return_risk_high", "compatibility_complex",
            ]:
                if k in r and pd.notna(r[k]):
                    v = r[k]
                    if k in {"created_at", "listed_at"}:
                        v = pd.to_datetime(v).to_pydatetime()
                    setattr(obj, k, v)
        s.commit()
    return n


def import_market(path: str | Path) -> int:
    init_db()
    df = _read(path)
    if not MARKET_COLS.issubset(df.columns):
        raise ValueError(f"Need columns {sorted(MARKET_COLS)}")
    n = 0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            dt = pd.to_datetime(r["date"]).to_pydatetime()
            obj = s.scalar(
                select(MarketSnapshot).where(
                    MarketSnapshot.date == dt,
                    MarketSnapshot.product_id == str(r["product_id"]),
                )
            )
            if not obj:
                obj = MarketSnapshot(date=dt, product_id=str(r["product_id"]))
                s.add(obj)
                n += 1
            for k in MARKET_COLS - {"date", "product_id"}:
                setattr(obj, k, float(r.get(k, 0) or 0))
        s.commit()
    return n


def import_store(path: str | Path, default_store_id: str = DEFAULT_STORE_ID) -> int:
    """Import seller-side daily metrics.

    `store_id` is optional for backwards compatibility. If missing/blank,
    `default_store_id` is used. This allows old exports to keep working while
    safely isolating metrics from multiple Ozon shops.
    """

    init_db()
    df = _read(path)
    if not STORE_COLS.issubset(df.columns):
        raise ValueError(f"Need columns {sorted(STORE_COLS)}")
    n = 0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            dt = pd.to_datetime(r["date"]).to_pydatetime()
            sid = _store_id(r.get("store_id")) if "store_id" in df.columns else _store_id(default_store_id)
            _ensure_store(s, sid)
            obj = s.scalar(
                select(StoreMetric).where(
                    StoreMetric.date == dt,
                    StoreMetric.store_id == sid,
                    StoreMetric.offer_id == str(r["offer_id"]),
                )
            )
            if not obj:
                obj = StoreMetric(date=dt, store_id=sid, offer_id=str(r["offer_id"]))
                s.add(obj)
                n += 1
            for k in STORE_COLS - {"date", "offer_id"}:
                setattr(obj, k, float(r.get(k, 0) or 0))
        s.commit()
    return n
