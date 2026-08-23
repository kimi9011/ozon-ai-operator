from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, func
from ..db import SessionLocal, Candidate, Product
from ..decision.allocation import next_day_allocation

def daily_report() -> str:
    today=datetime.utcnow().date()
    with SessionLocal() as s:
        candidates=s.scalars(select(Candidate)).all()
    grades={k:sum(1 for c in candidates if c.grade==k) for k in ["A","B","WATCH","REJECT"]}
    alloc=next_day_allocation()
    lines=[f"# Ozon AI Operator Daily Report — {today}","",f"Candidates total: {len(candidates)}",f"A: {grades['A']} | B: {grades['B']} | WATCH: {grades['WATCH']} | REJECT: {grades['REJECT']}","","## Next-day allocation", "```json", __import__('json').dumps(alloc,ensure_ascii=False,indent=2),"```"]
    return "\n".join(lines)
