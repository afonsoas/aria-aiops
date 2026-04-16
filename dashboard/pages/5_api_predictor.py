"""Pagina 5 — API Predictor: chama a API REST e exibe historico do banco."""
import os
import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="API Predictor — ARIA", layout="wide", page_icon="🚀")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme, section_title
from dashboard.utils.theme import BLUE, CYAN, ORANGE, GREEN, PURPLE, GRAY1, GRAY2, NAVY
from dashboard.utils.data_loader import load_data

import plotly.graph_objects as go

inject_css()
df = load_data()

# ── Config da API — lê secrets.toml (Streamlit Cloud) ou env var ou input manual ─
_default_api = (
    st.secrets.get("ARIA_API_URL", None)
    if hasattr(st, "secrets") and "ARIA_API_URL" in st.secrets
    else os.getenv("ARIA_API_URL", "http://localhost:8000")
)
API_BASE = st.sidebar.text_input("URL da API", _default_api)

with st.sidebar:
    st.markdown(f'<div style="color:{CYAN};font-size:1.1rem;font-weight:700;margin-bottom:0.5rem">⚙️ Conexao API</div>', unsafe_allow_html=True)
    if st.button("🔄 Testar /health"):
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3)
            data = r.json()
            if data.get("modelos_carregados"):
                st.success("API Online — Modelos carregados")
            else:
                st.warning("API respondeu mas modelos nao carregados")
            st.json(data)
        except Exception as e:
            st.error(f"Sem conexao: {e}")

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#050e1f 0%,#0d2d6e 60%,#050e1f 100%);
            border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:1rem 1.5rem;
            margin-bottom:1rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,#7C3AED,#00C87A,transparent)"></div>
  <span style="color:#fff;font-size:1.25rem;font-weight:700">🚀 API Predictor — Sprint 3 MVP</span>
  <span style="color:#8899bb;font-size:0.82rem;margin-left:1rem">
      FastAPI REST &nbsp;·&nbsp; Oracle ADB &nbsp;·&nbsp; Historico de predicoes
  </span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔮 Predizer via API", "📜 Historico (DB)", "📡 Documentacao"])

# ── Tab 1: Predicao via API ───────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Enviar Incidente para a API</div>', unsafe_allow_html=True)
    col_form, col_res = st.columns([1, 1], gap="large")

    with col_form:
        with st.form("api_form"):
            numero    = st.text_input("Numero do Incidente (opcional)", placeholder="INC0012345")
            prio      = st.selectbox("Prioridade", ["2 - Alta", "3 - Media", "4 - Baixa"])
            col_a, col_b = st.columns(2)
            with col_a:
                produto   = st.selectbox("Produto", sorted(df["produto"].dropna().unique()))
                categoria = st.selectbox("Categoria", sorted(df["categoria"].dropna().unique()))
            with col_b:
                grupo     = st.selectbox("Grupo", sorted(df["grupo"].dropna().unique()))
                subcateg  = st.selectbox("Subcategoria", sorted(df["subcategoria"].dropna().unique()))

            col_c, col_d = st.columns(2)
            with col_c:
                hora = st.slider("Hora", 0, 23, 10)
            with col_d:
                dia  = st.selectbox("Dia da Semana",
                    ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"])

            descricao    = st.text_area("Descricao", "Problem: Check Application Monitoring", height=70)
            is_mon       = st.checkbox("Monitoramento automatico", True)
            has_par      = st.checkbox("Tem Incidente Pai", False)
            endpoint_sel = st.radio("Endpoint", ["/predict/ola", "/predict/priority"], horizontal=True)
            submitted    = st.form_submit_button("🚀 ENVIAR PARA API", use_container_width=True)

    with col_res:
        st.markdown('<div class="section-title">Resposta da API</div>', unsafe_allow_html=True)

        if submitted:
            prio_num = int(prio.strip()[0])
            dia_num  = ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado","Domingo"].index(dia)

            import datetime as _dt
            payload = {
                "prio_num":           prio_num,
                "hora_abertura":      hora,
                "dia_semana":         dia_num,
                "mes":                _dt.date.today().month,
                "is_monitoring":      int(is_mon),
                "has_parent":         int(has_par),
                "produto_enc":        0,
                "grupo_enc":          0,
                "categoria_enc":      0,
                "subcategoria_enc":   0,
                "cod_fechamento_enc": 0,
                "descricao":          descricao,
                "numero":             numero or None,
                "produto":            produto,
                "grupo":              grupo,
                "categoria":          categoria,
                "subcategoria":       subcateg,
            }

            try:
                r = requests.post(f"{API_BASE}{endpoint_sel}", json=payload, timeout=10)
                r.raise_for_status()
                data = r.json()

                if endpoint_sel == "/predict/ola":
                    pct_val = float(data["probabilidade"]) * 100
                    nivel   = data["nivel_risco"]
                    cor_map = {"ALTO": ORANGE, "MEDIO": "#f39c12", "BAIXO": GREEN}
                    cor = cor_map.get(nivel, BLUE)

                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border:1px solid {cor};
                                border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1rem">
                        <div style="font-size:3rem;font-weight:900;color:{cor};line-height:1">{data['percentual']}</div>
                        <div style="font-size:1rem;font-weight:700;color:{cor};margin-top:0.4rem">{nivel}</div>
                        <div style="font-size:0.78rem;color:{GRAY2};margin-top:0.3rem">Probabilidade de violar OLA</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Gauge
                    fig_g = go.Figure(go.Indicator(
                        mode="gauge+number", value=pct_val,
                        number=dict(suffix="%", font=dict(color=cor, size=24)),
                        gauge=dict(
                            axis=dict(range=[0, 100], tickfont=dict(color=GRAY2, size=9)),
                            bar=dict(color=cor, thickness=0.25),
                            bgcolor="rgba(255,255,255,0.04)",
                            steps=[
                                dict(range=[0, 25],   color="rgba(0,200,122,0.12)"),
                                dict(range=[25, 50],  color="rgba(243,156,18,0.12)"),
                                dict(range=[50, 100], color="rgba(255,107,53,0.12)"),
                            ],
                        ),
                    ))
                    apply_plotly_theme(fig_g)
                    fig_g.update_layout(height=180, margin=dict(l=20, r=20, t=5, b=5))
                    st.plotly_chart(fig_g, use_container_width=True)

                    st.info(f"**Recomendacao:** {data['recomendacao']}")

                else:  # /predict/priority
                    prio_pred = data["prioridade_predita"]
                    label     = data["label"]
                    cor_prio  = {1: "#e74c3c", 2: ORANGE, 3: BLUE, 4: GREEN, 5: CYAN}.get(prio_pred, BLUE)
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border:1px solid {cor_prio};
                                border-radius:14px;padding:1.5rem;text-align:center">
                        <div style="font-size:3rem;font-weight:900;color:{cor_prio};line-height:1">P{prio_pred}</div>
                        <div style="font-size:1rem;color:{cor_prio};margin-top:0.4rem">{label}</div>
                        <div style="font-size:0.78rem;color:{GRAY2};margin-top:0.3rem">Prioridade predita pelo modelo</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Raw JSON
                with st.expander("JSON completo"):
                    st.json(data)

            except requests.exceptions.ConnectionError:
                st.error(f"Nao foi possivel conectar a {API_BASE}. A API esta rodando?")
                st.info("Inicie a API com: `uvicorn api.main:app --reload`")
            except requests.exceptions.HTTPError as e:
                st.error(f"Erro HTTP {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")
        else:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.12);
                        border-radius:14px;padding:2.5rem;text-align:center">
                <div style="font-size:3rem;margin-bottom:0.8rem">🚀</div>
                <div style="color:{GRAY1};font-size:0.95rem;font-weight:600">Preencha o formulario e envie para a API</div>
                <div style="color:{GRAY2};font-size:0.8rem;margin-top:0.5rem">
                    A API FastAPI deve estar rodando localmente ou no OCI
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 2: Historico do banco ─────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Historico de Predicoes OLA (Oracle ADB)</div>', unsafe_allow_html=True)

    col_btn, col_lim = st.columns([1, 3])
    with col_btn:
        refresh = st.button("🔄 Atualizar historico", use_container_width=True)
    with col_lim:
        lim = st.slider("Ultimas N predicoes", 10, 500, 100)

    if refresh or True:
        try:
            r = requests.get(f"{API_BASE}/predictions/ola?limit={lim}", timeout=5)
            r.raise_for_status()
            preds = r.json()

            if not preds:
                st.info("Nenhuma predicao encontrada. Envie incidentes via aba 'Predizer via API' ou a API pode estar offline.")
            else:
                hist_df = pd.DataFrame(preds)

                # KPIs
                c1, c2, c3 = st.columns(3)
                total   = len(hist_df)
                n_alto  = (hist_df["nivel_risco"] == "ALTO").sum()  if "nivel_risco" in hist_df else 0
                avg_prob = hist_df["probabilidade"].mean() * 100 if "probabilidade" in hist_df else 0
                with c1: st.markdown(kpi_card(f"{total}", "Total Predicoes", "no periodo", BLUE), unsafe_allow_html=True)
                with c2: st.markdown(kpi_card(f"{n_alto}", "Alto Risco", "ALTO nivel", ORANGE), unsafe_allow_html=True)
                with c3: st.markdown(kpi_card(f"{avg_prob:.1f}%", "Prob Media", "de violacao", CYAN), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Grafico distribuicao de risco
                if "nivel_risco" in hist_df.columns:
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.markdown('<div class="section-title">Distribuicao de Risco</div>', unsafe_allow_html=True)
                        risco_cnt = hist_df["nivel_risco"].value_counts()
                        ordem = ["ALTO", "MEDIO", "BAIXO"]
                        vals  = [risco_cnt.get(r, 0) for r in ordem]
                        cors  = [ORANGE, "#f39c12", GREEN]
                        fig_r = go.Figure(go.Bar(
                            x=ordem, y=vals, marker=dict(color=cors),
                            text=vals, textposition="outside",
                            textfont=dict(color=GRAY1, size=11),
                            cliponaxis=False,
                        ))
                        apply_plotly_theme(fig_r)
                        fig_r.update_layout(height=240, showlegend=False,
                                            margin=dict(l=5, r=5, t=30, b=5),
                                            yaxis=dict(range=[0, max(vals or [1]) * 1.3]))
                        st.plotly_chart(fig_r, use_container_width=True)

                    with col_g2:
                        st.markdown('<div class="section-title">Probabilidade ao Longo do Tempo</div>', unsafe_allow_html=True)
                        if "criado_em" in hist_df.columns:
                            hist_df["criado_em"] = pd.to_datetime(hist_df["criado_em"])
                            hist_sorted = hist_df.sort_values("criado_em").tail(50)
                            fig_t = go.Figure(go.Scatter(
                                x=hist_sorted["criado_em"],
                                y=hist_sorted["probabilidade"] * 100,
                                mode="lines+markers",
                                line=dict(color=CYAN, width=2),
                                marker=dict(size=5, color=CYAN),
                                fill="tozeroy",
                                fillcolor="rgba(0,212,255,0.07)",
                            ))
                            apply_plotly_theme(fig_t)
                            fig_t.update_layout(
                                height=240, yaxis_title="Probabilidade (%)",
                                yaxis=dict(range=[0, 105]),
                                margin=dict(l=10, r=10, t=10, b=30),
                            )
                            st.plotly_chart(fig_t, use_container_width=True)

                # Tabela
                st.markdown('<div class="section-title">Tabela Detalhada</div>', unsafe_allow_html=True)
                display_cols = [c for c in ["numero","prio_num","hora_abertura","grupo",
                                             "descricao","probabilidade","nivel_risco","criado_em"]
                                if c in hist_df.columns]
                disp = hist_df[display_cols].copy()
                if "probabilidade" in disp.columns:
                    disp["probabilidade"] = disp["probabilidade"].apply(lambda x: f"{x*100:.1f}%")
                st.dataframe(disp, use_container_width=True, height=400)

                csv = hist_df.to_csv(index=False, encoding="utf-8-sig")
                st.download_button("⬇️ Exportar historico CSV", csv, "aria_predicoes_ola.csv", "text/csv")

        except requests.exceptions.ConnectionError:
            st.warning("API offline. Inicie com: `uvicorn api.main:app --reload`")
        except Exception as e:
            st.error(f"Erro ao buscar historico: {e}")

# ── Tab 3: Documentacao ───────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Sobre a API ARIA — Sprint 3</div>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"""
        <div style="background:rgba(16,91,216,0.1);border:1px solid rgba(16,91,216,0.25);
                    border-radius:10px;padding:1rem;font-size:0.85rem;color:{GRAY2};margin-bottom:0.8rem">
            <div style="color:{CYAN};font-weight:700;font-size:0.95rem;margin-bottom:0.5rem">Endpoints Disponiveis</div>
            <code style="color:{GRAY1}">GET  /health</code><br>
            <span style="font-size:0.78rem">Status da API, modelos e DB</span><br><br>
            <code style="color:{GRAY1}">POST /predict/ola</code><br>
            <span style="font-size:0.78rem">Probabilidade de violacao OLA</span><br><br>
            <code style="color:{GRAY1}">POST /predict/priority</code><br>
            <span style="font-size:0.78rem">Classificacao de prioridade (2-4)</span><br><br>
            <code style="color:{GRAY1}">GET  /predictions/ola?limit=N</code><br>
            <span style="font-size:0.78rem">Historico persistido no Oracle ADB</span><br><br>
            <code style="color:{GRAY1}">GET  /encoders/info</code><br>
            <span style="font-size:0.78rem">Valores validos nos encoders</span>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown(f"""
        <div style="background:rgba(0,200,122,0.08);border:1px solid rgba(0,200,122,0.2);
                    border-radius:10px;padding:1rem;font-size:0.85rem;color:{GRAY2}">
            <div style="color:{GREEN};font-weight:700;font-size:0.95rem;margin-bottom:0.5rem">Iniciar a API</div>
            <div style="background:rgba(0,0,0,0.3);border-radius:6px;padding:0.6rem;
                        font-family:monospace;color:{GRAY1};font-size:0.82rem;margin-bottom:0.8rem">
                # Instalar dependencias<br>
                pip install fastapi uvicorn oracledb<br><br>
                # Iniciar API<br>
                uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload<br><br>
                # Documentacao interativa<br>
                http://localhost:8000/docs
            </div>
            <div style="color:{GRAY2};font-size:0.78rem">
                Variaveis de ambiente para Oracle ADB:<br>
                <code>ARIA_DB_USER</code>, <code>ARIA_DB_PASSWORD</code>, <code>ARIA_DB_DSN</code><br>
                <code>ARIA_WALLET_DIR</code> (se usar wallet OCI)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                border-radius:10px;padding:1rem;font-size:0.82rem;color:{GRAY2};margin-top:0.5rem">
        <div style="color:{GRAY1};font-weight:600;margin-bottom:0.5rem">Exemplo de requisicao cURL</div>
        <code style="color:{CYAN}">curl -X POST http://localhost:8000/predict/ola \\<br>
        &nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
        &nbsp;&nbsp;-d '{{"prio_num": 3, "hora_abertura": 14, "dia_semana": 1, "mes": 6,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"is_monitoring": 1, "has_parent": 0,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"produto_enc": 0, "grupo_enc": 0, "categoria_enc": 0,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"subcategoria_enc": 0, "cod_fechamento_enc": 0,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"descricao": "Problem: Check Application Monitoring"}}'</code>
    </div>
    """, unsafe_allow_html=True)
