"""Carregamento dos modelos ML treinados."""
import sys
import streamlit as st
import joblib
import numpy as np
import scipy.sparse as sp
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "model"

# ── Definido aqui para que pickle encontre ao carregar .pkl salvo como __main__._CalibratedXGB ──
class _CalibratedXGB:
    """Wrapper de calibracao isotonica sobre XGBoost."""
    def __init__(self, base, calibrator, threshold=0.5):
        self.base = base
        self.calibrator = calibrator
        self.threshold = threshold
        self.classes_ = getattr(base, "classes_", np.array([0, 1]))

    def predict_proba(self, X):
        raw = self.base.predict_proba(X)[:, 1]
        cal = self.calibrator.predict(raw)
        return np.column_stack([1 - cal, cal])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= self.threshold).astype(int)


# Injeta em __main__ para compatibilidade com pickle que serializou como __main__._CalibratedXGB
import __main__
if not hasattr(__main__, "_CalibratedXGB"):
    __main__._CalibratedXGB = _CalibratedXGB


@st.cache_resource(show_spinner="Carregando modelos ML...")
def load_models():
    ola      = joblib.load(MODEL_DIR / "model_ola.pkl")
    priority = joblib.load(MODEL_DIR / "model_priority.pkl")
    encoders = joblib.load(MODEL_DIR / "encoders.pkl")
    return ola, priority, encoders


def predict_ola(ola_bundle, row: dict) -> float:
    model  = ola_bundle["model"]
    tfidf  = ola_bundle["tfidf"]
    feats  = ola_bundle["features"]
    num = np.array([[row.get(f, 0) for f in feats]])
    txt = tfidf.transform([row.get("descricao", "")])
    X   = sp.hstack([num, txt])
    return float(model.predict_proba(X)[0][1])


def predict_priority(prio_bundle, row: dict) -> int:
    model  = prio_bundle["model"]
    tfidf  = prio_bundle["tfidf"]
    feats  = prio_bundle["features"]
    num = np.array([[row.get(f, 0) for f in feats]])
    txt = tfidf.transform([row.get("descricao", "")])
    X   = sp.hstack([num, txt])
    return int(model.predict(X)[0])
