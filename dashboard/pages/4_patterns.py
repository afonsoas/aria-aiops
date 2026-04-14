"""Pagina 4 — Padroes Recorrentes."""
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Padroes — ARIA", layout="wide", page_icon="🔍")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.data_loader import load_data, NAVY, BLUE, CYAN, ORANGE, GREEN

df = load_data()

st.title("🔍 Padroes Recorrentes")
st.caption("Top incidentes por frequencia, treemap por categoria e playbooks sugeridos")

with st.sidebar:
    st.header("Filtros")
    anos = sorted(df["ano"].dropna().astype(int).unique(), reverse=True)
    sel_anos = st.multiselect("Ano", anos, default=anos)
    top_n = st.slider("Top N descricoes", 5, 30, 20)

dff = df[df["ano"].isin(sel_anos)]

col_a, col_b = st.columns([1.2, 1])

# Top N descricoes
with col_a:
    st.subheader(f"Top {top_n} Descricoes mais Frequentes")
    top_desc = dff["descricao"].value_counts().head(top_n).reset_index()
    top_desc.columns = ["Descricao", "Qtd"]
    top_desc["Descricao_curta"] = top_desc["Descricao"].str[:60] + "..."
    fig = px.bar(top_desc.sort_values("Qtd"), x="Qtd", y="Descricao_curta",
                 orientation="h", color="Qtd",
                 color_continuous_scale=[[0, CYAN], [0.5, BLUE], [1, NAVY]],
                 text="Qtd")
    fig.update_layout(
        plot_bgcolor="white",
        yaxis_title="",
        xaxis_title="Frequencia",
        height=500,
        coloraxis_showscale=False,
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Top grupos
with col_b:
    st.subheader("Volume por Grupo")
    grp = dff["grupo"].value_counts().head(10).reset_index()
    grp.columns = ["Grupo", "Qtd"]
    fig2 = px.pie(grp, names="Grupo", values="Qtd",
                  color_discrete_sequence=[BLUE, ORANGE, GREEN, CYAN, NAVY,
                                           "#7C3AED","#E74C3C","#F1C40F","#1ABC9C","#95A5A6"])
    fig2.update_layout(height=300, legend_title="Grupo")
    st.plotly_chart(fig2, use_container_width=True)

    # Top produtos
    st.subheader("Top 8 Produtos")
    prod = dff["produto"].value_counts().head(8).reset_index()
    prod.columns = ["Produto", "Qtd"]
    fig3 = px.bar(prod, x="Produto", y="Qtd",
                  color_discrete_sequence=[BLUE], text="Qtd")
    fig3.update_layout(plot_bgcolor="white", height=250,
                       xaxis=dict(tickangle=30))
    fig3.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

# Treemap categoria x grupo
st.subheader("Treemap — Categoria x Grupo (Top 15 grupos)")
top_grupos = dff["grupo"].value_counts().head(15).index
dff_top = dff[dff["grupo"].isin(top_grupos)]
treemap_data = (
    dff_top.groupby(["grupo", "categoria"]).size()
    .reset_index(name="qtd")
    .sort_values("qtd", ascending=False)
    .head(80)
)
fig4 = px.treemap(treemap_data, path=["grupo", "categoria"], values="qtd",
                  color="qtd",
                  color_continuous_scale=[[0, CYAN], [0.5, BLUE], [1, NAVY]])
fig4.update_layout(height=400)
st.plotly_chart(fig4, use_container_width=True)

# Playbooks automaticos
st.subheader("Playbooks Sugeridos — Top 5 Incidentes")
st.markdown("""
| # | Padrao | Frequencia | Acao Recomendada |
|---|--------|-----------|-----------------|
| 1 | **Check Application Monitoring** | 28.728 | Verificar endpoint HTTPS; reiniciar servico de monitoramento; checar certificate expiry |
| 2 | **Free disk space < 10%** | 4.770 | Limpar /tmp e logs antigos; alertar infra para expansao de volume |
| 3 | **Check Application Monitoring VIP** | 4.281 | Verificar VIP load balancer; checar health dos nodes |
| 4 | **Unavailable by ICMP ping** | 4.133 | Verificar conectividade de rede; checar firewall e gateway; confirmar uptime do host |
| 5 | **Apache Busy Workers** | 3.925 | Aumentar MaxRequestWorkers no httpd.conf; monitorar conexoes abertas |
""")

# Tendencia por hora
st.subheader("Distribuicao de Abertura por Hora do Dia")
hora_counts = dff["hora_abertura"].value_counts().sort_index().reset_index()
hora_counts.columns = ["Hora", "Qtd"]
fig5 = px.bar(hora_counts, x="Hora", y="Qtd",
              color_discrete_sequence=[CYAN], text="Qtd")
fig5.update_layout(plot_bgcolor="white", xaxis=dict(dtick=1))
fig5.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig5, use_container_width=True)
