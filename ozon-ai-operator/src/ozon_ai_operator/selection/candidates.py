from __future__ import annotations
from sqlalchemy import select
from ..db import SessionLocal, Product, Candidate, init_db
from .scorer import score_candidate

def bucket_for(age_days:int)->str:
    if age_days<=30:return "trend_new"
    if age_days<=90:return "growth_30_90"
    return "mature"

def build_candidates(source="database", limit=200):
    init_db(); out=[]
    with SessionLocal() as s:
        products=s.scalars(select(Product).limit(limit)).all()
        for p in products:
            result=score_candidate(p.product_id)
            bucket=bucket_for(result.get("features",{}).get("age_days",999))
            c=Candidate(product_id=p.product_id,source=source,bucket=bucket,score=result["score"],grade=result["grade"],status=result["status"],reasons=",".join(result.get("reasons",[])))
            s.add(c); out.append({"product_id":p.product_id,"bucket":bucket,**result})
        s.commit()
    return out
