"""Pagina 1 — KPI Overview."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="KPI Overview — ARIA", layout="wide", page_icon="📊")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.data_loader import load_data, NAVY, BLUE, CYAN, ORANGE, GREEN, PRIO_COLORS

df = load_data()

st.title("📊 KPI Overview")
st.caption("Visao geral de incidentes e violacoes OLA — Jan/2023 a Dez/2025")

# ── Filtros ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    anos = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    sel_anos = st.multiselect("Ano", anos, default=anos)
    grupos_opts = ["Todos"] + sorted(df["grupo"].unique().tolist())
    sel_grupo = st.selectbox("Grupo", grupos_opts)
    prios_opts = sorted(df["prioridade"].unique().tolist())
    sel_prios = st.multiselect("Prioridade", prios_opts, default=prios_opts)

# Filtrar
mask = df["ano"].isin(sel_anos) & df["prioridade"].isin(sel_prios)
if sel_grupo != "Todos":
    mask &= (df["grupo"] == sel_grupo)
dff = df[mask]

df_kpi = dff[dff["entrou_kpi"] == "SIM"]
n_viol = (df_kpi["kpi_violado"] == "SIM").sum()

# ── KPI cards ───────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de Incidentes",    f"{len(dff):,}")
c2.metric("KPI Violados",           f"{n_viol}",
          delta=f"{n_viol/max(len(df_kpi),1)*100:.2f}% dos elegíveis",
          delta_color="inverse")
c3.metric("Via Monitoramento",      f"{dff['is_monitoring'].mean()*100:.1f}%")
c4.metric("Status Sem Intervencao", f"{(dff['status'].str.contains('Sem Interv', na=False, case=False).sum()/max(len(dff),1))*100:.1f}%")

st.markdown("---")

col_a, col_b = st.columns(2)

# Distribuicao de prioridades
with col_a:
    st.subheader("Distribuicao por Prioridade")
    prio_counts = dff["prioridade"].value_counts().sort_index().reset_index()
    prio_counts.columns = ["Prioridade", "Qtd"]
    fig = px.bar(prio_counts, x="Prioridade", y="Qtd",
                 color="Prioridade",
                 color_discrete_map={p: c for p, c in PRIO_COLORS.items()},
                 text="Qtd")
    fig.update_layout(showlegend=False, plot_bgcolor="white",
                      yaxis_title="Qtd. Incidentes", xaxis_title="")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Evolucao temporal
with col_b:
    st.subheader("Evolucao Mensal de Incidentes")
    tempo = dff.groupby("ano_mes").size().reset_index(name="qtd")
    fig2 = px.line(tempo, x="ano_mes", y="qtd",
                   markers=True, color_discrete_sequence=[BLUE])
    fig2.update_layout(plot_bgcolor="white",
                       xaxis_title="Mes", yaxis_title="Qtd. Incidentes",
                       xaxis=dict(tickangle=45))
    fig2.update_traces(line_width=2)
    st.plotly_chart(fig2, use_container_width=True)

col_c, col_d = st.columns(2)

# Taxa de violacao OLA por prioridade
with col_c:
    st.subheader("Taxa de Violacao OLA por Prioridade (%)")
    kpi_prio = (
        df_kpi.groupby("prioridade")["kpi_violado"]
        .apply(lambda x: (x == "SIM").sum() / max(len(x), 1) * 100)
        .reset_index()
    )
    kpi_prio.columns = ["Prioridade", "Taxa (%)"]
    fig3 = px.bar(kpi_prio, x="Prioridade", y="Taxa (%)",
                  color_discrete_sequence=[ORANGE], text="Taxa (%)")
    fig3.update_layout(plot_bgcolor="white")
    fig3.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

# Pie chart abertura
with col_d:
    st.subheader("Abertura: Monitoramento vs Manual")
    abertura = dff["aberto_por"].value_counts().reset_index()
    abertura.columns = ["Tipo", "Qtd"]
    fig4 = px.pie(abertura, names="Tipo", values="Qtd",
                  color_discrete_sequence=[CYAN, ORANGE, BLUE, GREEN])
    fig4.update_layout(legend_title="Tipo de abertura")
    st.plotly_chart(fig4, use_container_width=True)

# Heatmap hora x dia
st.subheader("Heatmap de Abertura: Hora x Dia da Semana")
dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
hm = dff.groupby(["dia_semana", "hora_abertura"]).size().reset_index(name="qtd")
hm_pivot = hm.pivot(index="dia_semana", columns="hora_abertura", values="qtd").fillna(0)
hm_pivot.index = [dias[i] for i in hm_pivot.index]
fig5 = px.imshow(hm_pivot, aspect="auto",
                 color_continuous_scale=[[0, "#E8EEFF"], [0.5, BLUE], [1, NAVY]],
                 labels=dict(x="Hora", y="Dia", color="Qtd"))
fig5.update_layout(height=280)
st.plotly_chart(fig5, use_container_width=True)
