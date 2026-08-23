from __future__ import annotations
from sqlalchemy import select
from ..db import SessionLocal, Product, Candidate
from ..config import load_yaml
from ..risk.filter import assess
from .features import market_features

def clamp(x,a=0,b=1): return max(a,min(b,x))
def pos_growth(v, good=.30): return clamp(v/good)
def competition_score(seller_count: float, seller_growth: float) -> float:
    count_factor=1-clamp((seller_count-5)/35)
    growth_factor=1-clamp(max(0,seller_growth)/.80)
    return .65*count_factor+.35*growth_factor

def age_score(days:int)->float:
    if 1<=days<=90: return 1
    if 91<=days<=180: return .7
    if 181<=days<=365: return .5
    return .25

def score_candidate(product_id: str, profit_margin: float=.30, supply_score: float=1.0, logistics_score: float=1.0) -> dict:
    cfg=load_yaml("scoring.yaml"); w=cfg["weights"]; t=cfg["thresholds"]
    with SessionLocal() as s: p=s.scalar(select(Product).where(Product.product_id==product_id))
    if not p: raise KeyError(product_id)
    risk=assess(p); f=market_features(product_id)
    if risk["hard_reject"]:
        return {"score":0,"grade":"REJECT","status":"REJECTED","reasons":risk["hard_reasons"],"features":f}
    parts={
      "sales_growth":pos_growth(f.get("sales_growth",0)),
      "search_growth":pos_growth(f.get("search_growth",0)),
      "cart_growth":pos_growth(f.get("cart_growth",0)),
      "competition":competition_score(f.get("seller_count",99),f.get("seller_growth",1)),
      "age":age_score(f.get("age_days",999)),
      "profit":clamp((profit_margin-.05)/.30),
      "logistics":clamp(logistics_score),
      "supply":clamp(supply_score),
      "risk":risk["risk_score"]/5,
    }
    total=round(sum(parts[k]*w[k] for k in w),2)
    grade="A" if total>=t["a"] else "B" if total>=t["b"] else "WATCH" if total>=t["watch"] else "REJECT"
    return {"score":total,"grade":grade,"status":"QUALIFIED" if grade in {"A","B"} else grade,"parts":parts,"features":f,"reasons":[]}
