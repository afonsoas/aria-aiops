"""Pagina 1 — KPI Overview."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="KPI Overview — ARIA", layout="wide", page_icon="📊")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme, section_title
from dashboard.utils.theme import NAVY, BLUE, CYAN, ORANGE, GREEN, PURPLE, GRAY1, GRAY2
from dashboard.utils.data_loader import load_data, PRIO_COLORS

inject_css()
df = load_data()

# ── Sidebar filtros ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="color:{CYAN};font-size:1.1rem;font-weight:700;margin-bottom:1rem">⚙️ Filtros</div>', unsafe_allow_html=True)
    anos       = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    sel_anos   = st.multiselect("Ano", anos, default=anos)
    grupos_all = ["Todos"] + sorted(df["grupo"].unique().tolist())
    sel_grupo  = st.selectbox("Grupo", grupos_all)
    prios_all  = sorted(df["prioridade"].unique().tolist())
    sel_prios  = st.multiselect("Prioridade", prios_all, default=prios_all)

mask = df["ano"].isin(sel_anos) & df["prioridade"].isin(sel_prios)
if sel_grupo != "Todos":
    mask &= (df["grupo"] == sel_grupo)
dff    = df[mask]
df_kpi = dff[dff["entrou_kpi"] == "SIM"]
n_viol = int((df_kpi["kpi_violado"] == "SIM").sum())

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#0d2d6e 60%,#050e1f 100%);
            border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#00D4FF,#105BD8,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">📊 KPI Overview</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      Visao geral de incidentes e violacoes OLA
  </span>
</div>
""", unsafe_allow_html=True)

# ── KPI cards ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi_card(f"{len(dff):,}", "Total de Incidentes", f"Filtro ativo", BLUE), unsafe_allow_html=True)
with c2: st.markdown(kpi_card(f"{n_viol}", "KPI Violados", f"{n_viol/max(len(df_kpi),1)*100:.2f}% dos elegíveis", ORANGE), unsafe_allow_html=True)
with c3: st.markdown(kpi_card(f"{dff['is_monitoring'].mean()*100:.1f}%", "Via Monitoramento", "Automaticos", CYAN), unsafe_allow_html=True)
with c4:
    sem_int = dff["status"].str.contains("Sem Interv", na=False, case=False).sum()
    st.markdown(kpi_card(f"{sem_int/max(len(dff),1)*100:.1f}%", "Sem Intervencao", f"{sem_int:,} incidentes", GREEN), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Linha 1: Prioridades + Evolucao temporal ─────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-title">Distribuicao por Prioridade</div>', unsafe_allow_html=True)
    prio_counts = dff["prioridade"].value_counts().sort_index().reset_index()
    prio_counts.columns = ["Prioridade", "Qtd"]
    PRIO_COLOR_MAP = {
        "1 - Crítica": "#E74C3C", "2 - Alta": ORANGE,
        "3 - Média": BLUE, "4 - Baixa": GREEN, "5 - Muito Baixa": CYAN,
    }
    cores = [PRIO_COLOR_MAP.get(p, BLUE) for p in prio_counts["Prioridade"]]
    fig = go.Figure(go.Bar(
        x=prio_counts["Prioridade"], y=prio_counts["Qtd"],
        marker=dict(color=cores, line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=prio_counts["Qtd"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(color=GRAY1, size=11),
        cliponaxis=False,
    ))
    apply_plotly_theme(fig)
    max_val = prio_counts["Qtd"].max() if len(prio_counts) else 1
    fig.update_layout(
        height=320, showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(range=[0, max_val * 1.18],
                   showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

with col_b:
    st.markdown('<div class="section-title">Evolucao Mensal de Incidentes</div>', unsafe_allow_html=True)
    tempo = dff.groupby("ano_mes").size().reset_index(name="qtd")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=tempo["ano_mes"], y=tempo["qtd"],
        mode="lines+markers",
        line=dict(color=CYAN, width=2.5),
        marker=dict(size=4, color=CYAN),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.07)",
    ))
    apply_plotly_theme(fig2)
    fig2.update_layout(height=300,
                       xaxis=dict(tickangle=45, tickfont=dict(size=9)))
    st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

# ── Linha 2: Taxa OLA + Pie abertura ─────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="section-title">Taxa de Violacao OLA por Prioridade (%)</div>', unsafe_allow_html=True)
    kpi_prio = (
        df_kpi.groupby("prioridade")["kpi_violado"]
        .apply(lambda x: (x == "SIM").sum() / max(len(x), 1) * 100)
        .reset_index()
    )
    kpi_prio.columns = ["Prioridade", "Taxa"]
    fig3 = go.Figure(go.Bar(
        x=kpi_prio["Prioridade"], y=kpi_prio["Taxa"],
        marker=dict(
            color=kpi_prio["Taxa"],
            colorscale=[[0, "#00C87A"], [0.5, BLUE], [1, ORANGE]],
            showscale=False,
        ),
        text=kpi_prio["Taxa"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(color=GRAY1, size=11),
        cliponaxis=False,
    ))
    apply_plotly_theme(fig3)
    max_taxa = kpi_prio["Taxa"].max() if len(kpi_prio) else 1
    fig3.update_layout(
        height=320, yaxis_title="% de Violacao",
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(range=[0, max_taxa * 1.25]),
    )
    st.plotly_chart(fig3, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

with col_d:
    st.markdown('<div class="section-title">Abertura: Monitoramento vs Manual</div>', unsafe_allow_html=True)
    abertura = dff["aberto_por"].value_counts().reset_index()
    abertura.columns = ["Tipo", "Qtd"]
    fig4 = go.Figure(go.Pie(
        labels=abertura["Tipo"], values=abertura["Qtd"],
        hole=0.55,
        marker=dict(
            colors=[CYAN, ORANGE, BLUE, GREEN],
            line=dict(color=NAVY, width=2),
        ),
        textfont=dict(color=GRAY1, size=11),
    ))
    apply_plotly_theme(fig4)
    fig4.update_traces(
        textinfo="percent+label",
        textposition="outside",
        textfont=dict(size=10, color=GRAY1),
        pull=[0.03] * len(abertura),
    )
    fig4.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=60),
        annotations=[dict(text=f"{abertura['Qtd'].sum():,}", x=0.5, y=0.5,
                          font=dict(size=15, color="white"), showarrow=False)],
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
                    font=dict(size=10)),
        showlegend=True,
    )
    st.plotly_chart(fig4, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

# ── Heatmap hora x dia ───────────────────────────────────────
st.markdown('<div class="section-title">Heatmap — Hora de Abertura x Dia da Semana</div>', unsafe_allow_html=True)
dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
hm = dff.groupby(["dia_semana", "hora_abertura"]).size().reset_index(name="qtd")
hm_pivot = hm.pivot(index="dia_semana", columns="hora_abertura", values="qtd").fillna(0)
hm_pivot.index = [dias[i] for i in hm_pivot.index]
fig5 = go.Figure(go.Heatmap(
    z=hm_pivot.values,
    x=[str(h) + "h" for h in hm_pivot.columns],
    y=hm_pivot.index.tolist(),
    colorscale=[[0, "rgba(10,22,40,0.8)"], [0.4, "#0d2d6e"], [0.7, BLUE], [1, CYAN]],
    showscale=True,
    hovertemplate="Hora: %{x}<br>Dia: %{y}<br>Incidentes: %{z:,}<extra></extra>",
    colorbar=dict(tickfont=dict(color=GRAY2), title=dict(text="Qtd", font=dict(color=GRAY2))),
))
apply_plotly_theme(fig5)
fig5.update_layout(
    height=250,
    margin=dict(l=50, r=20, t=10, b=40),
    xaxis=dict(tickangle=0, tickfont=dict(size=9), side="bottom"),
)
st.plotly_chart(fig5, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

# ── Top grupos ───────────────────────────────────────────────
st.markdown('<div class="section-title">Top 10 Grupos por Volume</div>', unsafe_allow_html=True)
grp = dff["grupo"].value_counts().head(10).reset_index()
grp.columns = ["Grupo", "Qtd"]
grp = grp.sort_values("Qtd")
max_grp = int(grp["Qtd"].max()) if len(grp) else 1
fig6 = go.Figure(go.Bar(
    x=grp["Qtd"], y=grp["Grupo"], orientation="h",
    marker=dict(
        color=grp["Qtd"],
        colorscale=[[0, "#0d2d6e"], [1, CYAN]],
        showscale=False,
        line=dict(color="rgba(255,255,255,0.05)", width=1),
    ),
    text=grp["Qtd"].apply(lambda x: f"{x:,}"),
    textposition="outside",
    textfont=dict(color=GRAY1, size=11),
    cliponaxis=False,
))
apply_plotly_theme(fig6)
fig6.update_layout(
    height=340,
    margin=dict(l=80, r=80, t=10, b=30),
    xaxis=dict(
        range=[0, max_grp * 1.18],
        title="Qtd. Incidentes",
        showgrid=True, gridcolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(tickfont=dict(size=11), automargin=True),
)
st.plotly_chart(fig6, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
