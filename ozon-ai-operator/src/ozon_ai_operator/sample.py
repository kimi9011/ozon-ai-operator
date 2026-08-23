from __future__ import annotations
from datetime import datetime,timedelta
import random, pandas as pd
from pathlib import Path

def generate(outdir="data/sample"):
    random.seed(42); out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    cats=["pets","home","kitchen","automotive","diy"]
    products=[]; market=[]; store=[]; now=datetime.utcnow()
    for i in range(1,61):
        pid=f"P{i:04d}"; offer=f"O{i:04d}"; cat=random.choice(cats); age=random.randint(5,160)
        products.append({"product_id":pid,"created_at":(now-timedelta(days=age)).isoformat(),"offer_id":offer,"name":f"Sample product {i}","category":cat,"subcategory":"general","brand":"generic","sku_count":1,"requires_certification":False,"restricted_category":False,"dangerous_goods":False,"brand_risk_high":False,"fragile":False,"battery":False,"return_risk_high":False,"compatibility_complex":False})
        base_sales=random.randint(20,500); base_search=random.randint(100,3000); base_cart=random.randint(10,300); sellers=random.randint(3,35)
        for d in [30,15,7,0]:
            growth=(30-d)/30
            market.append({"date":now-timedelta(days=d),"product_id":pid,"sales":base_sales*(1+growth*random.uniform(.05,.65)),"search_volume":base_search*(1+growth*random.uniform(-.05,.70)),"cart_additions":base_cart*(1+growth*random.uniform(-.05,.80)),"seller_count":sellers*(1+growth*random.uniform(0,.55)),"lowest_price":random.randint(800,2500),"median_price":random.randint(1000,3000)})
        for d in range(0,30):
            imp=max(0,int(random.gauss(180,90))); clicks=max(0,int(imp*max(.005,random.gauss(.04,.015)))); carts=max(0,int(clicks*max(.02,random.gauss(.16,.06)))); orders=max(0,int(clicks*max(.005,random.gauss(.06,.03))))
            store.append({"date":now-timedelta(days=d),"offer_id":offer,"impressions":imp,"clicks":clicks,"cart_additions":carts,"orders":orders,"revenue":orders*random.randint(1000,2500),"returns":1 if orders and random.random()<.06 else 0,"price":random.randint(1100,2600),"stock":random.randint(0,100)})
    pd.DataFrame(products).to_csv(out/"products.csv",index=False); pd.DataFrame(market).to_csv(out/"market.csv",index=False); pd.DataFrame(store).to_csv(out/"store.csv",index=False)
    return out
