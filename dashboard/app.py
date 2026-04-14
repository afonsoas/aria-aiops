"""ARIA Dashboard — Aplicacao principal Streamlit."""
import streamlit as st

st.set_page_config(
    page_title="ARIA — AIOps Locaweb",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado com paleta ARIA
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #F0F4FF; }
    [data-testid="stSidebar"] { background: #0D1B3E; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .aria-header {
        background: linear-gradient(90deg, #0D1B3E 0%, #105BD8 100%);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .aria-header h1 { color: #FFFFFF; margin: 0; font-size: 2rem; }
    .aria-header p  { color: #00D4FF; margin: 0.3rem 0 0 0; font-size: 0.9rem; }
    .kpi-card {
        background: #FFFFFF;
        border-top: 4px solid #105BD8;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #105BD8; }
    .kpi-label { font-size: 0.85rem; color: #445; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aria-header">
    <h1>ARIA &nbsp;|&nbsp; Automated Response &amp; Incident Analysis</h1>
    <p>Enterprise Challenge — Locaweb AIOps &nbsp;·&nbsp; Cluster 3 | 2TSCO | FIAP 2026</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Navegacao")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("app.py", label="Home", icon="🏠")
with col2:
    st.page_link("pages/1_kpi_overview.py", label="KPI Overview", icon="📊")
with col3:
    st.page_link("pages/2_incident_list.py", label="Incidentes", icon="📋")
with col4:
    st.page_link("pages/3_ola_predictor.py", label="Preditor OLA", icon="🔮")
with col5:
    st.page_link("pages/4_patterns.py", label="Padroes", icon="🔍")

st.markdown("---")

# Cards de resumo
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dashboard.utils.data_loader import load_data
df = load_data()

df_kpi      = df[df["entrou_kpi"] == "SIM"]
n_violacoes = (df_kpi["kpi_violado"] == "SIM").sum()
pct_monitor = df["is_monitoring"].mean() * 100
pct_team14  = (df["grupo"] == "Team14").mean() * 100

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, f"{len(df):,}",      "Total de Incidentes",   "#105BD8"),
    (c2, f"{n_violacoes}",    "KPI Violados",           "#FF6B35"),
    (c3, f"{pct_monitor:.1f}%", "Via Monitoramento",   "#00D4FF"),
    (c4, f"{pct_team14:.1f}%",  "Concentracao Team14", "#00C87A"),
    (c5, f"{df['ano'].nunique()} anos", "Periodo",      "#7C3AED"),
]
for col, val, label, cor in metrics:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color:{cor}">
            <div class="kpi-value" style="color:{cor}">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Use o menu lateral ou os links acima para navegar pelas paginas do dashboard.")
