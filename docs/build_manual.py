"""
Gerador do Manual de Utilizacao ARIA AIOps — PDF Profissional
Usa reportlab para layout de alta qualidade.
"""
import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable

# ── Paleta ARIA ───────────────────────────────────────────────
NAVY      = colors.HexColor("#050e1f")
NAVY2     = colors.HexColor("#0d2d6e")
BLUE      = colors.HexColor("#105BD8")
CYAN      = colors.HexColor("#00D4FF")
GREEN     = colors.HexColor("#00C87A")
ORANGE    = colors.HexColor("#FF6B35")
PURPLE    = colors.HexColor("#9B59B6")
WHITE     = colors.HexColor("#FFFFFF")
GRAY1     = colors.HexColor("#C8D8F0")
GRAY2     = colors.HexColor("#8899BB")
GRAY_LIGHT= colors.HexColor("#E8EEF8")
DARK_ROW  = colors.HexColor("#0a1628")
MID_ROW   = colors.HexColor("#0d1f3c")

PAGE_W, PAGE_H = A4
MARGIN = 1.8 * cm

OUT = Path(__file__).parent / "ARIA_Manual_Utilizacao.pdf"


# ── Helper: linha colorida horizontal ─────────────────────────
class ColorLine(Flowable):
    def __init__(self, width, color, thickness=2):
        self.width = width
        self.color = color
        self.thickness = thickness
        self._fixedWidth = width

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

    def wrap(self, *args):
        return self.width, self.thickness + 2


# ── Estilos ───────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "cover_title": s("cover_title",
            fontSize=32, leading=38, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_LEFT),

        "cover_sub": s("cover_sub",
            fontSize=13, leading=18, textColor=CYAN,
            fontName="Helvetica", alignment=TA_LEFT),

        "cover_meta": s("cover_meta",
            fontSize=9, leading=13, textColor=GRAY2,
            fontName="Helvetica", alignment=TA_LEFT),

        "h1": s("h1",
            fontSize=16, leading=20, textColor=CYAN,
            fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6),

        "h2": s("h2",
            fontSize=12, leading=16, textColor=WHITE,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),

        "h3": s("h3",
            fontSize=10, leading=14, textColor=CYAN,
            fontName="Helvetica-BoldOblique", spaceBefore=8, spaceAfter=3),

        "body": s("body",
            fontSize=9, leading=14, textColor=GRAY1,
            fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4),

        "body_small": s("body_small",
            fontSize=8, leading=12, textColor=GRAY2,
            fontName="Helvetica", spaceAfter=2),

        "bullet": s("bullet",
            fontSize=9, leading=13, textColor=GRAY1,
            fontName="Helvetica", leftIndent=12, spaceAfter=2,
            bulletIndent=4, bulletText="•"),

        "code": s("code",
            fontSize=8, leading=12, textColor=GREEN,
            fontName="Courier", backColor=colors.HexColor("#0a1628"),
            leftIndent=8, rightIndent=8, spaceBefore=3, spaceAfter=3),

        "code_label": s("code_label",
            fontSize=7, leading=10, textColor=GRAY2,
            fontName="Courier-Oblique"),

        "caption": s("caption",
            fontSize=8, leading=11, textColor=GRAY2,
            fontName="Helvetica-Oblique", alignment=TA_CENTER),

        "tag": s("tag",
            fontSize=8, leading=11, textColor=CYAN,
            fontName="Helvetica-Bold", alignment=TA_CENTER),
    }


# ── Tabela estilizada ─────────────────────────────────────────
def aria_table(data, col_widths, header=True):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0 if header else -1),
         NAVY2 if header else DARK_ROW),
        ("TEXTCOLOR", (0, 0), (-1, 0), CYAN),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), GRAY1),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_ROW, MID_ROW]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a3060")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, CYAN),
    ]
    return Table(data, colWidths=col_widths,
                 style=TableStyle(style), repeatRows=1 if header else 0)


# ── Caixa de destaque (info/warning) ──────────────────────────
def info_box(text, style_key, bg, border, styles):
    data = [[Paragraph(text, styles[style_key])]]
    tbl = Table(data, colWidths=[PAGE_W - 2 * MARGIN])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1.5, border),
        ("LINEAFTER", (0, 0), (0, -1), 0, border),
    ]))
    return tbl


# ── Header / Footer ───────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(MARGIN, h - 0.75 * cm, "ARIA AIOps — Manual de Utilizacao")
    canvas.setFillColor(GRAY2)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - MARGIN, h - 0.75 * cm,
                           "Locaweb · FIAP 2026 · Cluster 3 · 2TSCO")

    # Top accent line
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(2)
    canvas.line(0, h - 1.2 * cm, w, h - 1.2 * cm)

    # Footer
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 1.0 * cm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#1a3060"))
    canvas.setLineWidth(0.8)
    canvas.line(0, 1.0 * cm, w, 1.0 * cm)
    canvas.setFillColor(GRAY2)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGIN, 0.35 * cm,
        f"Confidencial — uso interno | Gerado em {datetime.date.today().strftime('%d/%m/%Y')}")
    canvas.setFillColor(CYAN)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawRightString(w - MARGIN, 0.35 * cm, f"Pagina {doc.page}")

    canvas.restoreState()


def on_cover_page(canvas, doc):
    """Sem header/footer na capa."""
    w, h = A4
    # Fundo total
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # Gradiente lateral (retangulo azul escuro lateral)
    canvas.setFillColor(NAVY2)
    canvas.rect(0, 0, 0.6 * cm, h, fill=1, stroke=0)

    # Accent lines no topo
    canvas.setStrokeColor(CYAN)
    canvas.setLineWidth(3)
    canvas.line(0.6 * cm, h - 1 * cm, w, h - 1 * cm)
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1)
    canvas.line(0.6 * cm, h - 1.4 * cm, w, h - 1.4 * cm)

    # Accent no rodapé
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1.5)
    canvas.line(0.6 * cm, 2.5 * cm, w, 2.5 * cm)
    canvas.setFillColor(GRAY2)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGIN, 1.5 * cm,
        f"Documento gerado em {datetime.date.today().strftime('%d/%m/%Y')} "
        f"| github.com/afonsoas/aria-aiops | Versao 4.0")


# ── Conteudo ──────────────────────────────────────────────────
def build_story(styles):
    story = []
    cw = PAGE_W - 2 * MARGIN  # content width

    def sp(n=6): return Spacer(1, n)
    def h1(t): return Paragraph(t, styles["h1"])
    def h2(t): return Paragraph(t, styles["h2"])
    def h3(t): return Paragraph(t, styles["h3"])
    def p(t):  return Paragraph(t, styles["body"])
    def bl(t): return Paragraph(t, styles["bullet"])
    def code(t): return Paragraph(t, styles["code"])
    def line(c=BLUE, th=1): return ColorLine(cw, c, th)

    # ── CAPA ──────────────────────────────────────────────────
    story += [
        Spacer(1, 3.5 * cm),
        Paragraph("ARIA", ParagraphStyle("big",
            fontSize=64, leading=70, textColor=CYAN,
            fontName="Helvetica-Bold", alignment=TA_LEFT)),
        Paragraph("AIOps", ParagraphStyle("big2",
            fontSize=40, leading=44, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_LEFT)),
        sp(16),
        Paragraph("Manual de Utilizacao", styles["cover_title"]),
        sp(8),
        Paragraph("Automated Response &amp; Incident Analysis", styles["cover_sub"]),
        sp(20),
        line(CYAN, 1.5),
        sp(10),
        Paragraph(
            "Enterprise Challenge · Locaweb AIOps · FIAP 2026",
            styles["cover_meta"]),
        Paragraph(
            "Cluster 3 · 2TSCO | Sprint 4 — Solucao Final",
            styles["cover_meta"]),
        sp(6),
        Paragraph(
            f"Versao 4.0 · {datetime.date.today().strftime('%d/%m/%Y')}",
            styles["cover_meta"]),
        PageBreak(),
    ]

    # ── 1. VISAO GERAL ────────────────────────────────────────
    story += [
        h1("1. Visao Geral"),
        line(CYAN, 1),
        sp(6),
        p("O <b>ARIA</b> (Automated Response &amp; Incident Analysis) e uma plataforma de "
          "<b>AIOps</b> desenvolvida para a Locaweb como parte do Enterprise Challenge FIAP 2026. "
          "A solucao combina machine learning, visualizacao interativa e persistencia em nuvem para "
          "apoiar a gestao proativa de incidentes de TI."),
        sp(8),
        aria_table([
            ["Camada", "URL / Endereco", "Funcao"],
            ["Dashboard", "afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app",
             "Interface visual — analise e predicao"],
            ["API REST", "aria-api-production.up.railway.app",
             "Motor de predicao ML — integracao externa"],
            ["Oracle ADB", "ariaaiops (OCI Sao Paulo)",
             "Historico persistido de predicoes"],
            ["GitHub", "github.com/afonsoas/aria-aiops",
             "Codigo-fonte e CI/CD"],
        ], [2.8*cm, 7.5*cm, 5.2*cm]),
        sp(12),

        h2("Componentes de Machine Learning"),
        sp(4),
        aria_table([
            ["Modelo", "Algoritmo", "Metrica Principal", "Dataset de Treino"],
            ["Modelo A — OLA", "XGBoost + SMOTE + Calibracao Isotonica",
             "ROC-AUC: 0.86 | Precision: 27%", "20.480 incidentes elegíveis"],
            ["Modelo B — Prioridade", "Random Forest", "F1-macro: 0.89 | Accuracy: 90%",
             "97.767 incidentes"],
        ], [3.2*cm, 4.8*cm, 4.2*cm, 4.0*cm]),
        sp(10),

        h2("Arquitetura da Solucao"),
        sp(4),
        p("O dashboard Streamlit consome a API REST via HTTP. A API carrega os modelos ML "
          "(.pkl) na inicializacao e persiste cada predicao no Oracle Autonomous Database. "
          "O deploy e automatizado via GitHub Actions (CI) e Railway.app (CD para a API)."),
        PageBreak(),
    ]

    # ── 2. ACESSO E NAVEGACAO ─────────────────────────────────
    story += [
        h1("2. Acesso e Navegacao"),
        line(CYAN, 1),
        sp(6),
        p("O dashboard e publico e acessivel diretamente pelo browser, sem necessidade de "
          "instalacao ou cadastro."),
        sp(4),
        info_box(
            "<b>URL do Dashboard:</b> https://afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app",
            "body", colors.HexColor("#051530"), CYAN, styles),
        sp(10),

        h2("Formas de Navegacao"),
        sp(4),
        aria_table([
            ["Metodo", "Como usar", "Disponivel em"],
            ["Barra superior", "Botoes azuis na pagina Home — clique na pagina desejada",
             "Apenas na Home"],
            ["Sidebar lateral", "Icone > no canto superior esquerdo — menu sempre visivel",
             "Todas as paginas"],
            ["URL direta", "Digite o caminho na barra do browser (ex: /kpi_overview)",
             "Todas as paginas"],
        ], [3.2*cm, 8.0*cm, 4.8*cm]),
        sp(10),

        h2("Paginas Disponiveis"),
        sp(4),
        aria_table([
            ["Pagina", "URL", "Funcao Principal"],
            ["Home", "/", "KPIs globais e visao geral dos modelos (v4.0)"],
            ["KPI Overview", "/kpi_overview", "6 graficos de analise de indicadores"],
            ["Incidentes", "/incident_list", "Tabela filtravel com todos os incidentes"],
            ["Preditor OLA", "/ola_predictor", "Predicao de risco + explicacao SHAP por instancia"],
            ["Padroes", "/patterns", "Heatmaps e analise de comportamento"],
            ["API Live", "/api_predictor", "Interface para testar a API REST + historico ADB"],
            ["Simulacao", "/simulacao", "Geracao de incidentes sinteticos em tempo real"],
        ], [3.0*cm, 3.5*cm, 8.5*cm]),
        PageBreak(),
    ]

    # ── 3. PAGINA INICIAL ─────────────────────────────────────
    story += [
        h1("3. Pagina Inicial — Home"),
        line(CYAN, 1),
        sp(6),
        p("Exibe os <b>5 KPIs globais</b> do dataset Locaweb (Jan/2023 – Dez/2025) e os "
          "destaques dos modelos ML treinados."),
        sp(8),

        h2("Cards de KPI"),
        sp(4),
        aria_table([
            ["Card", "O que representa"],
            ["Total de Incidentes", "Volume total de incidentes no periodo analisado"],
            ["KPI Violados", "Incidentes que ultrapassaram o tempo de OLA"],
            ["Via Monitoramento", "Percentual abertos automaticamente por ferramentas de monitoramento"],
            ["Concentracao Team14", "Percentual de incidentes do grupo com maior volume"],
            ["Periodo Analisado", "Cobertura temporal do dataset (em anos)"],
        ], [4.5*cm, 11.0*cm]),
        sp(10),

        h2("Cards de Destaques"),
        sp(4),
        aria_table([
            ["Card", "Informacao"],
            ["Modelo A — Predicao OLA", "XGBoost + SMOTE + Calibracao Isotonica | ROC-AUC 0.86 | Precision 27% | 20.480 incidentes"],
            ["Modelo B — Classificacao Prioridade", "Random Forest | F1-macro 0.89 | Accuracy 90% | 97.767 incidentes"],
            ["Top Incidente", "Check Application Monitoring — 28.728 ocorrencias (23,4% do total)"],
        ], [5.5*cm, 10.0*cm]),
        PageBreak(),
    ]

    # ── 4. KPI OVERVIEW ───────────────────────────────────────
    story += [
        h1("4. KPI Overview — Analise de Indicadores"),
        line(CYAN, 1),
        sp(6),
        p("Pagina de analise exploratoria com <b>6 graficos interativos</b> sobre o historico "
          "de incidentes Locaweb."),
        sp(8),

        h2("Graficos Disponiveis"),
        sp(4),
        aria_table([
            ["Grafico", "Tipo", "Insight Principal"],
            ["Violacoes OLA por Prioridade",
             "Barra agrupada", "Quais niveis de prioridade violam mais o OLA"],
            ["Distribuicao de Prioridades",
             "Barra horizontal", "Volume de incidentes por nivel (1=Critica a 5=Muito Baixa)"],
            ["Top 10 Grupos",
             "Barra horizontal", "Times com maior volume de incidentes recebidos"],
            ["Evolucao Mensal",
             "Linha temporal", "Tendencia de volume ao longo de Jan/2023 – Dez/2025"],
            ["Abertura por Hora do Dia",
             "Barra", "Pico de abertura de chamados por hora (0–23h)"],
            ["Taxa de Violacao por Grupo",
             "Barra", "Percentual de violacao OLA por grupo designado"],
        ], [4.5*cm, 3.0*cm, 8.0*cm]),
        sp(10),

        h2("Interatividade dos Graficos"),
        sp(4),
        bl("Passe o mouse sobre qualquer barra ou ponto para ver o valor exato"),
        bl("Clique e arraste dentro do grafico para zoom em uma regiao especifica"),
        bl("Duplo clique para resetar a vista original"),
        bl("Clique nos itens da legenda para ocultar/exibir series"),
        sp(4),
        info_box(
            "<b>Nota:</b> O scroll da pagina funciona normalmente ao passar sobre os graficos. "
            "O zoom por scroll esta desabilitado para melhor experiencia de navegacao.",
            "body_small", colors.HexColor("#051530"), BLUE, styles),
        PageBreak(),
    ]

    # ── 5. INCIDENTES ─────────────────────────────────────────
    story += [
        h1("5. Incidentes — Lista e Filtros"),
        line(CYAN, 1),
        sp(6),
        p("Tabela paginada e filtravel com todos os incidentes do dataset. Util para "
          "auditoria, busca de padroes especificos e analise detalhada por grupo ou periodo."),
        sp(8),

        h2("Filtros Disponiveis"),
        sp(4),
        aria_table([
            ["Filtro", "Tipo", "Descricao"],
            ["Prioridade", "Multiselect", "Filtrar por niveis 1 a 5"],
            ["Grupo designado", "Multiselect", "Time responsavel pelo incidente"],
            ["Status", "Multiselect", "Aberto, Resolvido, Encerrado"],
            ["KPI Violado", "Multiselect", "Sim / Nao / Nao informado"],
            ["Periodo de abertura", "Slider de datas", "Intervalo de datas de abertura"],
        ], [3.5*cm, 3.0*cm, 9.0*cm]),
        sp(10),

        h2("Como Usar"),
        sp(4),
        bl("Os filtros ficam na <b>sidebar esquerda</b> da pagina Incidentes"),
        bl("A tabela e os 2 graficos inferiores atualizam automaticamente ao aplicar filtros"),
        bl("Clique no cabecalho de uma coluna para <b>ordenar</b> (asc/desc)"),
        bl("O contador no topo mostra quantos registros estao exibidos apos filtro"),
        sp(10),

        h2("Graficos da Pagina"),
        sp(4),
        aria_table([
            ["Grafico", "O que exibe"],
            ["Distribuicao por Status", "Pizza com proporcao de incidentes por status atual"],
            ["Distribuicao por Prioridade", "Barra com volume dos registros filtrados por prioridade"],
        ], [5.5*cm, 10.0*cm]),
        PageBreak(),
    ]

    # ── 6. PREDITOR OLA ───────────────────────────────────────
    story += [
        h1("6. Preditor OLA — Risco de Violacao"),
        line(CYAN, 1),
        sp(6),
        p("<b>Modelo A:</b> XGBoost + SMOTE + Calibracao Isotonica | ROC-AUC 0.86 | Precision 27%"),
        sp(4),
        p("Prevê a probabilidade calibrada de um <b>novo incidente</b> violar o OLA antes de ser "
          "formalmente aberto. Apos a predicao, o <b>SHAP TreeExplainer</b> decompoe a previsao "
          "em contribuicoes individuais de cada feature, permitindo entender o motivo do risco."),
        sp(8),

        h2("Campos do Formulario"),
        sp(4),
        aria_table([
            ["Campo", "Tipo", "O que informar"],
            ["Prioridade", "Selecao", "Nivel de urgencia: 2=Alta, 3=Media, 4=Baixa"],
            ["Produto", "Selecao", "Sistema ou produto afetado (ex: Email, Hospedagem)"],
            ["Categoria", "Selecao", "Tipo de problema (ex: Indisponibilidade, Lentidao)"],
            ["Subcategoria", "Selecao", "Especializacao da categoria"],
            ["Grupo designado", "Selecao", "Time que receberá o incidente"],
            ["Hora de abertura", "Slider 0–23", "Hora prevista de criacao do incidente"],
            ["Dia da semana", "Selecao", "Dia em que o incidente sera aberto"],
            ["Descricao resumida", "Texto livre", "Titulo ou descricao do problema"],
            ["Aberto por Monitoramento", "Checkbox", "Marcar se veio de alerta automatico"],
            ["Tem Incidente Pai", "Checkbox", "Marcar se vinculado a outro incidente"],
            ["Codigo de Fechamento", "Selecao opcional", "Se ja conhecido — melhora a predicao"],
        ], [3.8*cm, 3.2*cm, 8.5*cm]),
        sp(10),

        h2("Interpretacao do Resultado"),
        sp(4),
        p("<b>Importante:</b> Os thresholds foram ajustados para refletir as probabilidades "
          "calibradas. Com calibracao isotonica e taxa base de violacao de 0,97%, valores "
          "acima de 25% ja representam risco significativamente elevado."),
        sp(4),
        aria_table([
            ["Prob. Calibrada", "Nivel de Risco", "Acao Recomendada"],
            ["0% – 9%",   "🟢 BAIXO RISCO",
             "Fluxo padrao — seguir processo normal de atendimento"],
            ["10% – 24%", "🟠 RISCO MEDIO",
             "Monitorar — acionar time responsavel se sem resposta em 30 min"],
            ["≥ 25%",     "🔴 ALTO RISCO",
             "Escalar imediatamente para o grupo designado"],
        ], [3.0*cm, 3.5*cm, 9.0*cm]),
        sp(10),

        h2("Explicacao SHAP por Instancia"),
        sp(4),
        p("Apos cada predicao, o <b>SHAP TreeExplainer</b> calcula a contribuicao de cada "
          "feature para aquele incidente especifico. O grafico de barras horizontal exibe:"),
        sp(3),
        bl("<b>Barras vermelhas</b> — features que <b>aumentam</b> o risco de violacao OLA"),
        bl("<b>Barras verdes</b> — features que <b>reduzem</b> o risco de violacao OLA"),
        bl("Valor numerico = contribuicao SHAP (magnitude = importancia relativa)"),
        bl("Valor base = probabilidade media do modelo sem nenhuma feature especifica"),
        sp(4),
        p("Se o SHAP nao estiver disponivel (modelo sem suporte a TreeExplainer), "
          "o sistema exibe automaticamente a importancia global das features como fallback."),
        sp(6),
        info_box(
            "<b>Importante:</b> Cada predicao e automaticamente salva no Oracle Autonomous "
            "Database e pode ser consultada no historico da pagina API Live.",
            "body_small", colors.HexColor("#051530"), GREEN, styles),
        PageBreak(),
    ]

    # ── 7. PADROES ────────────────────────────────────────────
    story += [
        h1("7. Padroes — Analise de Comportamento"),
        line(CYAN, 1),
        sp(6),
        p("Identificacao de padroes recorrentes no historico de incidentes. Util para "
          "planejamento de capacidade, prevencao de picos e benchmarking de SLA."),
        sp(8),

        h2("Visualizacoes"),
        sp(4),
        aria_table([
            ["Visualizacao", "Como Interpretar"],
            ["Top Descricoes",
             "Incidentes mais frequentes por titulo — identifica problemas sistemicos"],
            ["Heatmap Hora x Dia",
             "Intensidade de chamados por hora/dia — planejar escalas operacionais"],
            ["Duracao por Prioridade",
             "Tempo medio de resolucao — benchmarking vs SLA contratado"],
            ["Tendencia de Violacao",
             "Evolucao mensal da taxa de violacao OLA — detecta pioras/melhoras"],
            ["Correlacao entre Features",
             "Matriz de correlacao — identifica variaveis correlacionadas com violacao"],
        ], [4.5*cm, 11.0*cm]),
        sp(10),

        h2("Aplicacoes Praticas"),
        sp(4),
        bl("<b>Planejamento de plantao:</b> use o heatmap para definir horarios de pico e dimensionar equipes"),
        bl("<b>Playbooks:</b> as top descricoes indicam onde automatizar respostas"),
        bl("<b>Negociacao de SLA:</b> use a duracao por prioridade para embasar contratos"),
        bl("<b>Monitoramento continuo:</b> acompanhe a tendencia de violacao mensalmente"),
        PageBreak(),
    ]

    # ── 8. SIMULACAO ─────────────────────────────────────────
    story += [
        h1("8. Simulacao — Incidentes em Tempo Real"),
        line(CYAN, 1),
        sp(6),
        p("A pagina de <b>Simulacao</b> gera incidentes sinteticos a partir das distribuicoes "
          "reais do dataset Locaweb e executa o Modelo A em tempo real, permitindo observar "
          "como o sistema se comportaria em producao."),
        sp(8),

        h2("Controles da Simulacao"),
        sp(4),
        aria_table([
            ["Controle", "Descricao"],
            ["Incidentes por rodada", "Slider para definir quantos incidentes sinteticos gerar (1–50)"],
            ["Gerar Incidentes", "Executa uma rodada de predicoes com distribuicoes reais"],
            ["Auto-Refresh", "Ativa geracao automatica a cada 10 segundos"],
            ["Limpar", "Reseta o historico acumulado da sessao"],
        ], [4.5*cm, 11.0*cm]),
        sp(10),

        h2("Visualizacoes"),
        sp(4),
        aria_table([
            ["Componente", "O que exibe"],
            ["Cards KPI (4)", "Total gerado, Alto Risco, Risco Medio, Baixo Risco da rodada atual"],
            ["Tabela de Incidentes", "ID, Hora, Prioridade, Grupo, Produto, Prob.%, Nivel com badge colorido"],
            ["Donut Distribuicao", "Proporcao ALTO / MEDIO / BAIXO na rodada atual"],
            ["Historico Acumulado", "Grafico de barras empilhadas por rodada — evolucao da sesssao"],
        ], [4.5*cm, 11.0*cm]),
        sp(10),

        h2("Como os Incidentes Sinteticos Sao Gerados"),
        sp(4),
        bl("Grupo, produto, categoria e subcategoria: amostrados das distribuicoes reais do dataset"),
        bl("Prioridade: distribuicao ponderada (60% Media, 25% Baixa, 15% Alta)"),
        bl("Hora de abertura: uniforme entre 0-23h com maior peso em horario comercial"),
        bl("Descricao: selecionada aleatoriamente do top-50 descricoes mais frequentes do dataset"),
        bl("is_monitoring / has_parent: bernoulli com probabilidades historicas do dataset"),
        sp(6),
        info_box(
            "<b>Nota:</b> Os incidentes sinteticos nao sao salvos no Oracle ADB — "
            "sao usados apenas para demonstracao e validacao do modelo em tempo real.",
            "body_small", colors.HexColor("#051530"), CYAN, styles),
        PageBreak(),
    ]

    # ── 9. API LIVE ───────────────────────────────────────────
    story += [
        h1("9. API Live — Interface de Predicao"),
        line(CYAN, 1),
        sp(6),
        p("Interface visual para consumir a API REST diretamente pelo browser, sem necessidade "
          "de ferramentas externas como Postman ou curl."),
        sp(8),

        h2("Secoes da Pagina"),
        sp(4),
        aria_table([
            ["Secao", "Funcao"],
            ["Predicao OLA",
             "Formulario para testar /predict/ola — retorna probabilidade e nivel de risco"],
            ["Predicao de Prioridade",
             "Formulario para testar /predict/priority — retorna prioridade sugerida"],
            ["Historico de Predicoes",
             "Consulta /predictions/ola — exibe as ultimas predicoes salvas no Oracle ADB"],
            ["Info dos Encoders",
             "Lista todos os valores validos por campo — essencial para integracoes"],
        ], [4.5*cm, 11.0*cm]),
        sp(10),

        h2("Configuracao da URL da API"),
        sp(4),
        p("A URL da API e configuravel no topo da sidebar. O valor padrao e:"),
        sp(3),
        code("https://aria-api-production.up.railway.app"),
        sp(4),
        p("Para usar uma instancia local ou de homologacao, substitua pela URL desejada "
          "e clique fora do campo para aplicar."),
        PageBreak(),
    ]

    # ── 9. API REST ───────────────────────────────────────────
    story += [
        h1("10. API REST — Integracao com Sistemas Externos"),
        line(CYAN, 1),
        sp(6),
        p("A API ARIA pode ser integrada a qualquer sistema que suporte chamadas HTTP. "
          "Documentacao interativa disponivel em <b>/docs</b> (Swagger UI)."),
        sp(8),

        h2("Endpoints Disponiveis (API v4.0)"),
        sp(4),
        aria_table([
            ["Metodo", "Endpoint", "Descricao"],
            ["GET",  "/health",              "Status da API, modelos e conexao com DB"],
            ["POST", "/predict/ola",         "Probabilidade de violacao OLA (0–100%)"],
            ["POST", "/predict/ola/batch",   "Predicao em lote — ate 100 incidentes simultaneos"],
            ["POST", "/predict/priority",    "Classificacao de prioridade (2, 3 ou 4)"],
            ["POST", "/explain/ola",         "Predicao OLA + top 8 features SHAP explicadas"],
            ["GET",  "/predictions/ola",     "Historico de predicoes salvas no Oracle ADB"],
            ["GET",  "/encoders/info",       "Valores validos por campo codificado"],
        ], [1.8*cm, 4.5*cm, 9.2*cm]),
        sp(10),

        h2("Exemplo — Predicao OLA (curl)"),
        sp(4),
        code('curl -X POST "https://aria-api-production.up.railway.app/predict/ola" \\'),
        code('  -H "Content-Type: application/json" \\'),
        code('  -d \'{"prio_num":2,"hora_abertura":9,"dia_semana":0,"mes":4,'),
        code('       "is_monitoring":1,"has_parent":0,'),
        code('       "produto_enc":0,"grupo_enc":0,"categoria_enc":0,'),
        code('       "subcategoria_enc":0,"cod_fechamento_enc":0,'),
        code('       "descricao":"Servidor fora do ar","numero":"INC001"}\''),
        sp(6),

        h2("Exemplo — Resposta"),
        sp(4),
        code('{"probabilidade":0.0022,"percentual":"0.2%",'),
        code(' "nivel_risco":"BAIXO",'),
        code(' "recomendacao":"Incidente dentro do padrao. Seguir fluxo standard.",'),
        code(' "numero":"INC001","timestamp":"2026-04-16T01:47:02Z"}'),
        sp(10),

        h2("Referencia de Campos do Payload"),
        sp(4),
        aria_table([
            ["Campo", "Tipo", "Valores / Descricao"],
            ["prio_num", "int", "1=Critica, 2=Alta, 3=Media, 4=Baixa, 5=Muito Baixa"],
            ["hora_abertura", "int", "0 a 23"],
            ["dia_semana", "int", "0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sab, 6=Dom"],
            ["mes", "int", "1 a 12"],
            ["is_monitoring", "int", "0=Manual, 1=Monitoramento automatico"],
            ["has_parent", "int", "0=Nao tem pai, 1=Tem incidente pai"],
            ["*_enc", "int", "ID do encoder — consultar /encoders/info"],
            ["descricao", "string", "Texto livre do titulo do incidente"],
            ["numero", "string (opcional)", "Numero do incidente para rastreabilidade"],
        ], [3.5*cm, 2.5*cm, 9.5*cm]),
        PageBreak(),
    ]

    # ── 10. ORACLE ADB ────────────────────────────────────────
    story += [
        h1("11. Oracle Autonomous Database"),
        line(CYAN, 1),
        sp(6),
        p("Todas as predicoes realizadas pela API sao automaticamente persistidas no "
          "<b>Oracle Autonomous Database (ADB)</b> hospedado na OCI (regiao Sao Paulo)."),
        sp(8),

        h2("Tabelas Criadas Automaticamente"),
        sp(4),
        aria_table([
            ["Tabela", "Conteudo", "Campos Principais"],
            ["aria_ola_predictions",
             "Historico de predicoes de violacao OLA",
             "numero, prio_num, hora, probabilidade, nivel_risco, criado_em"],
            ["aria_priority_predictions",
             "Historico de predicoes de prioridade",
             "numero, prio_num_entrada, prioridade_predita, criado_em"],
        ], [4.5*cm, 4.5*cm, 7.5*cm]),
        sp(10),

        h2("Consulta via API"),
        sp(4),
        code("GET https://aria-api-production.up.railway.app/predictions/ola?limit=100"),
        sp(4),
        p("O parametro <b>limit</b> aceita valores de 1 a 500. "
          "Retorna lista JSON ordenada por data decrescente (mais recente primeiro)."),
        sp(10),

        h2("Comportamento Offline"),
        sp(4),
        p("Se as credenciais do banco nao estiverem configuradas ou a conexao falhar, "
          "a API continua funcionando normalmente em modo offline — as predicoes sao "
          "retornadas mas nao persistidas. O campo <b>db_conectado</b> no /health "
          "indica o status da conexao."),
        PageBreak(),
    ]

    # ── 11. RESOLUCAO DE PROBLEMAS ────────────────────────────
    story += [
        h1("12. Resolucao de Problemas"),
        line(CYAN, 1),
        sp(6),
        aria_table([
            ["Problema", "Causa Provavel", "Solucao"],
            ["Dashboard nao carrega",
             "App em cold start (primeiros 30s)",
             "Aguardar 30-60s e recarregar a pagina"],
            ["Graficos nao aparecem",
             "Dataset grande — loading lento",
             "Aguardar o spinner 'Carregando dataset...' completar"],
            ["API retorna 502",
             "Container em cold start",
             "Aguardar 15s e repetir a requisicao"],
            ["db_conectado: false no /health",
             "Credenciais Oracle nao configuradas",
             "Verificar env vars no Railway (ARIA_DB_PASSWORD, ARIA_DB_DSN)"],
            ["Predicao retorna erro de schema",
             "Campo obrigatorio ausente no payload",
             "Verificar todos os campos numericos obrigatorios"],
            ["'Page not found' no dashboard",
             "URL digitada com numero (ex: /1_kpi_overview)",
             "Usar URL sem numero (ex: /kpi_overview)"],
        ], [4.0*cm, 4.5*cm, 7.0*cm]),
        sp(12),

        h2("Suporte Tecnico"),
        sp(4),
        bl("<b>GitHub Issues:</b> github.com/afonsoas/aria-aiops/issues"),
        bl("<b>Documentacao API:</b> aria-api-production.up.railway.app/docs"),
        bl("<b>Logs da API:</b> Railway Dashboard — projeto aria-aiops"),
        sp(12),

        h1("13. Informacoes Tecnicas"),
        line(CYAN, 1),
        sp(6),
        aria_table([
            ["Componente", "Tecnologia", "Versao"],
            ["Dashboard", "Streamlit + Plotly", ">= 1.28"],
            ["API", "FastAPI + Uvicorn", ">= 0.104 / >= 0.24"],
            ["Modelo OLA", "XGBoost + imbalanced-learn (SMOTE)", ">= 2.0 / >= 0.11"],
            ["Calibracao", "Isotonic Regression (sklearn)", ">= 1.3"],
            ["Explicabilidade", "SHAP TreeExplainer", ">= 0.44"],
            ["Modelo Prioridade", "scikit-learn RandomForest", ">= 1.3"],
            ["NLP", "TF-IDF + NLTK Stopwords PT-BR", ">= 1.11 / >= 3.8"],
            ["Banco de Dados", "Oracle Autonomous DB (oracledb thin mode)", ">= 2.0"],
            ["CI/CD", "GitHub Actions + Railway.app", "—"],
            ["Hospedagem Dashboard", "Streamlit Community Cloud", "Free tier"],
            ["Linguagem", "Python", "3.12"],
        ], [4.0*cm, 6.0*cm, 5.5*cm]),
    ]

    return story


# ── Construcao do PDF ─────────────────────────────────────────
def build_pdf():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="ARIA AIOps — Manual de Utilizacao",
        author="Cluster 3 · 2TSCO · FIAP 2026",
        subject="Manual de Utilizacao da Plataforma ARIA AIOps",
    )

    styles = make_styles()
    story = build_story(styles)

    # Pagina 1 = capa (sem header/footer), restante com header/footer
    doc.build(story,
              onFirstPage=on_cover_page,
              onLaterPages=on_page)

    print(f"PDF gerado: {OUT}")
    print(f"Tamanho: {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    build_pdf()
