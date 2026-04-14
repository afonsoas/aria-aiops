"""Pagina 3 — Preditor de Violacao OLA."""
import streamlit as st
import numpy as np

st.set_page_config(page_title="Preditor OLA — ARIA", layout="wide", page_icon="🔮")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.data_loader import load_data, ORANGE, GREEN, BLUE, CYAN
from dashboard.utils.model_loader import load_models, predict_ola

df     = load_data()
models = load_models()
ola_bundle, prio_bundle, encoders = models

st.title("🔮 Preditor de Violacao OLA")
st.caption("Insira os dados de um novo incidente para obter a probabilidade de violacao de OLA")

col_form, col_result = st.columns([1, 1])

with col_form:
    st.subheader("Dados do Incidente")
    with st.form("predict_form"):
        prio       = st.selectbox("Prioridade", ["2 - Alta", "3 - Media", "4 - Baixa"])
        produto    = st.selectbox("Produto", sorted(df["produto"].unique()))
        grupo      = st.selectbox("Grupo designado", sorted(df["grupo"].unique()))
        categoria  = st.selectbox("Categoria", sorted(df["categoria"].unique()))
        subcateg   = st.selectbox("Subcategoria", sorted(df["subcategoria"].unique()))
        hora       = st.slider("Hora de abertura", 0, 23, 10)
        dia        = st.selectbox("Dia da semana", ["Segunda", "Terca", "Quarta",
                                                     "Quinta", "Sexta", "Sabado", "Domingo"])
        descricao  = st.text_area("Descricao resumida",
            "Problem: Check Application Monitoring", height=80)
        is_mon     = st.checkbox("Aberto por Monitoramento", value=True)
        has_par    = st.checkbox("Tem Incidente Pai", value=False)
        submitted  = st.form_submit_button("PREDIZER RISCO OLA", type="primary")

with col_result:
    st.subheader("Resultado")

    if submitted:
        prio_num = int(prio.strip()[0])
        dia_num  = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"].index(dia)

        def safe_encode(enc_dict, col, val):
            le = enc_dict.get(col)
            if le is None:
                return 0
            try:
                return int(le.transform([val])[0])
            except Exception:
                return 0

        row = {
            "prio_num":            prio_num,
            "hora_abertura":       hora,
            "dia_semana":          dia_num,
            "mes":                 6,
            "is_monitoring":       int(is_mon),
            "has_parent":          int(has_par),
            "produto_enc":         safe_encode(encoders, "produto", produto),
            "grupo_enc":           safe_encode(encoders, "grupo", grupo),
            "categoria_enc":       safe_encode(encoders, "categoria", categoria),
            "subcategoria_enc":    safe_encode(encoders, "subcategoria", subcateg),
            "cod_fechamento_enc":  0,
            "descricao":           descricao,
        }

        prob = predict_ola(ola_bundle, row)
        pct  = prob * 100

        if pct >= 50:
            cor, nivel, emoji = ORANGE, "ALTO RISCO", "🔴"
        elif pct >= 25:
            cor, nivel, emoji = "#FFC300", "RISCO MEDIO", "🟠"
        else:
            cor, nivel, emoji = GREEN, "BAIXO RISCO", "🟢"

        st.markdown(f"""
        <div style="background:#FFF;border-radius:8px;padding:1.5rem;border-top:5px solid {cor}">
            <div style="font-size:3rem;font-weight:700;color:{cor};text-align:center">{pct:.1f}%</div>
            <div style="text-align:center;font-size:1.2rem;color:{cor};font-weight:600;margin-top:0.5rem">
                {emoji} {nivel}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Barra de risco
        st.markdown("**Indicador de risco:**")
        progress_html = f"""
        <div style="background:#EEE;border-radius:4px;height:20px;width:100%">
            <div style="background:{cor};width:{min(pct,100):.1f}%;height:20px;border-radius:4px"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#888;margin-top:3px">
            <span>0%</span><span>Baixo</span><span>Medio</span><span>Alto</span><span>100%</span>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Fatores mais relevantes (modelo):**")
        feat_names = ola_bundle["features"] + ola_bundle["tfidf"].get_feature_names_out().tolist()
        importances = ola_bundle["model"].feature_importances_
        top = sorted(zip(feat_names, importances), key=lambda x: x[1], reverse=True)[:6]
        max_imp = max(fimp for _, fimp in top) or 1.0
        for fname, fimp in top:
            st.progress(float(fimp / max_imp), text=f"{fname}  ({fimp:.3f})")

        st.markdown("---")
        if pct >= 50:
            st.warning(f"**Recomendacao:** Escalar para {grupo} imediatamente. "
                       f"Prioridade {prio} com alto risco de exceder OLA.")
        elif pct >= 25:
            st.info("**Recomendacao:** Monitorar de perto. Acionar time se nao houver resposta em 30min.")
        else:
            st.success("**Recomendacao:** Incidente dentro do padrao. Seguir fluxo normal.")
    else:
        st.info("Preencha o formulario e clique em **PREDIZER RISCO OLA**.")
        st.markdown("""
        **Sobre o Modelo A:**
        - Algoritmo: XGBoost com SMOTE
        - ROC-AUC: 0.84 | Recall: 60%
        - Treinado em 20.480 incidentes (2023-2025)
        - Metricas priorizadas: Recall (capturar o maximo de violacoes iminentes)
        """)
