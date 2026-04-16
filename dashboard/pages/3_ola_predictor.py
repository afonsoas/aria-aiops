"""Pagina 3 — Preditor de Violacao OLA."""
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Preditor OLA — ARIA", layout="wide", page_icon="🔮")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme, section_title
from dashboard.utils.theme import BLUE, CYAN, ORANGE, GREEN, PURPLE, GRAY1, GRAY2, NAVY, NAVY2
from dashboard.utils.data_loader import load_data
from dashboard.utils.model_loader import load_models, predict_ola

inject_css()
df     = load_data()
models = load_models()
ola_bundle, prio_bundle, encoders = models

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#0d2d6e 60%,#050e1f 100%);
            border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#00C87A,#105BD8,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">🔮 Preditor de Violacao OLA</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      Modelo A: XGBoost + SMOTE &nbsp;·&nbsp; ROC-AUC 0.84 &nbsp;·&nbsp; Recall 60%
  </span>
</div>
""", unsafe_allow_html=True)

col_form, col_result = st.columns([1, 1], gap="large")

# ── Formulario ───────────────────────────────────────────────
with col_form:
    st.markdown('<div class="section-title">Dados do Incidente</div>', unsafe_allow_html=True)

    with st.form("predict_form"):
        prio      = st.selectbox("Prioridade", ["2 - Alta", "3 - Media", "4 - Baixa"])
        col_fa, col_fb = st.columns(2)
        with col_fa:
            produto   = st.selectbox("Produto", sorted(df["produto"].dropna().unique()))
            categoria = st.selectbox("Categoria", sorted(df["categoria"].dropna().unique()))
        with col_fb:
            grupo     = st.selectbox("Grupo designado", sorted(df["grupo"].dropna().unique()))
            subcateg  = st.selectbox("Subcategoria", sorted(df["subcategoria"].dropna().unique()))

        col_fc, col_fd = st.columns(2)
        with col_fc:
            hora = st.slider("Hora de abertura", 0, 23, 10)
        with col_fd:
            dia = st.selectbox("Dia da semana",
                ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"])

        descricao = st.text_area("Descricao resumida",
            "Problem: Check Application Monitoring", height=80)

        col_fe, col_ff = st.columns(2)
        with col_fe:
            is_mon  = st.checkbox("Aberto por Monitoramento", value=True)
        with col_ff:
            has_par = st.checkbox("Tem Incidente Pai", value=False)

        cod_fech_opts = ["(não informado)"] + sorted(df["cod_fechamento"].dropna().astype(str).unique())
        cod_fech = st.selectbox("Código de Fechamento (opcional)", cod_fech_opts)

        submitted = st.form_submit_button("🔮  PREDIZER RISCO OLA", use_container_width=True)

# ── Resultado ────────────────────────────────────────────────
with col_result:
    st.markdown('<div class="section-title">Resultado da Predicao</div>', unsafe_allow_html=True)

    if submitted:
        prio_num = int(prio.strip()[0])
        dia_num  = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"].index(dia)

        def safe_encode(enc_dict, col, val):
            le = enc_dict.get(col)
            if le is None: return 0
            try:   return int(le.transform([val])[0])
            except: return 0

        import datetime as _dt
        row = {
            "prio_num":           prio_num,
            "hora_abertura":      hora,
            "dia_semana":         dia_num,
            "mes":                _dt.date.today().month,
            "is_monitoring":      int(is_mon),
            "has_parent":         int(has_par),
            "produto_enc":        safe_encode(encoders, "produto",        produto),
            "grupo_enc":          safe_encode(encoders, "grupo",          grupo),
            "categoria_enc":      safe_encode(encoders, "categoria",      categoria),
            "subcategoria_enc":   safe_encode(encoders, "subcategoria",   subcateg),
            "cod_fechamento_enc": safe_encode(encoders, "cod_fechamento",
                                  cod_fech if cod_fech != "(não informado)" else None),
            "descricao":          descricao,
        }

        prob = predict_ola(ola_bundle, row)
        pct  = prob * 100

        if pct >= 50:
            cor, nivel, emoji = ORANGE, "ALTO RISCO", "🔴"
            bg_grad = "linear-gradient(135deg,rgba(255,107,53,0.18),rgba(255,107,53,0.06))"
            border  = "rgba(255,107,53,0.5)"
        elif pct >= 25:
            cor, nivel, emoji = "#f39c12", "RISCO MEDIO", "🟠"
            bg_grad = "linear-gradient(135deg,rgba(243,156,18,0.15),rgba(243,156,18,0.05))"
            border  = "rgba(243,156,18,0.45)"
        else:
            cor, nivel, emoji = GREEN, "BAIXO RISCO", "🟢"
            bg_grad = "linear-gradient(135deg,rgba(0,200,122,0.15),rgba(0,200,122,0.05))"
            border  = "rgba(0,200,122,0.45)"

        # Card principal do resultado
        st.markdown(f"""
        <div style="background:{bg_grad};border:1px solid {border};border-radius:14px;
                    padding:1.5rem;text-align:center;margin-bottom:1rem">
            <div style="font-size:3.5rem;font-weight:900;color:{cor};
                        line-height:1;letter-spacing:-2px">{pct:.1f}%</div>
            <div style="font-size:1rem;font-weight:700;color:{cor};
                        margin-top:0.4rem;letter-spacing:1px">{emoji} {nivel}</div>
            <div style="font-size:0.78rem;color:{GRAY2};margin-top:0.4rem">
                Probabilidade de violar OLA
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge Plotly
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number=dict(suffix="%", font=dict(color=cor, size=28)),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=GRAY2,
                          tickfont=dict(color=GRAY2, size=10)),
                bar=dict(color=cor, thickness=0.25),
                bgcolor="rgba(255,255,255,0.04)",
                bordercolor="rgba(255,255,255,0.1)",
                steps=[
                    dict(range=[0, 25],  color="rgba(0,200,122,0.15)"),
                    dict(range=[25, 50], color="rgba(243,156,18,0.15)"),
                    dict(range=[50, 100],color="rgba(255,107,53,0.15)"),
                ],
                threshold=dict(line=dict(color=cor, width=3), thickness=0.75, value=pct),
            ),
        ))
        apply_plotly_theme(fig_g)
        fig_g.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_g, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})

        # Feature importance
        st.markdown(f'<div class="section-title" style="margin-top:0.5rem">Fatores do Modelo</div>', unsafe_allow_html=True)
        feat_names  = ola_bundle["features"] + ola_bundle["tfidf"].get_feature_names_out().tolist()
        importances = ola_bundle["model"].feature_importances_
        top6 = sorted(zip(feat_names, importances), key=lambda x: x[1], reverse=True)[:6]
        max_imp = max(v for _, v in top6) or 1.0

        feats_html = ""
        for fname, fimp in top6:
            pct_bar = fimp / max_imp * 100
            feats_html += f"""
            <div style="margin-bottom:0.5rem">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.78rem;color:{GRAY1};margin-bottom:3px">
                <span>{fname}</span><span style="color:{CYAN}">{fimp:.3f}</span>
              </div>
              <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:6px">
                <div style="background:linear-gradient(90deg,{BLUE},{CYAN});
                            width:{pct_bar:.0f}%;height:6px;border-radius:4px"></div>
              </div>
            </div>"""
        st.markdown(feats_html, unsafe_allow_html=True)

        # Recomendacao
        st.markdown("<br>", unsafe_allow_html=True)
        if pct >= 50:
            st.error(f"**Acao imediata:** Escalar para {grupo}. Prioridade {prio} com alto risco de exceder OLA.")
        elif pct >= 25:
            st.warning("**Monitorar:** Acionar time se nao houver resposta em 30 min.")
        else:
            st.success("**Normal:** Incidente dentro do padrao. Seguir fluxo standard.")

    else:
        # Estado vazio estilizado
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.12);
                    border-radius:14px;padding:2.5rem;text-align:center;margin-top:1rem">
            <div style="font-size:3rem;margin-bottom:1rem">🔮</div>
            <div style="color:{GRAY1};font-size:1rem;font-weight:600">
                Preencha o formulario ao lado
            </div>
            <div style="color:{GRAY2};font-size:0.82rem;margin-top:0.5rem">
                O modelo retornara a probabilidade de violacao OLA<br>
                com base nas features do incidente informado.
            </div>
        </div>
        <br>
        <div style="background:rgba(16,91,216,0.1);border:1px solid rgba(16,91,216,0.25);
                    border-radius:10px;padding:1rem;font-size:0.82rem;color:{GRAY2}">
            <div style="color:{CYAN};font-weight:600;margin-bottom:0.5rem">Sobre o Modelo A</div>
            &bull; XGBoost com SMOTE (balanceamento da classe minoritaria)<br>
            &bull; ROC-AUC: <b style="color:{GRAY1}">0.84</b> &nbsp;·&nbsp;
               Recall: <b style="color:{GRAY1}">60%</b><br>
            &bull; Treinado em 20.480 incidentes elegíveis para KPI<br>
            &bull; Features: prioridade, hora, grupo, produto, categoria, descricao (TF-IDF)
        </div>
        """, unsafe_allow_html=True)
