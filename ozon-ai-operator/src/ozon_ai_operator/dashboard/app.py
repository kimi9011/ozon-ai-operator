from __future__ import annotations
import streamlit as st, pandas as pd
from sqlalchemy import select
from ..db import SessionLocal, Candidate, StoreMetric
from ..decision.allocation import category_performance, next_day_allocation

st.set_page_config(page_title="Ozon AI Operator", layout="wide")
st.title("Ozon AI Operator")
with SessionLocal() as s:
    candidates=s.scalars(select(Candidate)).all()
    metrics=s.scalars(select(StoreMetric)).all()
cols=st.columns(4)
cols[0].metric("候选商品",len(candidates)); cols[1].metric("A级",sum(c.grade=="A" for c in candidates)); cols[2].metric("B级",sum(c.grade=="B" for c in candidates)); cols[3].metric("已记录日数据",len(metrics))
st.subheader("类目表现")
st.dataframe(pd.DataFrame(category_performance()))
st.subheader("下一轮选品分配")
st.json(next_day_allocation())
