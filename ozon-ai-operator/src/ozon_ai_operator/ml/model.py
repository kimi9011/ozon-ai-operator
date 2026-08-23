from __future__ import annotations
from pathlib import Path
import joblib, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES=["selection_score","sales_growth","search_growth","cart_growth","seller_count","profit_margin","ctr_7d","cart_rate_7d","cvr_7d"]

def train(df: pd.DataFrame, model_path="data/success_model.joblib"):
    if len(df)<50: raise ValueError("Need at least 50 labeled rows for a minimally meaningful model; 1000+ is preferred.")
    X=df[FEATURES].fillna(0); y=df["success_30d"].astype(int)
    model=Pipeline([("scale",StandardScaler()),("clf",LogisticRegression(max_iter=1000,class_weight="balanced"))])
    model.fit(X,y); Path(model_path).parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,model_path); return model

def predict(df: pd.DataFrame, model_path="data/success_model.joblib"):
    model=joblib.load(model_path); return model.predict_proba(df[FEATURES].fillna(0))[:,1]
