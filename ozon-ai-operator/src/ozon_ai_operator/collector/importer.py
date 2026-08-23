from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import select
from ..db import SessionLocal, Product, MarketSnapshot, StoreMetric, init_db

PRODUCT_COLS = {"product_id","name","category"}
MARKET_COLS = {"date","product_id","sales","search_volume","cart_additions","seller_count","lowest_price","median_price"}
STORE_COLS = {"date","offer_id","impressions","clicks","cart_additions","orders","revenue","returns","price","stock"}

def _read(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    return pd.read_excel(path) if path.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(path)

def import_products(path: str | Path) -> int:
    init_db(); df = _read(path)
    if not PRODUCT_COLS.issubset(df.columns): raise ValueError(f"Need columns {sorted(PRODUCT_COLS)}")
    n=0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            obj = s.scalar(select(Product).where(Product.product_id == str(r["product_id"])))
            if not obj:
                obj = Product(product_id=str(r["product_id"]), name=str(r["name"]), category=str(r["category"]))
                s.add(obj); n+=1
            for k in ["offer_id","subcategory","brand","created_at","listed_at","sku_count","requires_certification","restricted_category","dangerous_goods","brand_risk_high","fragile","battery","return_risk_high","compatibility_complex"]:
                if k in r and pd.notna(r[k]):
                    v=r[k]
                    if k in {"created_at","listed_at"}: v=pd.to_datetime(v).to_pydatetime()
                    setattr(obj,k,v)
        s.commit()
    return n

def import_market(path: str | Path) -> int:
    init_db(); df = _read(path)
    if not MARKET_COLS.issubset(df.columns): raise ValueError(f"Need columns {sorted(MARKET_COLS)}")
    n=0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            dt=pd.to_datetime(r["date"]).to_pydatetime()
            obj=s.scalar(select(MarketSnapshot).where(MarketSnapshot.date==dt,MarketSnapshot.product_id==str(r["product_id"])))
            if not obj:
                obj=MarketSnapshot(date=dt,product_id=str(r["product_id"])); s.add(obj); n+=1
            for k in MARKET_COLS-{"date","product_id"}: setattr(obj,k,float(r.get(k,0) or 0))
        s.commit()
    return n

def import_store(path: str | Path) -> int:
    init_db(); df = _read(path)
    if not STORE_COLS.issubset(df.columns): raise ValueError(f"Need columns {sorted(STORE_COLS)}")
    n=0
    with SessionLocal() as s:
        for r in df.to_dict("records"):
            dt=pd.to_datetime(r["date"]).to_pydatetime()
            obj=s.scalar(select(StoreMetric).where(StoreMetric.date==dt,StoreMetric.offer_id==str(r["offer_id"])))
            if not obj:
                obj=StoreMetric(date=dt,offer_id=str(r["offer_id"])); s.add(obj); n+=1
            for k in STORE_COLS-{"date","offer_id"}: setattr(obj,k,float(r.get(k,0) or 0))
        s.commit()
    return n
