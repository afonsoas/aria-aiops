"""ARIA Dashboard — Home."""
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="ARIA — AIOps Locaweb",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.utils.theme import inject_css, kpi_card, aria_header, CYAN, ORANGE, GREEN, PURPLE, BLUE
from dashboard.utils.data_loader import load_data

inject_css()

st.markdown(aria_header(
    "ARIA &nbsp;|&nbsp; Automated Response &amp; Incident Analysis",
    "Enterprise Challenge &nbsp;·&nbsp; Locaweb AIOps &nbsp;·&nbsp; Cluster 3 | 2TSCO | FIAP 2026"
), unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem">
  <a href="." target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">🏠 Home</a>
  <a href="./1_kpi_overview" target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">📊 KPI Overview</a>
  <a href="./2_incident_list" target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">📋 Incidentes</a>
  <a href="./3_ola_predictor" target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">🔮 Preditor OLA</a>
  <a href="./4_patterns" target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">🔍 Padrões</a>
  <a href="./5_api_predictor" target="_self"
     style="background:rgba(16,91,216,0.2);border:1px solid rgba(0,212,255,0.3);
            border-radius:8px;padding:0.4rem 0.9rem;color:#00D4FF;
            text-decoration:none;font-size:0.85rem;font-weight:600">🔗 API Live</a>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

df      = load_data()
df_kpi  = df[df["entrou_kpi"] == "SIM"]
n_viol  = int((df_kpi["kpi_violado"] == "SIM").sum())
pct_mon = df["is_monitoring"].mean() * 100
pct_t14 = (df["grupo"] == "Team14").mean() * 100
n_anos  = df["ano"].nunique()

cols = st.columns(5)
cards = [
    (cols[0], f"{len(df):,}",      "Total de Incidentes",    f"Jan/2023 – Dez/2025",  BLUE),
    (cols[1], f"{n_viol}",         "KPI Violados",           f"{n_viol/len(df_kpi)*100:.2f}% dos elegíveis", ORANGE),
    (cols[2], f"{pct_mon:.1f}%",   "Via Monitoramento",      "Automaticos vs Manual",  CYAN),
    (cols[3], f"{pct_t14:.1f}%",   "Concentracao Team14",    "Grupo dominante",         GREEN),
    (cols[4], f"{n_anos} anos",    "Periodo Analisado",       "Dataset Locaweb",         PURPLE),
]
for col, val, label, sub, cor in cards:
    with col:
        st.markdown(kpi_card(val, label, sub, cor), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Destaques
st.markdown("""
<div style="
    display:grid;
    grid-template-columns: repeat(3,1fr);
    gap: 1rem;
    margin-top: 0.5rem;
">
  <div style="background:rgba(16,91,216,0.12);border:1px solid rgba(16,91,216,0.35);
               border-radius:12px;padding:1.2rem">
    <div style="color:#00D4FF;font-size:0.7rem;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:0.5rem">Modelo A — Predicao OLA</div>
    <div style="color:#fff;font-size:1.1rem;font-weight:700">XGBoost + SMOTE</div>
    <div style="color:#8899bb;font-size:0.82rem;margin-top:0.3rem">
        ROC-AUC 0.84 &nbsp;·&nbsp; Recall 60%<br>
        Treinado em 20.480 incidentes elegíveis
    </div>
  </div>
  <div style="background:rgba(0,200,122,0.10);border:1px solid rgba(0,200,122,0.3);
               border-radius:12px;padding:1.2rem">
    <div style="color:#00C87A;font-size:0.7rem;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:0.5rem">Modelo B — Classificacao Prioridade</div>
    <div style="color:#fff;font-size:1.1rem;font-weight:700">Random Forest</div>
    <div style="color:#8899bb;font-size:0.82rem;margin-top:0.3rem">
        F1-macro 0.90 &nbsp;·&nbsp; Accuracy 91%<br>
        Treinado em 97.767 incidentes
    </div>
  </div>
  <div style="background:rgba(255,107,53,0.10);border:1px solid rgba(255,107,53,0.3);
               border-radius:12px;padding:1.2rem">
    <div style="color:#FF6B35;font-size:0.7rem;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:0.5rem">Top Incidente</div>
    <div style="color:#fff;font-size:1.1rem;font-weight:700">Check Application Monitoring</div>
    <div style="color:#8899bb;font-size:0.82rem;margin-top:0.3rem">
        28.728 ocorrencias (23,4% do total)<br>
        Playbook automatico disponível
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("ARIA v1.0 — Sprint 2 | github.com/afonsoas/aria-aiops | Cluster 3 · 2TSCO · FIAP 2026")
