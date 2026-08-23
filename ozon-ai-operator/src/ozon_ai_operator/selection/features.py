from __future__ import annotations
from datetime import datetime
import pandas as pd
from sqlalchemy import select
from ..db import SessionLocal, Product, MarketSnapshot

def pct_change(old: float, new: float) -> float:
    if old <= 0: return 1.0 if new > 0 else 0.0
    return (new-old)/old

def market_features(product_id: str) -> dict:
    with SessionLocal() as s:
        p=s.scalar(select(Product).where(Product.product_id==product_id))
        rows=s.scalars(select(MarketSnapshot).where(MarketSnapshot.product_id==product_id).order_by(MarketSnapshot.date)).all()
    if not p or not rows: return {}
    a,b=rows[0],rows[-1]
    age_days=max(0,(datetime.utcnow()-(p.created_at or datetime.utcnow())).days)
    return {
        "sales_growth":pct_change(a.sales,b.sales),
        "search_growth":pct_change(a.search_volume,b.search_volume),
        "cart_growth":pct_change(a.cart_additions,b.cart_additions),
        "seller_growth":pct_change(a.seller_count,b.seller_count),
        "seller_count":b.seller_count,
        "age_days":age_days,
        "median_price":b.median_price,
    }
