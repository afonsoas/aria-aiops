"""Pagina 6 — Simulacao em Tempo Real de Incidentes."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
import random
from datetime import datetime

st.set_page_config(page_title="Simulacao — ARIA", layout="wide", page_icon="⚡")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, apply_plotly_theme
from dashboard.utils.theme import BLUE, CYAN, ORANGE, GREEN, GRAY1, GRAY2, NAVY, PURPLE
from dashboard.utils.data_loader import load_data
from dashboard.utils.model_loader import load_models, predict_ola

inject_css()
df     = load_data()
models = load_models()
ola_bundle, _, encoders = models

# ── Distribuicoes do dataset real ─────────────────────────────
@st.cache_data
def _get_distributions():
    grupos    = df["grupo"].dropna().value_counts(normalize=True)
    produtos  = df["produto"].dropna().value_counts(normalize=True)
    cats      = df["categoria"].dropna().value_counts(normalize=True)
    subcats   = df["subcategoria"].dropna().value_counts(normalize=True)
    desc_pool = df["descricao"].dropna().sample(min(500, len(df))).tolist()
    return grupos, produtos, cats, subcats, desc_pool

grupos_dist, produtos_dist, cats_dist, subcats_dist, desc_pool = _get_distributions()

DESCRICOES = [
    "Problem: Check Application Monitoring",
    "Server not running - domain down",
    "Disk space critical on prod server",
    "SSL certificate expired",
    "Database connection timeout",
    "High CPU usage detected",
    "Memory leak in application",
    "Network latency spike",
    "API endpoint returning 500",
    "Scheduled task failed",
    "Backup job not completed",
    "Load balancer health check failed",
]

def _safe_encode(col, val):
    le = encoders.get(col)
    if le is None: return 0
    try: return int(le.transform([val])[0])
    except: return 0

def _gerar_incidente(i: int) -> dict:
    now = datetime.now()
    grupo    = np.random.choice(grupos_dist.index[:20],   p=(grupos_dist.values[:20]   / grupos_dist.values[:20].sum()))
    produto  = np.random.choice(produtos_dist.index[:20], p=(produtos_dist.values[:20] / produtos_dist.values[:20].sum()))
    cat      = np.random.choice(cats_dist.index[:20],     p=(cats_dist.values[:20]     / cats_dist.values[:20].sum()))
    subcat   = np.random.choice(subcats_dist.index[:20],  p=(subcats_dist.values[:20]  / subcats_dist.values[:20].sum()))
    prio_num = random.choices([2, 3, 4], weights=[13, 34, 53])[0]
    hora     = random.randint(0, 23)
    dia      = random.randint(0, 6)
    is_mon   = random.choices([0, 1], weights=[15, 85])[0]
    has_par  = random.choices([0, 1], weights=[70, 30])[0]
    descricao = random.choice(DESCRICOES + desc_pool[:20])

    row = {
        "prio_num":           prio_num,
        "hora_abertura":      hora,
        "dia_semana":         dia,
        "mes":                now.month,
        "is_monitoring":      is_mon,
        "has_parent":         has_par,
        "produto_enc":        _safe_encode("produto",      produto),
        "grupo_enc":          _safe_encode("grupo",        grupo),
        "categoria_enc":      _safe_encode("categoria",    cat),
        "subcategoria_enc":   _safe_encode("subcategoria", subcat),
        "cod_fechamento_enc": 0,
        "descricao":          descricao,
    }
    prob  = predict_ola(ola_bundle, row)
    pct   = prob * 100
    nivel = "ALTO" if pct >= 50 else ("MEDIO" if pct >= 25 else "BAIXO")

    prio_label = {2: "Alta", 3: "Media", 4: "Baixa"}.get(prio_num, str(prio_num))
    dia_label  = ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"][dia]

    return {
        "ID": f"INC{random.randint(100000,999999)}",
        "Hora": f"{hora:02d}:{random.randint(0,59):02d}",
        "Dia": dia_label,
        "Prioridade": prio_label,
        "Grupo": grupo,
        "Produto": produto,
        "Descricao": descricao[:45] + "...",
        "Monit.": "✅" if is_mon else "❌",
        "Risco %": f"{pct:.1f}%",
        "Nivel": nivel,
        "_prob": prob,
        "_nivel": nivel,
    }

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#1a0540 60%,#050e1f 100%);
            border:1px solid rgba(124,58,237,0.35);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#7C3AED,#00D4FF,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">⚡ Simulacao de Incidentes em Tempo Real</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      ARIA detecta riscos de violacao OLA conforme incidentes chegam
  </span>
</div>
""", unsafe_allow_html=True)

# ── Controles ────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 2])
with col_ctrl1:
    n_incidentes = st.number_input("Incidentes por rodada", 5, 50, 20, step=5)
with col_ctrl2:
    auto_loop = st.checkbox("Auto-refresh (3s)", value=False)
with col_ctrl3:
    st.markdown("<br>", unsafe_allow_html=True)
    gerar = st.button("⚡ Gerar Incidentes", use_container_width=True, type="primary")
with col_ctrl4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar", use_container_width=True):
        st.session_state.pop("sim_incidentes", None)
        st.session_state.pop("sim_historico", None)
        st.rerun()

# ── Gerar incidentes ─────────────────────────────────────────
if gerar or auto_loop:
    incidentes = [_gerar_incidente(i) for i in range(int(n_incidentes))]
    st.session_state["sim_incidentes"] = incidentes

    hist = st.session_state.get("sim_historico", [])
    hist.extend(incidentes)
    st.session_state["sim_historico"] = hist[-200:]  # manter ultimos 200

# ── Exibir resultado ─────────────────────────────────────────
if "sim_incidentes" in st.session_state:
    incidentes = st.session_state["sim_incidentes"]

    alto   = [i for i in incidentes if i["_nivel"] == "ALTO"]
    medio  = [i for i in incidentes if i["_nivel"] == "MEDIO"]
    baixo  = [i for i in incidentes if i["_nivel"] == "BAIXO"]

    # KPIs da rodada
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:900;color:{CYAN}">{len(incidentes)}</div>
            <div style="font-size:0.78rem;color:{GRAY2}">Total Analisados</div>
        </div>""", unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"""
        <div style="background:rgba(255,107,53,0.12);border:1px solid rgba(255,107,53,0.35);
                    border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:900;color:{ORANGE}">{len(alto)}</div>
            <div style="font-size:0.78rem;color:{GRAY2}">🔴 Alto Risco</div>
        </div>""", unsafe_allow_html=True)
    with col_k3:
        st.markdown(f"""
        <div style="background:rgba(243,156,18,0.10);border:1px solid rgba(243,156,18,0.3);
                    border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:900;color:#f39c12">{len(medio)}</div>
            <div style="font-size:0.78rem;color:{GRAY2}">🟠 Medio Risco</div>
        </div>""", unsafe_allow_html=True)
    with col_k4:
        st.markdown(f"""
        <div style="background:rgba(0,200,122,0.10);border:1px solid rgba(0,200,122,0.3);
                    border-radius:10px;padding:1rem;text-align:center">
            <div style="font-size:2rem;font-weight:900;color:{GREEN}">{len(baixo)}</div>
            <div style="font-size:0.78rem;color:{GRAY2}">🟢 Baixo Risco</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_tabela, col_graficos = st.columns([3, 2], gap="large")

    with col_tabela:
        st.markdown(f'<div class="section-title">Incidentes da Rodada Atual</div>', unsafe_allow_html=True)

        # Colunas fixas — evita quebra de linha nas células
        COLS = "88px 44px 36px 52px 110px 44px 60px 68px"
        CELL = "overflow:hidden;white-space:nowrap;text-overflow:ellipsis"

        rows_html = ""
        for inc in sorted(incidentes, key=lambda x: x["_prob"], reverse=True):
            nivel = inc["_nivel"]
            if nivel == "ALTO":
                bg = "rgba(255,107,53,0.12)"; badge_bg = "#FF6B35"; badge_c = "#fff"
                border_l = "3px solid #FF6B35"
            elif nivel == "MEDIO":
                bg = "rgba(243,156,18,0.08)"; badge_bg = "#f39c12"; badge_c = "#000"
                border_l = "3px solid #f39c12"
            else:
                bg = "rgba(0,200,122,0.06)"; badge_bg = "#00C87A"; badge_c = "#000"
                border_l = "3px solid #00C87A"

            badge = (f'<span style="background:{badge_bg};color:{badge_c};padding:1px 6px;'
                     f'border-radius:10px;font-size:0.70rem;font-weight:700;white-space:nowrap">'
                     f'{nivel}</span>')
            desc  = inc["Descricao"][:30]
            grupo = inc["Grupo"][:14]

            rows_html += f"""
            <div style="background:{bg};border-left:{border_l};border-radius:6px;
                        padding:0.35rem 0.6rem;margin-bottom:0.3rem;overflow:hidden;
                        display:grid;grid-template-columns:{COLS};
                        gap:0.35rem;align-items:center;font-size:0.76rem;height:32px">
                <span style="{CELL};color:{GRAY2};font-family:monospace" title="{inc['ID']}">{inc['ID']}</span>
                <span style="{CELL};color:{GRAY1}">{inc['Hora']}</span>
                <span style="{CELL};color:{GRAY2}">{inc['Dia']}</span>
                <span style="{CELL};color:{GRAY1}">{inc['Prioridade']}</span>
                <span style="{CELL};color:{GRAY1}" title="{inc['Grupo']}">{grupo}</span>
                <span style="{CELL};text-align:center">{inc['Monit.']}</span>
                <span style="{CELL};color:#fff;font-weight:700;text-align:right">{inc['Risco %']}</span>
                <span style="text-align:right">{badge}</span>
            </div>"""

        # Header alinhado com as mesmas colunas
        header = f"""
        <div style="display:grid;grid-template-columns:{COLS};
                    gap:0.35rem;padding:0.25rem 0.6rem;margin-bottom:0.2rem;
                    font-size:0.70rem;color:{GRAY2};font-weight:600;letter-spacing:0.03em">
            <span>ID</span><span>Hora</span><span>Dia</span><span>Prio</span>
            <span>Grupo</span><span>Mon</span>
            <span style="text-align:right">Risco</span><span style="text-align:right">Nivel</span>
        </div>"""
        st.markdown(header + rows_html, unsafe_allow_html=True)

    with col_graficos:
        st.markdown(f'<div class="section-title">Distribuicao de Risco</div>', unsafe_allow_html=True)

        # Pizza de risco
        fig_pie = go.Figure(go.Pie(
            labels=["Alto", "Medio", "Baixo"],
            values=[len(alto), len(medio), len(baixo)],
            marker=dict(colors=[ORANGE, "#f39c12", GREEN]),
            hole=0.55,
            textinfo="label+percent",
            textfont=dict(color=GRAY1, size=11),
        ))
        apply_plotly_theme(fig_pie)
        fig_pie.update_layout(
            height=220, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        # Historico acumulado
        if "sim_historico" in st.session_state and len(st.session_state["sim_historico"]) > 20:
            hist = st.session_state["sim_historico"]
            st.markdown(f'<div class="section-title" style="margin-top:0.5rem">Historico Acumulado</div>', unsafe_allow_html=True)
            chunk = 10
            h_alto  = [sum(1 for x in hist[i:i+chunk] if x["_nivel"]=="ALTO")   for i in range(0,len(hist),chunk)]
            h_medio = [sum(1 for x in hist[i:i+chunk] if x["_nivel"]=="MEDIO")  for i in range(0,len(hist),chunk)]
            h_baixo = [sum(1 for x in hist[i:i+chunk] if x["_nivel"]=="BAIXO")  for i in range(0,len(hist),chunk)]
            x_axis  = [f"Rodada {i+1}" for i in range(len(h_alto))]

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Bar(name="Alto",  x=x_axis, y=h_alto,  marker_color=ORANGE))
            fig_hist.add_trace(go.Bar(name="Medio", x=x_axis, y=h_medio, marker_color="#f39c12"))
            fig_hist.add_trace(go.Bar(name="Baixo", x=x_axis, y=h_baixo, marker_color=GREEN))
            apply_plotly_theme(fig_hist)
            fig_hist.update_layout(
                barmode="stack", height=200,
                margin=dict(l=0, r=0, t=10, b=30),
                legend=dict(orientation="h", y=-0.15),
                xaxis=dict(showticklabels=len(x_axis) <= 10),
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

    # Auto-refresh
    if auto_loop:
        time.sleep(3)
        st.rerun()

else:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px dashed rgba(124,58,237,0.3);
                border-radius:14px;padding:3rem;text-align:center;margin-top:1rem">
        <div style="font-size:3.5rem;margin-bottom:1rem">⚡</div>
        <div style="color:{GRAY1};font-size:1.1rem;font-weight:600">Sistema pronto para simulacao</div>
        <div style="color:{GRAY2};font-size:0.85rem;margin-top:0.5rem">
            Clique em "Gerar Incidentes" para ver o ARIA analisando<br>
            incidentes em tempo real com predicao de risco OLA.
        </div>
        <div style="margin-top:1.5rem;display:flex;justify-content:center;gap:2rem;font-size:0.82rem;color:{GRAY2}">
            <span>📊 Baseado em distribuicoes reais do dataset Locaweb</span>
            <span>🤖 Modelo XGBoost + SMOTE</span>
            <span>⚡ Predicao instantanea</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
