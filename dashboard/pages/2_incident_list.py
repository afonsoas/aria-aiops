"""Pagina 2 — Lista de Incidentes."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Incidentes — ARIA", layout="wide", page_icon="📋")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme, section_title
from dashboard.utils.theme import BLUE, CYAN, ORANGE, GREEN, PURPLE, GRAY1, GRAY2, NAVY
from dashboard.utils.data_loader import load_data

inject_css()
df = load_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="color:{CYAN};font-size:1.1rem;font-weight:700;margin-bottom:1rem">⚙️ Filtros</div>', unsafe_allow_html=True)
    anos        = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    prios       = sorted(df["prioridade"].unique().tolist())
    grupos      = ["Todos"] + sorted(df["grupo"].unique().tolist())
    status_opts = ["Todos"] + sorted(df["status"].unique().tolist())

    sel_anos         = st.multiselect("Ano", anos, default=[max(anos)])
    sel_prios        = st.multiselect("Prioridade", prios, default=prios)
    sel_grupo        = st.selectbox("Grupo", grupos)
    sel_status       = st.selectbox("Status", status_opts)
    busca            = st.text_input("🔍 Buscar na descricao")
    somente_violados = st.checkbox("Apenas KPI Violados")

mask = df["ano"].isin(sel_anos) & df["prioridade"].isin(sel_prios)
if sel_grupo != "Todos":
    mask &= df["grupo"] == sel_grupo
if sel_status != "Todos":
    mask &= df["status"] == sel_status
if busca:
    mask &= df["descricao"].str.contains(busca, case=False, na=False)
if somente_violados:
    mask &= df["kpi_violado"] == "SIM"
dff = df[mask].copy()

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#0d2d6e 60%,#050e1f 100%);
            border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#FF6B35,#105BD8,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">📋 Lista de Incidentes</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      Tabela filtravel com badge de risco OLA
  </span>
</div>
""", unsafe_allow_html=True)

# ── Mini KPIs ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
viol_f = int((dff["kpi_violado"] == "SIM").sum())
alto_f = int(((dff["prio_num"] <= 2) & (dff["entrou_kpi"] == "SIM")).sum())

with c1: st.markdown(kpi_card(f"{len(dff):,}", "Encontrados", "com filtro ativo", BLUE), unsafe_allow_html=True)
with c2: st.markdown(kpi_card(f"{viol_f}", "KPI Violados", "no filtro", ORANGE), unsafe_allow_html=True)
with c3: st.markdown(kpi_card(f"{alto_f}", "Alta Prioridade KPI", "prio ≤ 2", CYAN), unsafe_allow_html=True)
with c4:
    enc_auto = int(dff["status"].str.contains("Automaticamente", na=False, case=False).sum())
    st.markdown(kpi_card(f"{enc_auto:,}", "Encerrado Auto", "sem intervencao", GREEN), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Badge de risco ───────────────────────────────────────────
RISCO_COR   = {"VIOLADO": ORANGE, "ALTO": "#e67e22", "MEDIO": "#f39c12", "BAIXO": GREEN}
RISCO_EMOJI = {"VIOLADO": "🔴", "ALTO": "🟠", "MEDIO": "🟡", "BAIXO": "🟢"}
PRIO_COR    = {"1": "#e74c3c","2": ORANGE,"3": BLUE,"4": GREEN,"5": CYAN}

def risco_badge(row):
    if row.get("kpi_violado") == "SIM":       return "VIOLADO"
    pn = row.get("prio_num", 4)
    if pn <= 2 and row.get("entrou_kpi") == "SIM": return "ALTO"
    if pn == 3:                                return "MEDIO"
    return "BAIXO"

dff["risco_ola"] = dff.apply(risco_badge, axis=1)

# ── Mini grafico de risco (sparkline) ────────────────────────
col_spark, col_table = st.columns([1, 3])

with col_spark:
    st.markdown('<div class="section-title">Distribuicao de Risco</div>', unsafe_allow_html=True)
    risco_counts = dff["risco_ola"].value_counts()
    ordem = ["VIOLADO", "ALTO", "MEDIO", "BAIXO"]
    vals  = [risco_counts.get(r, 0) for r in ordem]
    cors  = [RISCO_COR[r] for r in ordem]
    fig_r = go.Figure(go.Bar(
        x=ordem, y=vals,
        marker=dict(color=cors, line=dict(color="rgba(255,255,255,0.08)", width=1)),
        text=vals, textposition="outside",
        textfont=dict(color=GRAY1, size=11),
    ))
    apply_plotly_theme(fig_r)
    fig_r.update_layout(height=220, showlegend=False,
                        margin=dict(l=5, r=5, t=5, b=5))
    st.plotly_chart(fig_r, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:0.8rem">Por Prioridade</div>', unsafe_allow_html=True)
    prio_f = dff["prioridade"].value_counts().reset_index()
    prio_f.columns = ["Prioridade", "Qtd"]
    prio_f = prio_f.sort_values("Prioridade")
    fig_p = go.Figure(go.Pie(
        labels=prio_f["Prioridade"], values=prio_f["Qtd"],
        hole=0.6,
        marker=dict(colors=[ORANGE, BLUE, GREEN, CYAN], line=dict(color=NAVY, width=2)),
        textfont=dict(color=GRAY1, size=10),
    ))
    apply_plotly_theme(fig_p)
    fig_p.update_layout(height=200, margin=dict(l=0,r=0,t=5,b=0),
                        showlegend=True,
                        legend=dict(font=dict(size=9), orientation="v"))
    st.plotly_chart(fig_p, use_container_width=True)

with col_table:
    st.markdown('<div class="section-title">Tabela de Incidentes</div>', unsafe_allow_html=True)

    cols_show = ["numero","prioridade","descricao","grupo","status","risco_ola","aberto","entrou_kpi","kpi_violado"]
    cols_show = [c for c in cols_show if c in dff.columns]
    disp = dff[cols_show].copy()
    disp["risco_ola"] = disp["risco_ola"].map(lambda x: f"{RISCO_EMOJI.get(x,'')} {x}")
    if "aberto" in disp.columns:
        disp["aberto"] = disp["aberto"].dt.strftime("%d/%m/%Y %H:%M")
    disp = disp.rename(columns={
        "numero":"Numero","prioridade":"Prioridade","descricao":"Descricao",
        "grupo":"Grupo","status":"Status","risco_ola":"Risco OLA",
        "aberto":"Aberto em","entrou_kpi":"KPI?","kpi_violado":"Violou?",
    })
    st.dataframe(
        disp.head(500),
        use_container_width=True,
        height=460,
        column_config={
            "Descricao": st.column_config.TextColumn(width="large"),
            "Risco OLA": st.column_config.TextColumn(width="small"),
        },
    )

# ── Exportar ─────────────────────────────────────────────────
csv = dff[cols_show].to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="⬇️  Exportar CSV",
    data=csv,
    file_name="aria_incidentes.csv",
    mime="text/csv",
)
