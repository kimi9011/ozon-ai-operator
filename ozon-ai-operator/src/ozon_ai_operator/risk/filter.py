from __future__ import annotations
from ..config import load_yaml

def assess(product) -> dict:
    cfg=load_yaml("risk_rules.yaml")
    hard=[]
    if getattr(product,"requires_certification",False): hard.append("requires_certification")
    if getattr(product,"brand_risk_high",False): hard.append("brand_risk_high")
    if getattr(product,"restricted_category",False): hard.append("restricted_category")
    if getattr(product,"dangerous_goods",False): hard.append("dangerous_goods")
    if getattr(product,"sku_count",1)>5: hard.append("sku_count_gt_5")
    penalty=0
    for key, pts in cfg.get("soft_penalties",{}).items():
        if getattr(product,key,False): penalty+=pts
    return {"hard_reject":bool(hard),"hard_reasons":hard,"penalty":penalty,"risk_score":max(0,5-penalty)}
