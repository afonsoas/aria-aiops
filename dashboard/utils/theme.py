"""
ARIA Dashboard — Sistema de Tema Global
Estilo escuro profissional com glassmorphism e gradientes.
"""

# ── Paleta ───────────────────────────────────────────────────
NAVY    = "#0a1628"
NAVY2   = "#0D1B3E"
BLUE    = "#105BD8"
BLUE2   = "#1a6fee"
CYAN    = "#00D4FF"
ORANGE  = "#FF6B35"
GREEN   = "#00C87A"
PURPLE  = "#7C3AED"
WHITE   = "#FFFFFF"
GRAY1   = "#e2e8f8"
GRAY2   = "#8899bb"
GLASS   = "rgba(255,255,255,0.05)"
GLASS2  = "rgba(255,255,255,0.10)"

# Plotly dark template
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=GRAY1, family="Inter, sans-serif", size=12),
    # title_font removido — causa renderizacao de "undefined" quando title.text nao esta definido
    title=dict(text="", font=dict(color=WHITE, size=14)),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.15)",
        tickfont=dict(color=GRAY2),
        title_font=dict(color=GRAY2),
        zerolinecolor="rgba(255,255,255,0.07)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.15)",
        tickfont=dict(color=GRAY2),
        title_font=dict(color=GRAY2),
        zerolinecolor="rgba(255,255,255,0.07)",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=GRAY1),
    ),
    margin=dict(l=10, r=10, t=10, b=10),
    dragmode=False,
    coloraxis_colorbar=dict(
        tickfont=dict(color=GRAY2),
        title_font=dict(color=GRAY2),
    ),
)

ARIA_CSS = """
<style>
/* ── Reset e fundo global ── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
    background: linear-gradient(135deg, #050e1f 0%, #0a1628 40%, #0d1e3a 100%) !important;
    color: #e2e8f8 !important;
}

/* ── Toolbar (faixa branca do topo com botao Deploy) ── */
[data-testid="stHeader"],
header[data-testid="stHeader"] {
    background: #050e1f !important;
    border-bottom: 1px solid rgba(0,212,255,0.08) !important;
}
[data-testid="stToolbar"] {
    background: #050e1f !important;
}
[data-testid="stToolbar"] * { color: #8899bb !important; }
[data-testid="stToolbar"] button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    color: #8899bb !important;
}
[data-testid="stToolbar"] button:hover {
    background: rgba(0,212,255,0.1) !important;
    border-color: rgba(0,212,255,0.3) !important;
    color: #00D4FF !important;
}
#MainMenu { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Remove padding excessivo */
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06101f 0%, #0a1628 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.15) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f8 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 6px !important;
    color: #e2e8f8 !important;
}
[data-testid="stSidebar"] label { color: #8899bb !important; font-size: 0.78rem !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #00D4FF !important; }

/* ── Header ARIA ── */
.aria-header {
    background: linear-gradient(90deg, #050e1f 0%, #0d2d6e 50%, #050e1f 100%);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.aria-header::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00D4FF, #105BD8, transparent);
}
.aria-header h1 {
    color: #FFFFFF !important;
    margin: 0;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}
.aria-header p {
    color: #00D4FF !important;
    margin: 0.3rem 0 0 0 !important;
    font-size: 0.82rem !important;
    opacity: 0.85;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.1rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    transition: transform 0.2s;
}
.kpi-card::after {
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.35rem;
    letter-spacing: -1px;
}
.kpi-label {
    font-size: 0.75rem;
    color: #8899bb;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-sub {
    font-size: 0.7rem;
    color: #5566aa;
    margin-top: 0.2rem;
}

/* ── Section titles ── */
h1, h2, h3, h4 { color: #e2e8f8 !important; }
.section-title {
    color: #e2e8f8 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border-left: 3px solid #00D4FF;
    padding-left: 0.6rem;
    margin-bottom: 0.8rem;
}

/* ── Chart containers ── */
.chart-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}

/* ── Streamlit overrides ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
}
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { color: #8899bb !important; }
[data-testid="stMetricDelta"] > div { font-size: 0.75rem !important; }

/* Inputs / selects */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(0,212,255,0.2) !important;
    color: #e2e8f8 !important;
    border-radius: 6px !important;
}
input, textarea {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(0,212,255,0.2) !important;
    color: #e2e8f8 !important;
    border-radius: 6px !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 8px !important;
    padding: 3px !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    color: #8899bb !important;
    border-radius: 6px !important;
}
[aria-selected="true"] {
    background: rgba(16,91,216,0.4) !important;
    color: #FFFFFF !important;
}

/* Tabela */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Botoes */
[data-testid="stButton"] > button,
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #105BD8, #0a3d9e) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button {
    background: rgba(0,200,122,0.15) !important;
    border: 1px solid rgba(0,200,122,0.4) !important;
    color: #00C87A !important;
    border-radius: 8px !important;
}

/* st.info / warning / success / error */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 8px !important;
    border-left-width: 3px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 10px; }

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Caption */
[data-testid="stCaptionContainer"] p { color: #5566aa !important; }

/* Checkbox */
[data-testid="stCheckbox"] label { color: #8899bb !important; }

/* Slider */
[data-testid="stSlider"] > div > div > div > div {
    background: #105BD8 !important;
}

/* sidebar navigation — texto em maiusculas */
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] span,
[data-testid="stSidebarNavItems"] span,
section[data-testid="stSidebar"] nav a span {
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* page nav links */
[data-testid="stPageLink"] a {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #8899bb !important;
    padding: 0.4rem 0.8rem !important;
    text-decoration: none !important;
    font-size: 0.85rem !important;
}
[data-testid="stPageLink"] a:hover {
    background: rgba(0,212,255,0.1) !important;
    border-color: rgba(0,212,255,0.4) !important;
    color: #00D4FF !important;
}
</style>
"""


def inject_css():
    """Injeta o CSS do tema ARIA em qualquer página Streamlit."""
    import streamlit as st
    st.markdown(ARIA_CSS, unsafe_allow_html=True)


def kpi_card(value: str, label: str, sub: str = "", color: str = "#105BD8") -> str:
    """Retorna HTML de um card KPI estilizado."""
    return f"""
    <div class="kpi-card" style="border-top: 3px solid {color}">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
        {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
    </div>
    """


def section_title(text: str, icon: str = "") -> str:
    return f'<div class="section-title">{icon + " " if icon else ""}{text}</div>'


def aria_header(title: str = "ARIA", subtitle: str = "") -> str:
    return f"""
    <div class="aria-header">
        <h1>{title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """


def apply_plotly_theme(fig):
    """Aplica o tema escuro ARIA a qualquer figura Plotly."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
