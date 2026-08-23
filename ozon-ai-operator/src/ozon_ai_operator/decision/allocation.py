from __future__ import annotations
from datetime import datetime,timedelta
from collections import defaultdict
from sqlalchemy import select
from ..db import SessionLocal, Product, StoreMetric
from ..config import load_yaml

def category_performance(days=30):
    since=datetime.utcnow()-timedelta(days=days); data=defaultdict(lambda:{"listed":set(),"orders":0,"revenue":0})
    with SessionLocal() as s:
        products={p.offer_id:p for p in s.scalars(select(Product).where(Product.offer_id.is_not(None))).all()}
        rows=s.scalars(select(StoreMetric).where(StoreMetric.date>=since)).all()
    for r in rows:
        p=products.get(r.offer_id)
        if not p: continue
        d=data[p.category]; d["listed"].add(r.offer_id); d["orders"]+=r.orders; d["revenue"]+=r.revenue
    out=[]
    for cat,d in data.items():
        listed=len(d["listed"]); success=d["orders"]/listed if listed else 0
        out.append({"category":cat,"listed":listed,"orders":d["orders"],"revenue":d["revenue"],"success_index":success})
    return sorted(out,key=lambda x:x["success_index"],reverse=True)

def next_day_allocation(target=None):
    cfg=load_yaml("strategy.yaml"); target=target or cfg["daily_target"]; explore=max(1,round(target*cfg["exploration_share"])); exploit=target-explore
    perf=category_performance()
    if not perf: return {"exploration":explore,"default_buckets":cfg["buckets"]}
    total=sum(max(.01,x["success_index"]) for x in perf[:5])
    alloc={}
    used=0
    for i,x in enumerate(perf[:5]):
        n=round(exploit*max(.01,x["success_index"])/total)
        alloc[x["category"]]=n; used+=n
    if alloc and used!=exploit:
        k=max(alloc,key=alloc.get); alloc[k]+=exploit-used
    return {"target":target,"exploration":explore,"exploit":alloc,"performance":perf[:10]}
