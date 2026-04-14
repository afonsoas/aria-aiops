"""Pagina 2 — Lista de Incidentes."""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Incidentes — ARIA", layout="wide", page_icon="📋")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.data_loader import load_data, PRIO_COLORS

df = load_data()

st.title("📋 Lista de Incidentes")
st.caption("Tabela filtravel com badge de prioridade e risco OLA")

# Filtros
with st.sidebar:
    st.header("Filtros")
    anos   = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    prios  = sorted(df["prioridade"].unique().tolist())
    grupos = ["Todos"] + sorted(df["grupo"].unique().tolist())
    status_opts = ["Todos"] + sorted(df["status"].unique().tolist())

    sel_anos   = st.multiselect("Ano", anos, default=[max(anos)])
    sel_prios  = st.multiselect("Prioridade", prios, default=prios)
    sel_grupo  = st.selectbox("Grupo", grupos)
    sel_status = st.selectbox("Status", status_opts)
    busca      = st.text_input("Buscar na descricao")
    somente_violados = st.checkbox("Apenas KPI Violados")

mask = (
    df["ano"].isin(sel_anos) &
    df["prioridade"].isin(sel_prios)
)
if sel_grupo != "Todos":
    mask &= df["grupo"] == sel_grupo
if sel_status != "Todos":
    mask &= df["status"] == sel_status
if busca:
    mask &= df["descricao"].str.contains(busca, case=False, na=False)
if somente_violados:
    mask &= (df["kpi_violado"] == "SIM")

dff = df[mask].copy()

# Badge de risco simplificado: Alta prio + entrou KPI = ALTO, Media = MEDIO, outros = BAIXO
def risco_badge(row):
    if row.get("kpi_violado") == "SIM":
        return "VIOLADO"
    pn = row.get("prio_num", 4)
    if pn <= 2 and row.get("entrou_kpi") == "SIM":
        return "ALTO"
    elif pn == 3:
        return "MEDIO"
    return "BAIXO"

dff["risco_ola"] = dff.apply(risco_badge, axis=1)

RISCO_EMOJI = {"VIOLADO": "🔴", "ALTO": "🟠", "MEDIO": "🟡", "BAIXO": "🟢"}

st.info(f"**{len(dff):,}** incidentes encontrados")

# Colunas para exibicao
cols_show = ["numero", "prioridade", "descricao", "grupo", "status",
             "risco_ola", "aberto", "entrou_kpi", "kpi_violado"]
cols_show = [c for c in cols_show if c in dff.columns]
disp = dff[cols_show].copy()
disp["risco_ola"] = disp["risco_ola"].map(lambda x: f"{RISCO_EMOJI.get(x,'')} {x}")
if "aberto" in disp.columns:
    disp["aberto"] = disp["aberto"].dt.strftime("%d/%m/%Y %H:%M")

disp = disp.rename(columns={
    "numero": "Numero",
    "prioridade": "Prioridade",
    "descricao": "Descricao",
    "grupo": "Grupo",
    "status": "Status",
    "risco_ola": "Risco OLA",
    "aberto": "Aberto em",
    "entrou_kpi": "KPI?",
    "kpi_violado": "Violou?",
})

st.dataframe(disp.head(500), use_container_width=True, height=500)

# Exportar
csv = dff[cols_show].to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="Exportar CSV",
    data=csv,
    file_name="aria_incidentes.csv",
    mime="text/csv",
)
