"""
ARIA AIOps — API REST
FastAPI + Uvicorn | Sprint 3 MVP Preliminar

Endpoints:
  GET  /health               — status da API e dependencias
  POST /predict/ola          — probabilidade de violacao OLA
  POST /predict/priority     — classificacao de prioridade
  GET  /predictions/ola      — historico de predicoes OLA (DB)
  GET  /encoders/info        — valores disponiveis nos encoders

Iniciar:
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Ajuste de path para importar utils do dashboard
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.schemas import (
    IncidentInput, OLAPrediction, PriorityPrediction, HealthResponse,
)
from api.db import check_connection, ensure_tables, insert_ola_prediction, \
    insert_priority_prediction, fetch_recent_ola_predictions

# Importa loaders sem Streamlit (usamos joblib diretamente)
import joblib
import numpy as np
import scipy.sparse as sp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aria.api")

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="ARIA AIOps API",
    description="Automated Response & Incident Analysis — Locaweb / FIAP Enterprise Challenge 2026",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Modelos (carregados uma vez no startup) ───────────────────
MODEL_DIR = ROOT / "model"
_ola_bundle      = None
_priority_bundle = None
_encoders        = None
_models_ok       = False


@app.on_event("startup")
async def startup_event():
    global _ola_bundle, _priority_bundle, _encoders, _models_ok
    try:
        _ola_bundle      = joblib.load(MODEL_DIR / "model_ola.pkl")
        _priority_bundle = joblib.load(MODEL_DIR / "model_priority.pkl")
        _encoders        = joblib.load(MODEL_DIR / "encoders.pkl")
        _models_ok = True
        logger.info("Modelos ML carregados com sucesso.")
    except Exception as exc:
        logger.error("Falha ao carregar modelos: %s", exc)

    # Cria tabelas em background para não bloquear o startup
    import threading
    def _init_db():
        try:
            ensure_tables()
            logger.info("DB: tabelas verificadas/criadas.")
        except Exception as exc:
            logger.warning("ensure_tables falhou (modo offline): %s", exc)
    threading.Thread(target=_init_db, daemon=True).start()


# ── Helpers ───────────────────────────────────────────────────
def _safe_encode(col: str, val: Optional[str]) -> int:
    if val is None or _encoders is None:
        return 0
    le = _encoders.get(col)
    if le is None:
        return 0
    try:
        return int(le.transform([val])[0])
    except Exception:
        return 0


def _predict_ola(row: dict) -> float:
    model = _ola_bundle["model"]
    tfidf = _ola_bundle["tfidf"]
    feats = _ola_bundle["features"]
    num   = np.array([[row.get(f, 0) for f in feats]])
    txt   = tfidf.transform([row.get("descricao", "")])
    X     = sp.hstack([num, txt])
    return float(model.predict_proba(X)[0][1])


def _predict_priority(row: dict) -> int:
    model = _priority_bundle["model"]
    tfidf = _priority_bundle["tfidf"]
    feats = _priority_bundle["features"]
    num   = np.array([[row.get(f, 0) for f in feats]])
    txt   = tfidf.transform([row.get("descricao", "")])
    X     = sp.hstack([num, txt])
    return int(model.predict(X)[0])


def _nivel_risco(pct: float) -> tuple[str, str]:
    if pct >= 50:
        return "ALTO", "Escalar imediatamente para o grupo responsavel."
    if pct >= 25:
        return "MEDIO", "Monitorar; acionar time se sem resposta em 30 min."
    return "BAIXO", "Incidente dentro do padrao. Seguir fluxo standard."


# ── Rotas ─────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health():
    return HealthResponse(
        status="ok",
        version="3.0.0",
        modelos_carregados=_models_ok,
        db_conectado=check_connection(),
    )


@app.post("/predict/ola", response_model=OLAPrediction, tags=["Predicao"])
def predict_ola(payload: IncidentInput):
    """
    Calcula a probabilidade de violacao de OLA para um incidente.

    - **prio_num**: 1-5 (1=Critica, 5=Muito Baixa)
    - **hora_abertura**: 0-23
    - **dia_semana**: 0=Segunda ... 6=Domingo
    - **descricao**: texto livre do incidente
    """
    if not _models_ok:
        raise HTTPException(503, "Modelos nao carregados. Aguarde o startup.")

    row = payload.model_dump()

    # Re-encoda se strings foram passadas
    if payload.produto:
        row["produto_enc"] = _safe_encode("produto", payload.produto)
    if payload.grupo:
        row["grupo_enc"] = _safe_encode("grupo", payload.grupo)
    if payload.categoria:
        row["categoria_enc"] = _safe_encode("categoria", payload.categoria)
    if payload.subcategoria:
        row["subcategoria_enc"] = _safe_encode("subcategoria", payload.subcategoria)

    prob  = _predict_ola(row)
    pct   = prob * 100
    nivel, recomendacao = _nivel_risco(pct)

    # Persiste no Oracle ADB (falha silenciosa se offline)
    insert_ola_prediction(
        numero        = payload.numero,
        prio_num      = payload.prio_num,
        hora          = payload.hora_abertura,
        dia           = payload.dia_semana,
        is_monitoring = payload.is_monitoring,
        descricao     = payload.descricao,
        grupo         = payload.grupo,
        probabilidade = prob,
        nivel_risco   = nivel,
    )

    return OLAPrediction(
        probabilidade = round(prob, 4),
        percentual    = f"{pct:.1f}%",
        nivel_risco   = nivel,
        recomendacao  = recomendacao,
        numero        = payload.numero,
        timestamp     = datetime.now(timezone.utc),
    )


@app.post("/predict/priority", response_model=PriorityPrediction, tags=["Predicao"])
def predict_priority(payload: IncidentInput):
    """
    Classifica a prioridade esperada de um incidente (2=Alta, 3=Media, 4=Baixa).
    """
    if not _models_ok:
        raise HTTPException(503, "Modelos nao carregados. Aguarde o startup.")

    row = payload.model_dump()
    if payload.produto:
        row["produto_enc"] = _safe_encode("produto", payload.produto)
    if payload.grupo:
        row["grupo_enc"] = _safe_encode("grupo", payload.grupo)
    if payload.categoria:
        row["categoria_enc"] = _safe_encode("categoria", payload.categoria)
    if payload.subcategoria:
        row["subcategoria_enc"] = _safe_encode("subcategoria", payload.subcategoria)

    prio_pred = _predict_priority(row)
    labels    = {1: "1 - Critica", 2: "2 - Alta", 3: "3 - Media", 4: "4 - Baixa", 5: "5 - Muito Baixa"}

    insert_priority_prediction(
        numero             = payload.numero,
        prio_num_entrada   = payload.prio_num,
        prioridade_predita = prio_pred,
        descricao          = payload.descricao,
        grupo              = payload.grupo,
    )

    return PriorityPrediction(
        prioridade_predita = prio_pred,
        label              = labels.get(prio_pred, str(prio_pred)),
        numero             = payload.numero,
        timestamp          = datetime.now(timezone.utc),
    )


@app.get("/predictions/ola", tags=["Historico"])
def get_ola_predictions(limit: int = Query(100, ge=1, le=500)):
    """
    Retorna as ultimas predicoes OLA persistidas no Oracle ADB.
    Retorna lista vazia se DB nao configurado.
    """
    return fetch_recent_ola_predictions(limit)


@app.get("/encoders/info", tags=["Sistema"])
def encoders_info():
    """Lista os valores conhecidos por cada LabelEncoder."""
    if _encoders is None:
        return {}
    return {
        col: list(map(str, le.classes_.tolist()))
        for col, le in _encoders.items()
    }
