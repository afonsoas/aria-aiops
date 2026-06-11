"""
Testes da API ARIA — roda com: pytest tests/ -v
Nao requer banco: sem credenciais, a API opera em modo offline.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402

PAYLOAD = {
    "prio_num": 3,
    "hora_abertura": 10,
    "dia_semana": 0,
    "mes": 4,
    "is_monitoring": 1,
    "has_parent": 0,
    "descricao": "Problem: Check Application Monitoring",
    "numero": "INC0099999",
    "grupo": "Team01",
}


@pytest.fixture(scope="module")
def client():
    # TestClient como context manager dispara o evento de startup
    # (carregamento dos modelos)
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["modelos_carregados"] is True


def test_predict_ola(client):
    r = client.post("/predict/ola", json=PAYLOAD)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["probabilidade"] <= 1.0
    assert data["nivel_risco"] in ("BAIXO", "MEDIO", "ALTO")
    assert data["numero"] == "INC0099999"


def test_predict_ola_batch(client):
    r = client.post("/predict/ola/batch", json={"incidents": [PAYLOAD, PAYLOAD]})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert data["alto_risco"] + data["medio_risco"] + data["baixo_risco"] == 2
    assert len(data["predicoes"]) == 2


def test_predict_ola_batch_limite(client):
    r = client.post("/predict/ola/batch", json={"incidents": [PAYLOAD] * 101})
    assert r.status_code == 422  # max_length=100 no schema


def test_predict_priority(client):
    r = client.post("/predict/priority", json=PAYLOAD)
    assert r.status_code == 200
    data = r.json()
    assert data["prioridade_predita"] in (1, 2, 3, 4, 5)
    assert data["label"]


def test_explain_ola(client):
    r = client.post("/explain/ola", json=PAYLOAD)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["probabilidade"] <= 1.0
    assert isinstance(data["top_features"], list)
    assert len(data["top_features"]) > 0
    for feat in data["top_features"]:
        assert feat["direcao"] in ("aumenta", "reduz")


def test_model_metrics(client):
    r = client.get("/model/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "roc_auc" in data["modelo_ola"]
    assert "f1_macro" in data["modelo_prioridade"]
    assert 0.5 <= data["modelo_ola"]["roc_auc"] <= 1.0


def test_encoders_info(client):
    r = client.get("/encoders/info")
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) == {"produto", "grupo", "categoria",
                                "subcategoria", "cod_fechamento"}


def test_payload_invalido(client):
    r = client.post("/predict/ola", json={"prio_num": 99})
    assert r.status_code == 422  # fora do range 1-5


def test_api_key_quando_configurada(client):
    os.environ["ARIA_API_KEY"] = "chave-de-teste"
    try:
        r = client.post("/predict/ola", json=PAYLOAD)
        assert r.status_code == 401
        r = client.post("/predict/ola", json=PAYLOAD,
                        headers={"X-API-Key": "chave-de-teste"})
        assert r.status_code == 200
    finally:
        del os.environ["ARIA_API_KEY"]
