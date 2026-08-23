from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import select, func
from ..db import SessionLocal, StoreMetric, Lifecycle, Product
from ..config import load_yaml

def rates(m):
    imp=sum(x.impressions for x in m); clicks=sum(x.clicks for x in m); carts=sum(x.cart_additions for x in m); orders=sum(x.orders for x in m); returns=sum(x.returns for x in m)
    return {"impressions":imp,"clicks":clicks,"carts":carts,"orders":orders,"returns":returns,
            "ctr":clicks/imp if imp else 0,"cart_rate":carts/clicks if clicks else 0,"cvr":orders/clicks if clicks else 0,"return_rate":returns/orders if orders else 0}

def store_benchmarks(days=30):
    since=datetime.utcnow()-timedelta(days=days)
    with SessionLocal() as s: rows=s.scalars(select(StoreMetric).where(StoreMetric.date>=since)).all()
    return rates(rows)

def evaluate_offer(offer_id:str, days=7, profit_margin=.30, selection_score=75) -> dict:
    cfg=load_yaml("strategy.yaml"); since=datetime.utcnow()-timedelta(days=days)
    with SessionLocal() as s: rows=s.scalars(select(StoreMetric).where(StoreMetric.offer_id==offer_id,StoreMetric.date>=since)).all()
    r=rates(rows); b=store_benchmarks(30); lc=cfg["lifecycle"]; status="WATCH"; reason="collect_more_data"
    if days>=15 and r["orders"]>=cfg["scale"]["min_orders_15d"] and profit_margin>=cfg["scale"]["min_margin"] and r["return_rate"]<=cfg["scale"]["max_return_rate"] and selection_score>=cfg["scale"]["min_score"]:
        status,reason="SCALE","orders_margin_returns_pass"
    elif days>=7 and r["impressions"]<lc["low_visibility_impressions_7d"]:
        status,reason="LOW_VISIBILITY","insufficient_impressions"
    elif b["ctr"] and r["ctr"]<b["ctr"]*lc["low_ctr_multiplier"]:
        status,reason="REPRICE_OR_CREATIVE","low_ctr"
    elif b["cart_rate"] and r["cart_rate"]<b["cart_rate"]*lc["low_cart_multiplier"]:
        status,reason="PRODUCT_INTENT_WEAK","low_cart_rate"
    elif b["cvr"] and r["cvr"]<b["cvr"]*lc["low_cvr_multiplier"]:
        status,reason="PRICE_OR_DELIVERY","low_conversion"
    elif days>=30 and r["orders"]==0:
        status,reason="ELIMINATE","no_orders_30d"
    elif r["orders"]>0:
        status,reason="POTENTIAL","has_orders"
    return {"offer_id":offer_id,"days":days,"status":status,"reason":reason,"metrics":r,"benchmark":b}
