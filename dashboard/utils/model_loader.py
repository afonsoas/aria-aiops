"""Carregamento dos modelos ML treinados."""
import streamlit as st
import joblib
import pandas as pd
import numpy as np
import scipy.sparse as sp
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "model"

@st.cache_resource(show_spinner="Carregando modelos ML...")
def load_models():
    ola      = joblib.load(MODEL_DIR / "model_ola.pkl")
    priority = joblib.load(MODEL_DIR / "model_priority.pkl")
    encoders = joblib.load(MODEL_DIR / "encoders.pkl")
    return ola, priority, encoders


def predict_ola(ola_bundle, row: dict) -> float:
    """Retorna probabilidade de violar OLA (0-1)."""
    model  = ola_bundle["model"]
    tfidf  = ola_bundle["tfidf"]
    feats  = ola_bundle["features"]

    num = np.array([[row.get(f, 0) for f in feats]])
    txt = tfidf.transform([row.get("descricao", "")])
    X   = sp.hstack([num, txt])
    return float(model.predict_proba(X)[0][1])


def predict_priority(prio_bundle, row: dict) -> int:
    """Retorna prioridade predita (2, 3 ou 4)."""
    model  = prio_bundle["model"]
    tfidf  = prio_bundle["tfidf"]
    feats  = prio_bundle["features"]

    num = np.array([[row.get(f, 0) for f in feats]])
    txt = tfidf.transform([row.get("descricao", "")])
    X   = sp.hstack([num, txt]).toarray()
    return int(model.predict(X)[0])
