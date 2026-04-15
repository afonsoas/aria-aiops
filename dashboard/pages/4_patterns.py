"""Pagina 4 — Padroes Recorrentes."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Padroes — ARIA", layout="wide", page_icon="🔍")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme, section_title
from dashboard.utils.theme import NAVY, BLUE, CYAN, ORANGE, GREEN, PURPLE, GRAY1, GRAY2

inject_css()
from dashboard.utils.data_loader import load_data
df = load_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="color:{CYAN};font-size:1.1rem;font-weight:700;margin-bottom:1rem">⚙️ Filtros</div>', unsafe_allow_html=True)
    anos     = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    sel_anos = st.multiselect("Ano", anos, default=anos)
    top_n    = st.slider("Top N descricoes", 5, 30, 20)
    sel_grupo_p = st.selectbox("Grupo (treemap)", ["Todos"] + sorted(df["grupo"].unique().tolist()))

dff = df[df["ano"].isin(sel_anos)]
if sel_grupo_p != "Todos":
    dff = dff[dff["grupo"] == sel_grupo_p]

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#0d2d6e 60%,#050e1f 100%);
            border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#7C3AED,#105BD8,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">🔍 Padroes Recorrentes</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      Top descricoes, treemap e playbooks automaticos
  </span>
</div>
""", unsafe_allow_html=True)

# ── KPIs rápidos ─────────────────────────────────────────────
top1       = dff["descricao"].value_counts().index[0] if len(dff) else "—"
top1_count = int(dff["descricao"].value_counts().iloc[0]) if len(dff) else 0
n_uniq_desc = dff["descricao"].nunique()
n_grupos    = dff["grupo"].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi_card(f"{top1_count:,}", "Ocorrencias Top 1", top1[:35]+"...", ORANGE), unsafe_allow_html=True)
with c2: st.markdown(kpi_card(f"{n_uniq_desc:,}", "Desc. Unicas", "tipos distintos", BLUE), unsafe_allow_html=True)
with c3: st.markdown(kpi_card(f"{n_grupos}", "Grupos Ativos", "no filtro", CYAN), unsafe_allow_html=True)
with c4: st.markdown(kpi_card(f"{len(dff):,}", "Incidentes", "no filtro", GREEN), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Linha 1: Top N + Pie grupos ──────────────────────────────
col_a, col_b = st.columns([1.4, 1])

with col_a:
    st.markdown('<div class="section-title">Top Descricoes mais Frequentes</div>', unsafe_allow_html=True)
    top_desc = dff["descricao"].value_counts().head(top_n).reset_index()
    top_desc.columns = ["Descricao", "Qtd"]
    top_desc["Label"] = top_desc["Descricao"].str.replace("Problem: ", "", regex=False).str[:55]
    top_desc = top_desc.sort_values("Qtd")

    fig = go.Figure(go.Bar(
        x=top_desc["Qtd"],
        y=top_desc["Label"],
        orientation="h",
        marker=dict(
            color=top_desc["Qtd"],
            colorscale=[[0, "#0d2d6e"], [0.5, BLUE], [1, CYAN]],
            showscale=False,
            line=dict(color="rgba(255,255,255,0.05)", width=1),
        ),
        text=top_desc["Qtd"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(color=GRAY1, size=10),
    ))
    apply_plotly_theme(fig)
    fig.update_layout(
        height=max(320, top_n * 22),
        xaxis_title="Frequencia",
        yaxis=dict(tickfont=dict(size=9), automargin=True),
        margin=dict(l=5, r=60, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">Volume por Grupo</div>', unsafe_allow_html=True)
    grp = dff["grupo"].value_counts().head(10).reset_index()
    grp.columns = ["Grupo", "Qtd"]
    palette = [BLUE, ORANGE, GREEN, CYAN, PURPLE, "#e74c3c", "#f1c40f", "#1abc9c", "#95a5a6", "#e67e22"]
    fig2 = go.Figure(go.Pie(
        labels=grp["Grupo"], values=grp["Qtd"],
        hole=0.55,
        marker=dict(colors=palette, line=dict(color=NAVY, width=2)),
        textfont=dict(color=GRAY1, size=10),
        textposition="inside",
    ))
    apply_plotly_theme(fig2)
    fig2.update_layout(
        height=280,
        annotations=[dict(text=f"{grp['Qtd'].sum():,}", x=0.5, y=0.5,
                          font=dict(size=15, color="white"), showarrow=False)],
        legend=dict(font=dict(size=9), orientation="v",
                    x=1.0, xanchor="left"),
        margin=dict(l=0, r=80, t=10, b=0),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:0.5rem">Top 8 Produtos</div>', unsafe_allow_html=True)
    prod = dff["produto"].value_counts().head(8).reset_index()
    prod.columns = ["Produto", "Qtd"]
    fig3 = go.Figure(go.Bar(
        x=prod["Produto"], y=prod["Qtd"],
        marker=dict(color=BLUE, line=dict(color="rgba(255,255,255,0.08)", width=1)),
        text=prod["Qtd"].apply(lambda x: f"{x:,}"),
        textposition="outside", textfont=dict(color=GRAY1, size=9),
    ))
    apply_plotly_theme(fig3)
    fig3.update_layout(height=220, xaxis=dict(tickangle=30, tickfont=dict(size=9)),
                       margin=dict(l=5, r=5, t=5, b=5))
    st.plotly_chart(fig3, use_container_width=True)

# ── Treemap ──────────────────────────────────────────────────
st.markdown('<div class="section-title">Treemap — Grupo × Categoria</div>', unsafe_allow_html=True)
top_grupos   = dff["grupo"].value_counts().head(12).index
dff_top      = dff[dff["grupo"].isin(top_grupos)]
treemap_data = (
    dff_top.groupby(["grupo", "categoria"]).size()
    .reset_index(name="qtd")
    .sort_values("qtd", ascending=False)
    .head(100)
)
fig4 = px.treemap(
    treemap_data, path=["grupo", "categoria"], values="qtd",
    color="qtd",
    color_continuous_scale=[[0, "#0d2d6e"], [0.4, BLUE], [0.75, CYAN], [1, "#ffffff"]],
)
fig4.update_traces(
    textfont=dict(color="white", size=11),
    marker=dict(line=dict(color=NAVY, width=2)),
    hovertemplate="<b>%{label}</b><br>Qtd: %{value:,}<extra></extra>",
)
apply_plotly_theme(fig4)
fig4.update_layout(
    height=380,
    coloraxis_colorbar=dict(
        tickfont=dict(color=GRAY2), title=dict(text="Qtd", font=dict(color=GRAY2))
    ),
)
st.plotly_chart(fig4, use_container_width=True)

# ── Playbooks ────────────────────────────────────────────────
st.markdown('<div class="section-title">Playbooks Sugeridos — Top 5 Padroes</div>', unsafe_allow_html=True)

playbooks = [
    ("Check Application Monitoring",  "28.728", BLUE,   "Verificar endpoint HTTPS; reiniciar servico de monitoramento; checar certificate expiry"),
    ("Free disk space < 10%",         "4.770",  ORANGE, "Limpar /tmp e logs antigos; alertar infra para expansao de volume"),
    ("Unavailable by ICMP ping",       "4.133",  CYAN,   "Verificar conectividade de rede; checar firewall e gateway; confirmar uptime do host"),
    ("Apache Busy Workers",            "3.925",  GREEN,  "Aumentar MaxRequestWorkers no httpd.conf; monitorar conexoes abertas"),
    ("Processor load is too high P3",  "2.174",  PURPLE, "Identificar processo responsavel; escalar recursos ou reiniciar servico"),
]

for i, (padrao, freq, cor, acao) in enumerate(playbooks, 1):
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-left:3px solid {cor};border-radius:10px;padding:0.8rem 1rem;
                margin-bottom:0.5rem;display:flex;align-items:flex-start;gap:1rem">
        <div style="background:{cor};color:#000;font-weight:800;font-size:0.85rem;
                    border-radius:6px;padding:0.2rem 0.5rem;min-width:24px;text-align:center">
            {i}
        </div>
        <div style="flex:1">
            <div style="color:#fff;font-weight:600;font-size:0.9rem">{padrao}
                <span style="color:{cor};font-size:0.75rem;margin-left:0.5rem">
                    {freq} ocorrencias
                </span>
            </div>
            <div style="color:{GRAY2};font-size:0.8rem;margin-top:0.25rem">{acao}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Distribuicao por hora ─────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:1rem">Distribuicao por Hora do Dia</div>', unsafe_allow_html=True)
hora_counts = dff["hora_abertura"].value_counts().sort_index().reset_index()
hora_counts.columns = ["Hora", "Qtd"]
fig5 = go.Figure(go.Bar(
    x=hora_counts["Hora"], y=hora_counts["Qtd"],
    marker=dict(
        color=hora_counts["Qtd"],
        colorscale=[[0, "#0d2d6e"], [1, CYAN]],
        showscale=False,
        line=dict(color="rgba(255,255,255,0.06)", width=1),
    ),
    text=hora_counts["Qtd"].apply(lambda x: f"{x:,}"),
    textposition="outside", textfont=dict(color=GRAY1, size=9),
))
apply_plotly_theme(fig5)
fig5.update_layout(
    height=240,
    xaxis=dict(dtick=1, tickfont=dict(size=9)),
    margin=dict(l=5, r=5, t=5, b=5),
)
st.plotly_chart(fig5, use_container_width=True)
