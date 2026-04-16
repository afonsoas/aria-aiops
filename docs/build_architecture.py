"""
Gera ARIA_Arquitetura_Tecnica.pdf
Documento profissional de arquitetura do sistema ARIA AIOps.
Requer: reportlab
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle
from reportlab.graphics import renderPDF

OUTPUT = Path(__file__).parent / "ARIA_Arquitetura_Tecnica.pdf"

# ── Paleta ARIA ─────────────────────────────────────────────
NAVY    = colors.HexColor("#050e1f")
NAVY2   = colors.HexColor("#0D1B3E")
BLUE    = colors.HexColor("#105BD8")
BLUE2   = colors.HexColor("#1a6fee")
CYAN    = colors.HexColor("#00D4FF")
ORANGE  = colors.HexColor("#FF6B35")
GREEN   = colors.HexColor("#00C87A")
PURPLE  = colors.HexColor("#7C3AED")
WHITE   = colors.white
GRAY1   = colors.HexColor("#e2e8f8")
GRAY2   = colors.HexColor("#8899bb")
GRAY3   = colors.HexColor("#3a4a6b")
DARK    = colors.HexColor("#0a1628")

W, H = A4  # 595.27 x 841.89 points

# ── Estilos ──────────────────────────────────────────────────
def S(name, **kw):
    base = {
        "fontName": "Helvetica",
        "fontSize": 10,
        "textColor": GRAY1,
        "leading": 14,
        "spaceAfter": 4,
    }
    base.update(kw)
    return ParagraphStyle(name, **base)

sTitle    = S("title",   fontName="Helvetica-Bold", fontSize=28, textColor=WHITE,   leading=34, spaceAfter=6,  alignment=TA_CENTER)
sTitleSub = S("titlesub",fontName="Helvetica",       fontSize=13, textColor=CYAN,    leading=18, spaceAfter=4,  alignment=TA_CENTER)
sH1       = S("h1",      fontName="Helvetica-Bold", fontSize=16, textColor=WHITE,   leading=20, spaceBefore=14,spaceAfter=6)
sH2       = S("h2",      fontName="Helvetica-Bold", fontSize=12, textColor=CYAN,    leading=16, spaceBefore=10,spaceAfter=4)
sH3       = S("h3",      fontName="Helvetica-Bold", fontSize=10, textColor=GRAY1,   leading=14, spaceBefore=6, spaceAfter=2)
sBody     = S("body",    fontName="Helvetica",       fontSize=9,  textColor=GRAY1,   leading=13, spaceAfter=3,  alignment=TA_JUSTIFY)
sBodyBold = S("bodybold",fontName="Helvetica-Bold", fontSize=9,  textColor=WHITE,   leading=13, spaceAfter=3)
sCode     = S("code",    fontName="Courier",         fontSize=8,  textColor=CYAN,    leading=11, spaceAfter=2,  backColor=colors.HexColor("#0d1b3e"), leftIndent=8, rightIndent=8)
sCaption  = S("caption", fontName="Helvetica",       fontSize=7.5,textColor=GRAY2,   leading=10, spaceAfter=2,  alignment=TA_CENTER)
sBullet   = S("bullet",  fontName="Helvetica",       fontSize=9,  textColor=GRAY1,   leading=13, spaceAfter=2,  leftIndent=14, bulletIndent=4)
sMeta     = S("meta",    fontName="Helvetica",       fontSize=8,  textColor=GRAY2,   leading=11, spaceAfter=0,  alignment=TA_CENTER)
sLabel    = S("label",   fontName="Helvetica-Bold", fontSize=8,  textColor=CYAN,    leading=10, spaceAfter=1)
sTag      = S("tag",     fontName="Helvetica-Bold", fontSize=7,  textColor=WHITE,   leading=9,  spaceAfter=0,  alignment=TA_CENTER)


# ── Flowables customizados ───────────────────────────────────
class ColoredBackground(Flowable):
    """Fundo colorido de largura total para seções de destaque."""
    def __init__(self, color, height=0.8*cm):
        super().__init__()
        self.color = color
        self.height = height
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, W - 4*cm, self.height, stroke=0, fill=1)


class SectionHeader(Flowable):
    """Header de seção estilizado com linha CYAN."""
    def __init__(self, text, number="", width=None):
        super().__init__()
        self.text = text
        self.number = number
        self.width = width or (W - 4*cm)
        self.height = 1.4*cm

    def draw(self):
        c = self.canv
        w = self.width
        # fundo
        c.setFillColor(NAVY2)
        c.rect(0, 0, w, self.height, stroke=0, fill=1)
        # linha topo cyan
        c.setFillColor(CYAN)
        c.rect(0, self.height - 2, w, 2, stroke=0, fill=1)
        # barra lateral
        c.setFillColor(BLUE)
        c.rect(0, 0, 4, self.height, stroke=0, fill=1)
        # número
        if self.number:
            c.setFillColor(CYAN)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(10, 8, self.number)
        # texto
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13)
        offset = 32 if self.number else 12
        c.drawString(offset, 8, self.text)


class ArchBox(Flowable):
    """Caixa de componente arquitetural estilizada."""
    def __init__(self, title, items, color=BLUE, width=None, icon=""):
        super().__init__()
        self.title = title
        self.items = items
        self.color = color
        self.icon = icon
        self.width = width or (W - 4*cm)
        self.height = (1.0 + len(items) * 0.55) * cm

    def draw(self):
        c = self.canv
        w = self.width
        # fundo geral
        c.setFillColor(colors.HexColor("#0d1b3e"))
        c.roundRect(0, 0, w, self.height, 6, stroke=0, fill=1)
        # borda
        c.setStrokeColor(self.color)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, w, self.height, 6, stroke=1, fill=0)
        # cabeçalho
        c.setFillColor(self.color)
        c.roundRect(0, self.height - 0.75*cm, w, 0.75*cm, 6, stroke=0, fill=1)
        c.rect(0, self.height - 0.75*cm, w, 0.4*cm, stroke=0, fill=1)
        # título
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        label = f"{self.icon}  {self.title}" if self.icon else self.title
        c.drawString(10, self.height - 0.52*cm, label)
        # itens
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY1)
        for i, item in enumerate(self.items):
            y = self.height - 0.75*cm - (i + 1) * 0.55*cm + 0.12*cm
            # bullet
            c.setFillColor(self.color)
            c.circle(8, y + 0.15*cm, 2, stroke=0, fill=1)
            c.setFillColor(GRAY1)
            c.drawString(16, y, item)


class ArrowConnector(Flowable):
    """Seta de conexão entre componentes."""
    def __init__(self, text="", direction="down", width=None):
        super().__init__()
        self.text = text
        self.direction = direction
        self.width = width or (W - 4*cm)
        self.height = 1.0*cm

    def draw(self):
        c = self.canv
        cx = self.width / 2
        # linha pontilhada
        c.setStrokeColor(CYAN)
        c.setLineWidth(1.2)
        c.setDash([4, 3])
        c.line(cx, self.height, cx, 0.3*cm)
        c.setDash()
        # seta
        c.setFillColor(CYAN)
        c.setStrokeColor(CYAN)
        arrow = [cx - 5, 0.3*cm, cx + 5, 0.3*cm, cx, 0]
        c.polygon(arrow, stroke=0, fill=1)
        # label
        if self.text:
            c.setFillColor(GRAY2)
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx + 18, self.height / 2 - 3, self.text)


class MetricCard(Flowable):
    """Card de métrica compacto."""
    def __init__(self, value, label, color=CYAN, width=4*cm):
        super().__init__()
        self.value = value
        self.label = label
        self.color = color
        self.width = width
        self.height = 1.6*cm

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#0d1b3e"))
        c.roundRect(0, 0, self.width, self.height, 5, stroke=0, fill=1)
        c.setStrokeColor(self.color)
        c.setLineWidth(1)
        c.roundRect(0, 0, self.width, self.height, 5, stroke=1, fill=0)
        # barra topo
        c.setFillColor(self.color)
        c.rect(0, self.height - 3, self.width, 3, stroke=0, fill=1)
        # valor
        c.setFillColor(self.color)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(self.width / 2, 0.65*cm, self.value)
        # label
        c.setFillColor(GRAY2)
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.width / 2, 0.22*cm, self.label.upper())


class FullArchDiagram(Flowable):
    """Diagrama de arquitetura completo em ASCII art estilizado."""
    def __init__(self, width=None):
        super().__init__()
        self.width = width or (W - 4*cm)
        self.height = 13*cm

    def draw(self):
        c = self.canv
        w = self.width
        h = self.height
        pad = 8

        def box(x, y, bw, bh, fill_color, stroke_color, radius=5):
            c.setFillColor(fill_color)
            c.setStrokeColor(stroke_color)
            c.setLineWidth(1.2)
            c.roundRect(x, y, bw, bh, radius, stroke=1, fill=1)

        def label(x, y, text, font="Helvetica-Bold", size=8, color=WHITE, align="center"):
            c.setFillColor(color)
            c.setFont(font, size)
            if align == "center":
                c.drawCentredString(x, y, text)
            else:
                c.drawString(x, y, text)

        def arrow(x1, y1, x2, y2, color=CYAN, dash=False):
            import math
            c.setStrokeColor(color)
            c.setLineWidth(1)
            if dash:
                c.setDash([3, 2])
            else:
                c.setDash()
            c.line(x1, y1, x2, y2)
            c.setDash()
            # ponta
            angle = math.atan2(y2 - y1, x2 - x1)
            arrowLen = 7
            c.setFillColor(color)
            px1 = x2 - arrowLen * math.cos(angle - 0.4)
            py1 = y2 - arrowLen * math.sin(angle - 0.4)
            px2 = x2 - arrowLen * math.cos(angle + 0.4)
            py2 = y2 - arrowLen * math.sin(angle + 0.4)
            p = c.beginPath()
            p.moveTo(x2, y2)
            p.lineTo(px1, py1)
            p.lineTo(px2, py2)
            p.close()
            c.drawPath(p, stroke=0, fill=1)

        # fundo geral
        c.setFillColor(colors.HexColor("#04090f"))
        c.roundRect(0, 0, w, h, 8, stroke=0, fill=1)
        c.setStrokeColor(GRAY3)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, w, h, 8, stroke=1, fill=0)

        # ── Linha 1: FONTES DE DADOS (topo) ───────────────────
        y_data = h - 2.2*cm
        bw_d = 3.5*cm
        bh_d = 1.3*cm
        # Dataset
        box(pad, y_data, bw_d, bh_d, colors.HexColor("#1a2b55"), BLUE)
        label(pad + bw_d/2, y_data + bh_d/2 + 1, "LW-DATASET.xlsx", size=7.5)
        label(pad + bw_d/2, y_data + bh_d/2 - 8, "122.543 incidentes", "Helvetica", 6.5, GRAY2)
        # Monitoramento
        x2 = pad + bw_d + 0.8*cm
        box(x2, y_data, bw_d, bh_d, colors.HexColor("#1a2b55"), BLUE)
        label(x2 + bw_d/2, y_data + bh_d/2 + 1, "Monitoramento", size=7.5)
        label(x2 + bw_d/2, y_data + bh_d/2 - 8, "Alertas em tempo real", "Helvetica", 6.5, GRAY2)
        # Oracle ADB
        x3 = w - pad - bw_d
        box(x3, y_data, bw_d, bh_d, colors.HexColor("#2a1a1a"), ORANGE)
        label(x3 + bw_d/2, y_data + bh_d/2 + 1, "Oracle ADB (OCI)", size=7.5, color=ORANGE)
        label(x3 + bw_d/2, y_data + bh_d/2 - 8, "sa-saopaulo-1", "Helvetica", 6.5, GRAY2)

        # label camada
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(pad, y_data + bh_d + 5, "CAMADA DE DADOS")

        # ── Linha 2: ML ENGINE ─────────────────────────────────
        y_ml = h - 5.0*cm
        bw_ml = 4.5*cm
        bh_ml = 1.5*cm
        x_ml1 = pad
        x_ml2 = pad + bw_ml + 0.6*cm
        box(x_ml1, y_ml, bw_ml, bh_ml, colors.HexColor("#0d1f45"), PURPLE)
        label(x_ml1 + bw_ml/2, y_ml + bh_ml/2 + 3, "Modelo A — XGBoost", size=7.5, color=PURPLE)
        label(x_ml1 + bw_ml/2, y_ml + bh_ml/2 - 5, "Predicao OLA", "Helvetica", 6.5, GRAY2)
        label(x_ml1 + bw_ml/2, y_ml + bh_ml/2 - 14, "ROC-AUC 0.84 | Recall 60%", "Helvetica", 6, GRAY2)
        box(x_ml2, y_ml, bw_ml, bh_ml, colors.HexColor("#0d1f45"), GREEN)
        label(x_ml2 + bw_ml/2, y_ml + bh_ml/2 + 3, "Modelo B — RandomForest", size=7.5, color=GREEN)
        label(x_ml2 + bw_ml/2, y_ml + bh_ml/2 - 5, "Classificacao Prioridade", "Helvetica", 6.5, GRAY2)
        label(x_ml2 + bw_ml/2, y_ml + bh_ml/2 - 14, "F1-macro 0.90 | Acc 91%", "Helvetica", 6, GRAY2)
        # NLP box
        x_nlp = x_ml2 + bw_ml + 0.6*cm
        bw_nlp = w - x_nlp - pad
        box(x_nlp, y_ml, bw_nlp, bh_ml, colors.HexColor("#1a1a2e"), CYAN)
        label(x_nlp + bw_nlp/2, y_ml + bh_ml/2 + 3, "NLP — TF-IDF", size=7.5, color=CYAN)
        label(x_nlp + bw_nlp/2, y_ml + bh_ml/2 - 5, "top-50 tokens", "Helvetica", 6.5, GRAY2)
        label(x_nlp + bw_nlp/2, y_ml + bh_ml/2 - 14, "+ SMOTE balancing", "Helvetica", 6, GRAY2)

        c.setFillColor(PURPLE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(pad, y_ml + bh_ml + 5, "CAMADA ML")

        # ── Linha 3: API ───────────────────────────────────────
        y_api = h - 8.1*cm
        bw_api = w - 2*pad
        bh_api = 1.7*cm
        box(pad, y_api, bw_api, bh_api, colors.HexColor("#05132e"), BLUE)
        # título
        c.setFillColor(BLUE)
        c.roundRect(pad, y_api + bh_api - 0.55*cm, bw_api, 0.55*cm, 5, stroke=0, fill=1)
        c.rect(pad, y_api + bh_api - 0.55*cm, bw_api, 0.3*cm, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(pad + 10, y_api + bh_api - 0.38*cm, "API REST — FastAPI  |  Railway.app Docker  |  aria-api-production.up.railway.app")
        # endpoints
        endpoints = [
            ("GET /health", CYAN),
            ("POST /predict/ola", GREEN),
            ("POST /predict/priority", GREEN),
            ("GET /predictions/ola", ORANGE),
            ("GET /encoders/info", GRAY2),
        ]
        ep_w = (bw_api - 20) / len(endpoints)
        for i, (ep, col) in enumerate(endpoints):
            ex = pad + 10 + i * ep_w
            ey = y_api + 0.15*cm
            c.setFillColor(colors.HexColor("#0d2050"))
            c.roundRect(ex, ey, ep_w - 4, 0.9*cm, 3, stroke=0, fill=1)
            c.setStrokeColor(col)
            c.setLineWidth(0.8)
            c.roundRect(ex, ey, ep_w - 4, 0.9*cm, 3, stroke=1, fill=0)
            c.setFillColor(col)
            c.setFont("Courier-Bold", 6.5)
            c.drawCentredString(ex + (ep_w - 4)/2, ey + 0.22*cm, ep)

        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(pad, y_api + bh_api + 5, "CAMADA API")

        # ── Linha 4: DASHBOARD ─────────────────────────────────
        y_dash = h - 11.2*cm
        bw_dash = w - 2*pad
        bh_dash = 1.7*cm
        box(pad, y_dash, bw_dash, bh_dash, colors.HexColor("#04101f"), CYAN)
        c.setFillColor(CYAN)
        c.roundRect(pad, y_dash + bh_dash - 0.55*cm, bw_dash, 0.55*cm, 5, stroke=0, fill=1)
        c.rect(pad, y_dash + bh_dash - 0.55*cm, bw_dash, 0.3*cm, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(pad + 10, y_dash + bh_dash - 0.38*cm, "DASHBOARD — Streamlit Cloud  |  afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app")
        pages = ["Home", "KPI Overview", "Incidentes", "Preditor OLA", "Padroes", "API Live"]
        pg_w = (bw_dash - 20) / len(pages)
        pg_colors = [BLUE, CYAN, ORANGE, GREEN, PURPLE, BLUE2]
        for i, (pg, col) in enumerate(zip(pages, pg_colors)):
            px = pad + 10 + i * pg_w
            py = y_dash + 0.15*cm
            c.setFillColor(colors.HexColor("#071a38"))
            c.roundRect(px, py, pg_w - 4, 0.9*cm, 3, stroke=0, fill=1)
            c.setStrokeColor(col)
            c.setLineWidth(0.8)
            c.roundRect(px, py, pg_w - 4, 0.9*cm, 3, stroke=1, fill=0)
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(px + (pg_w - 4)/2, py + 0.22*cm, pg)

        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(pad, y_dash + bh_dash + 5, "CAMADA APRESENTACAO")

        # ── Setas ──────────────────────────────────────────────
        # dataset → modelo A
        cx1 = pad + bw_d / 2
        arrow(cx1, y_data, cx1, y_ml + bh_ml, BLUE)
        # monitoring → modelo B
        cx2 = pad + bw_d + 0.8*cm + bw_d/2
        arrow(cx2, y_data, x_ml2 + bw_ml/2, y_ml + bh_ml, BLUE)
        # ML → API
        arrow(x_ml1 + bw_ml/2, y_ml, x_ml1 + bw_ml/2, y_api + bh_api, GREEN)
        arrow(x_ml2 + bw_ml/2, y_ml, x_ml2 + bw_ml/2, y_api + bh_api, GREEN)
        # API → Oracle (bidirectional)
        arrow(w - pad - bw_d/2, y_data + bh_d/2, w - pad - bw_d/2 + 0, y_api + bh_api, ORANGE, dash=True)
        # API → Dashboard
        arrow(w/2, y_api, w/2, y_dash + bh_dash, CYAN)


class DataFlowTable(Flowable):
    """Diagrama de fluxo de dados horizontal."""
    def __init__(self, width=None):
        super().__init__()
        self.width = width or (W - 4*cm)
        self.height = 2.8*cm

    def draw(self):
        c = self.canv
        w = self.width
        steps = [
            ("INPUT", "IncidentInput\nJSON payload", BLUE),
            ("ENCODE", "LabelEncoder\n+ TF-IDF", PURPLE),
            ("MERGE", "scipy.sparse\nhstack()", CYAN),
            ("PREDICT", "XGBoost /\nRandomForest", GREEN),
            ("PERSIST", "Oracle ADB\ninsert()", ORANGE),
            ("OUTPUT", "OLAPrediction\nJSON response", BLUE2),
        ]
        bw = (w - 10) / len(steps) - 4
        bh = 1.8*cm

        for i, (title, desc, col) in enumerate(steps):
            x = 5 + i * (bw + 4)
            y = 0.5*cm
            c.setFillColor(colors.HexColor("#0d1b3e"))
            c.roundRect(x, y, bw, bh, 4, stroke=0, fill=1)
            c.setStrokeColor(col)
            c.setLineWidth(1)
            c.roundRect(x, y, bw, bh, 4, stroke=1, fill=0)
            c.setFillColor(col)
            c.rect(x, y + bh - 3, bw, 3, stroke=0, fill=1)
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(x + bw/2, y + bh - 0.45*cm, title)
            c.setFillColor(GRAY1)
            c.setFont("Helvetica", 6.5)
            for j, line in enumerate(desc.split("\n")):
                c.drawCentredString(x + bw/2, y + bh - 0.85*cm - j*0.35*cm, line)
            # seta
            if i < len(steps) - 1:
                ax = x + bw + 1
                ay = y + bh/2
                c.setFillColor(GRAY2)
                c.setStrokeColor(GRAY2)
                c.setLineWidth(0.8)
                c.line(ax, ay, ax + 2, ay)
                p2 = c.beginPath()
                p2.moveTo(ax + 2, ay)
                p2.lineTo(ax - 1, ay + 4)
                p2.lineTo(ax - 1, ay - 4)
                p2.close()
                c.drawPath(p2, stroke=0, fill=1)


# ── Helpers de conteúdo ──────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY3, spaceAfter=6, spaceBefore=2)

def spacer(h=0.3):
    return Spacer(1, h*cm)

def bullet(text, color=CYAN):
    marker = f'<font color="#{color.hexval()[2:] if hasattr(color,"hexval") else "00D4FF"}">▸</font>'
    return Paragraph(f'{marker} {text}', sBullet)

def tag_table(tags):
    """Linha de tags coloridas."""
    cells = []
    tag_colors = [BLUE, PURPLE, GREEN, ORANGE, CYAN, BLUE2]
    for i, t in enumerate(tags):
        col = tag_colors[i % len(tag_colors)]
        cells.append(Paragraph(t, ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=7,
                                                  textColor=WHITE, alignment=TA_CENTER,
                                                  backColor=col, borderPadding=3)))
    t = Table([cells], colWidths=[3.2*cm]*len(tags))
    t.setStyle(TableStyle([
        ("ALIGN",    (0,0), (-1,-1), "CENTER"),
        ("VALIGN",   (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.transparent]),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 2),
        ("RIGHTPADDING",  (0,0), (-1,-1), 2),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

def kv_table(rows, col_widths=None):
    """Tabela chave-valor estilizada."""
    data = [[Paragraph(f'<b><font color="#00D4FF">{k}</font></b>', sBody),
             Paragraph(v, sBody)] for k, v in rows]
    cw = col_widths or [4.5*cm, 11.5*cm]
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), colors.HexColor("#0a1628")),
        ("BACKGROUND",  (0,0), (0,-1), colors.HexColor("#0d1b3e")),
        ("TEXTCOLOR",   (0,0), (-1,-1), GRAY1),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
        ("GRID",        (0,0), (-1,-1), 0.4, GRAY3),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ]))
    return t

def metrics_row(cards):
    """Linha de cards de métricas."""
    row = [MetricCard(*c) for c in cards]
    cw = [4.0*cm] * len(row)
    t = Table([row], colWidths=cw)
    t.setStyle(TableStyle([
        ("ALIGN",   (0,0), (-1,-1), "CENTER"),
        ("VALIGN",  (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    return t

def endpoint_table(rows):
    header = [
        Paragraph("<b>Método</b>", ParagraphStyle("eh", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN, alignment=TA_CENTER)),
        Paragraph("<b>Endpoint</b>", ParagraphStyle("eh", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN)),
        Paragraph("<b>Descrição</b>", ParagraphStyle("eh", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN)),
        Paragraph("<b>Resposta</b>", ParagraphStyle("eh", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN)),
    ]
    data = [header]
    method_colors = {"GET": GREEN, "POST": ORANGE}
    for method, route, desc, resp in rows:
        col = method_colors.get(method, BLUE)
        data.append([
            Paragraph(f'<b><font color="#{col.hexval()[2:]}">{method}</font></b>',
                      ParagraphStyle("mc", fontName="Helvetica-Bold", fontSize=8, alignment=TA_CENTER)),
            Paragraph(f'<font name="Courier" size="8" color="#00D4FF">{route}</font>', sBody),
            Paragraph(desc, sBody),
            Paragraph(f'<font name="Courier" size="7" color="#8899bb">{resp}</font>', sBody),
        ])
    t = Table(data, colWidths=[1.5*cm, 4.5*cm, 6.0*cm, 4.0*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#0d1b3e")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
        ("GRID",        (0,0), (-1,-1), 0.4, GRAY3),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN",       (0,0), (0,-1), "CENTER"),
    ]))
    return t

def db_table(table_name, columns, color=ORANGE):
    header = [
        Paragraph(f'<b><font color="#{color.hexval()[2:]}">{table_name}</font></b>',
                  ParagraphStyle("dh", fontName="Helvetica-Bold", fontSize=9, textColor=color)),
        Paragraph("<b>Tipo</b>", ParagraphStyle("dh2", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN)),
        Paragraph("<b>Descrição</b>", ParagraphStyle("dh3", fontName="Helvetica-Bold", fontSize=8, textColor=CYAN)),
    ]
    data = [header] + [
        [Paragraph(f'<font name="Courier" size="8" color="#00D4FF">{col}</font>', sBody),
         Paragraph(f'<font name="Courier" size="7.5" color="#8899bb">{tp}</font>', sBody),
         Paragraph(desc, sBody)]
        for col, tp, desc in columns
    ]
    t = Table(data, colWidths=[4.5*cm, 3.5*cm, 8.0*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a0f05")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
        ("GRID",        (0,0), (-1,-1), 0.4, GRAY3),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",   (0,0), (-1,0), 1.2, color),
    ]))
    return t


# ── Page Template ────────────────────────────────────────────
PAGE_NUM = [0]

def on_page(c, doc):
    PAGE_NUM[0] += 1
    c.saveState()
    # fundo
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # linha topo
    c.setFillColor(CYAN)
    c.rect(0, H - 3, W, 3, stroke=0, fill=1)
    # linha rodapé
    c.setFillColor(GRAY3)
    c.rect(2*cm, 1.2*cm, W - 4*cm, 0.5, stroke=0, fill=1)
    # rodapé esquerda
    c.setFillColor(GRAY2)
    c.setFont("Helvetica", 7)
    c.drawString(2*cm, 0.7*cm, "ARIA AIOps — Arquitetura Técnica  |  Confidencial  |  FIAP Enterprise Challenge 2026")
    # rodapé direita — página
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - 2*cm, 0.7*cm, f"{PAGE_NUM[0]}")
    c.restoreState()


def on_first_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.restoreState()


# ── Conteúdo ─────────────────────────────────────────────────
story = []

# ── CAPA ─────────────────────────────────────────────────────
# Gradiente simulado via retângulos
story.append(Spacer(1, 5.5*cm))

# Logo / título
story.append(Paragraph("ARIA", ParagraphStyle("logo", fontName="Helvetica-Bold", fontSize=64,
                                               textColor=CYAN, leading=72, alignment=TA_CENTER)))
story.append(Paragraph("AIOps Platform", ParagraphStyle("logosub", fontName="Helvetica",
                                                          fontSize=18, textColor=GRAY2,
                                                          leading=22, alignment=TA_CENTER)))
story.append(spacer(0.5))
story.append(HRFlowable(width="60%", thickness=1.5, color=CYAN, spaceAfter=8,
                         spaceBefore=8, hAlign="CENTER"))
story.append(Paragraph("Documento de Arquitetura Técnica", ParagraphStyle(
    "subtitle", fontName="Helvetica-Bold", fontSize=16, textColor=WHITE,
    leading=20, alignment=TA_CENTER)))
story.append(Paragraph("Automated Response &amp; Incident Analysis", ParagraphStyle(
    "subtitle2", fontName="Helvetica", fontSize=11, textColor=GRAY2,
    leading=14, alignment=TA_CENTER, spaceAfter=6)))

story.append(spacer(3.5))

# Caixa de info
info_data = [
    [Paragraph("<b>Versão</b>", ParagraphStyle("iv", fontName="Helvetica-Bold", fontSize=9, textColor=CYAN, alignment=TA_CENTER)),
     Paragraph("<b>Data</b>", ParagraphStyle("iv", fontName="Helvetica-Bold", fontSize=9, textColor=CYAN, alignment=TA_CENTER)),
     Paragraph("<b>Equipe</b>", ParagraphStyle("iv", fontName="Helvetica-Bold", fontSize=9, textColor=CYAN, alignment=TA_CENTER)),
     Paragraph("<b>Projeto</b>", ParagraphStyle("iv", fontName="Helvetica-Bold", fontSize=9, textColor=CYAN, alignment=TA_CENTER))],
    [Paragraph("3.0.0", ParagraphStyle("iv2", fontName="Helvetica", fontSize=9, textColor=GRAY1, alignment=TA_CENTER)),
     Paragraph("Abril / 2026", ParagraphStyle("iv2", fontName="Helvetica", fontSize=9, textColor=GRAY1, alignment=TA_CENTER)),
     Paragraph("Cluster 3 — 2TSCO", ParagraphStyle("iv2", fontName="Helvetica", fontSize=9, textColor=GRAY1, alignment=TA_CENTER)),
     Paragraph("FIAP Enterprise Challenge", ParagraphStyle("iv2", fontName="Helvetica", fontSize=9, textColor=GRAY1, alignment=TA_CENTER))],
]
info_t = Table(info_data, colWidths=[3.5*cm]*4, hAlign="CENTER")
info_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0d1b3e")),
    ("BACKGROUND",   (0,1), (-1,1), colors.HexColor("#081224")),
    ("GRID",         (0,0), (-1,-1), 0.5, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 7),
    ("BOTTOMPADDING",(0,0), (-1,-1), 7),
    ("LINEABOVE",    (0,0), (-1,0), 1.5, CYAN),
    ("LINEBELOW",    (0,-1),(-1,-1),1.5, CYAN),
]))
story.append(info_t)
story.append(spacer(0.6))
story.append(Paragraph('"Resposta certa, no tempo certo, pelo caminho certo."',
                        ParagraphStyle("tagline", fontName="Helvetica", fontSize=10, textColor=GRAY2,
                                        alignment=TA_CENTER, leading=14)))

story.append(PageBreak())

# ── SUMÁRIO ───────────────────────────────────────────────────
story.append(SectionHeader("SUMÁRIO", ""))
story.append(spacer(0.3))

toc_items = [
    ("01", "Visão Geral do Sistema", "3"),
    ("02", "Diagrama de Arquitetura", "4"),
    ("03", "Camada de Dados", "5"),
    ("04", "Camada de Machine Learning", "6"),
    ("05", "Camada de API REST", "7"),
    ("06", "Camada de Dashboard", "8"),
    ("07", "Fluxo de Dados", "9"),
    ("08", "Banco de Dados Oracle ADB", "10"),
    ("09", "Infraestrutura e Deploy", "11"),
    ("10", "Métricas e Qualidade", "12"),
]

toc_data = []
for num, title, page in toc_items:
    toc_data.append([
        Paragraph(f'<font color="#00D4FF"><b>{num}</b></font>', ParagraphStyle("tn", fontName="Helvetica-Bold", fontSize=9, textColor=CYAN)),
        Paragraph(title, ParagraphStyle("tt", fontName="Helvetica", fontSize=9, textColor=GRAY1)),
        Paragraph(page, ParagraphStyle("tp", fontName="Helvetica-Bold", fontSize=9, textColor=GRAY2, alignment=TA_RIGHT)),
    ])
toc_t = Table(toc_data, colWidths=[1.2*cm, 12.5*cm, 1.8*cm])
toc_t.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#081224"), colors.HexColor("#0a1628")]),
    ("TOPPADDING",    (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ("LINEBELOW",     (0,0), (-1,-1), 0.3, GRAY3),
    ("LINEBELOW",     (0,4), (-1,4), 1, BLUE),
]))
story.append(toc_t)

story.append(PageBreak())

# ── 01 VISÃO GERAL ────────────────────────────────────────────
story.append(SectionHeader("VISÃO GERAL DO SISTEMA", "01"))
story.append(spacer(0.3))

story.append(Paragraph("Contexto e Problema", sH2))
story.append(Paragraph(
    "A Locaweb registra <b>122.543 incidentes por ano</b>, dos quais 85% são abertos automaticamente por "
    "monitoramento. Apesar disso, <b>248 violações de OLA</b> (0,97% dos elegíveis para KPI) ocorrem — "
    "concentradas especialmente no <b>Team14 (75%)</b> — causando penalidades contratuais e sobrecarga "
    "nas equipes NOC. A ausência de predição antecipada força as equipes a agir <i>reativamente</i>.", sBody))
story.append(spacer(0.2))

story.append(Paragraph("Solução ARIA", sH2))
story.append(Paragraph(
    "ARIA (Automated Response &amp; Incident Analysis) é uma plataforma AIOps que <b>prediz violações de OLA "
    "antes que aconteçam</b> e classifica automaticamente a prioridade de incidentes, centralizando a gestão "
    "operacional em um dashboard analítico com integração de API REST.", sBody))
story.append(spacer(0.2))

story.append(metrics_row([
    ("122.543", "Incidentes/ano", BLUE),
    ("248", "Violações OLA", ORANGE),
    ("0.84", "ROC-AUC Modelo A", GREEN),
    ("91%", "Acurácia Modelo B", PURPLE),
]))
story.append(spacer(0.4))

story.append(Paragraph("Componentes Principais", sH2))
story.append(kv_table([
    ("Dataset",    "LW-DATASET.xlsx — 122.543 incidentes Locaweb (Jan/2023–Dez/2025), 19 colunas"),
    ("Modelo A",   "XGBoost + SMOTE — predição binária de violação OLA (ROC-AUC 0.84, Recall 60%)"),
    ("Modelo B",   "Random Forest — classificação multiclasse de prioridade 2/3/4 (F1-macro 0.90)"),
    ("NLP",        "TF-IDF top-50 tokens em descrição de incidente, concatenado às features numéricas via scipy.sparse"),
    ("API REST",   "FastAPI + Uvicorn, 5 endpoints, Swagger automático, deploy Railway.app (Docker)"),
    ("Dashboard",  "Streamlit 6 páginas + Plotly (glassmorphism), deploy Streamlit Community Cloud"),
    ("Banco",      "Oracle Autonomous DB (OCI, Always Free, sa-saopaulo-1) — thin mode sem Oracle Client"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Stack Tecnológico", sH2))
story.append(tag_table(["Python 3.11", "FastAPI", "Streamlit", "XGBoost", "Random Forest", "Oracle ADB"]))
story.append(spacer(0.2))
story.append(tag_table(["Pandas/NumPy", "scikit-learn", "imbalanced-learn", "scipy.sparse", "TF-IDF", "reportlab"]))
story.append(spacer(0.2))
story.append(tag_table(["Railway.app", "Docker", "Streamlit Cloud", "OCI Always Free", "oracledb thin", "GitHub Actions"]))

story.append(PageBreak())

# ── 02 DIAGRAMA ───────────────────────────────────────────────
story.append(SectionHeader("DIAGRAMA DE ARQUITETURA", "02"))
story.append(spacer(0.3))
story.append(Paragraph("Visão geral das camadas e conexões do sistema ARIA.", sCaption))
story.append(spacer(0.2))
story.append(FullArchDiagram())
story.append(spacer(0.3))
story.append(Paragraph(
    "O sistema é organizado em <b>4 camadas independentes</b>: Dados, ML, API e Dashboard. "
    "A separação de responsabilidades permite substituir componentes individuais sem impactar o restante. "
    "O Oracle ADB persiste predições de forma assíncrona — a API continua operando mesmo se o banco estiver "
    "indisponível (fallback offline silencioso).", sBody))
story.append(spacer(0.3))

story.append(Paragraph("Tecnologias por Camada", sH2))
layers = [
    ["Camada", "Tecnologia", "Deploy", "Responsabilidade"],
    ["Dados", "Pandas + OpenPyXL", "Local / Railway", "Ingestão, limpeza, feature engineering"],
    ["ML", "XGBoost + RandomForest + TF-IDF + SMOTE", "Railway (pkl)", "Treinamento e inferência"],
    ["API", "FastAPI + Uvicorn + Pydantic", "Railway.app (Docker)", "Exposição dos modelos via HTTP REST"],
    ["Dashboard", "Streamlit + Plotly", "Streamlit Cloud", "Visualização analítica e predição interativa"],
    ["Banco", "Oracle ADB + oracledb thin", "OCI Always Free", "Persistência e histórico de predições"],
]
layer_t = Table(layers, colWidths=[2.5*cm, 5.5*cm, 3.5*cm, 4.5*cm])
layer_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0d1b3e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), CYAN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, CYAN),
]))
story.append(layer_t)

story.append(PageBreak())

# ── 03 DADOS ──────────────────────────────────────────────────
story.append(SectionHeader("CAMADA DE DADOS", "03"))
story.append(spacer(0.3))

story.append(Paragraph("Dataset Principal — LW-DATASET.xlsx", sH2))
story.append(Paragraph(
    "O dataset oficial da Locaweb contém o histórico completo de incidentes de TI. "
    "Utilizado tanto para treinamento dos modelos quanto para alimentar o dashboard analítico.", sBody))
story.append(spacer(0.2))
story.append(kv_table([
    ("Arquivo",     "LW-DATASET.xlsx  |  Sheet: Dataset Geral"),
    ("Volume",      "122.543 registros  |  19 colunas originais"),
    ("Período",     "Janeiro/2023 – Dezembro/2025"),
    ("Loader",      "dashboard/utils/data_loader.py → load_data() com @st.cache_data"),
    ("Biblioteca",  "pandas.read_excel(engine='openpyxl') + normalização de colunas via str.strip()"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Feature Engineering — Colunas Derivadas", sH2))
feat_data = [
    ["Feature", "Origem", "Tipo", "Descrição"],
    ["hora_abertura", "data_hora_abertura", "int 0-23", "Hora de abertura do incidente"],
    ["dia_semana", "data_hora_abertura", "int 0-6", "0=Segunda … 6=Domingo"],
    ["mes", "data_hora_abertura", "int 1-12", "Mês de abertura"],
    ["is_monitoring", "Aberto por", "bool 0/1", "1 se aberto por sistema de monitoramento automático"],
    ["has_parent", "Incidente Pai", "bool 0/1", "1 se incidente possui incidente pai vinculado"],
    ["prio_num", "Prioridade", "int 1-5", "Prioridade numérica (1=Crítica, 5=Muito Baixa)"],
    ["produto_enc", "Produto", "int", "LabelEncoder — 52 produtos distintos"],
    ["grupo_enc", "Grupo designado", "int", "LabelEncoder — 17 grupos (Team14 domina com 75%)"],
    ["categoria_enc", "Categoria", "int", "LabelEncoder — 142 categorias"],
    ["subcategoria_enc", "Subcategoria", "int", "LabelEncoder — encoder salvo em encoders.pkl"],
    ["cod_fechamento_enc", "Codigo de fechamento", "int", "LabelEncoder — código de resolução"],
]
feat_t = Table(feat_data, colWidths=[3.8*cm, 4.0*cm, 2.0*cm, 6.2*cm])
feat_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0d1b3e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), CYAN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (0,-1), CYAN),
    ("TEXTCOLOR",    (1,1), (-1,-1), GRAY1),
    ("FONTNAME",     (0,1), (0,-1), "Courier"),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, CYAN),
]))
story.append(feat_t)
story.append(spacer(0.3))

story.append(Paragraph("Critérios de Elegibilidade para KPI OLA", sH2))
story.append(Paragraph(
    "Apenas incidentes <b>elegíveis para KPI</b> entram no dataset de treino do Modelo A. "
    "São excluídos: incidentes com status <i>Sem Intervenção Humana</i> e incidentes com <i>Incidente Pai</i> preenchido.", sBody))
story.append(spacer(0.1))
story.append(kv_table([
    ("Elegíveis para KPI",  "25.600 incidentes (21% do total)"),
    ("Com violação OLA",    "248 incidentes (0,97% dos elegíveis)"),
    ("SLA Prio 2 (Alta)",   "≤ 4 horas — 42 violações"),
    ("SLA Prio 3 (Média)",  "≤ 12 horas — 206 violações"),
    ("SLA Prio 4 (Baixa)",  "≤ 24 horas"),
]))

story.append(PageBreak())

# ── 04 ML ─────────────────────────────────────────────────────
story.append(SectionHeader("CAMADA DE MACHINE LEARNING", "04"))
story.append(spacer(0.3))

story.append(Paragraph("Modelo A — Predição de Violação OLA (XGBoost)", sH2))
story.append(kv_table([
    ("Arquivo PKL",    "model/model_ola.pkl"),
    ("Algoritmo",      "XGBClassifier (binary:logistic) com SMOTE para balanceamento de classes"),
    ("Dataset treino", "20.480 instâncias (80% de 25.600 elegíveis para KPI)"),
    ("SMOTE",          "Após oversampling: 20.282 positivos sintéticos vs 20.282 negativos — proporção 1:1"),
    ("Features",       "11 numéricas + TF-IDF top-50 tokens = vetor de 61 dimensões (scipy.sparse)"),
    ("ROC-AUC",        "0.8382  |  Recall violações: 60%  |  Precision: 4% (trade-off de negócio)"),
    ("Trade-off",      "Precision baixa é aceitável — melhor alertar falso positivo do que perder violação real"),
]))
story.append(spacer(0.2))
story.append(Paragraph("Top 10 Features — Modelo A", sH3))

feat_a = [
    ["Feature", "Importância", "Interpretação"],
    ["domain (TF-IDF)", "11.85%", "Incidentes com 'domain' têm alta correlação com violação OLA"],
    ["not running (TF-IDF)", "7.78%", "Serviço inativo associado a violações críticas"],
    ["recipes (TF-IDF)", "7.15%", "Token específico de produto Locaweb de alto risco"],
    ["is_monitoring", "5.40%", "Incidentes de monitoramento tendem a violar mais OLA"],
    ["on (TF-IDF)", "4.83%", "Indicador de contexto operacional"],
    ["grupo_enc", "3.99%", "Grupo designado — Team14 concentra 75% dos incidentes"],
    ["on port (TF-IDF)", "3.84%", "Problemas de porta/rede frequentemente violam OLA"],
    ["error backup (TF-IDF)", "3.57%", "Erros de backup têm padrão de violação específico"],
    ["prio_num", "2.51%", "Prioridade numérica — prio 2 tem SLA mais curto"],
]
feat_a_t = Table(feat_a, colWidths=[4.5*cm, 2.5*cm, 9.0*cm])
feat_a_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#1a0a2e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), PURPLE),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("TEXTCOLOR",    (1,1), (1,-1), GREEN),
    ("FONTNAME",     (0,1), (0,-1), "Courier"),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, PURPLE),
]))
story.append(feat_a_t)
story.append(spacer(0.3))

story.append(Paragraph("Modelo B — Classificação de Prioridade (Random Forest)", sH2))
story.append(kv_table([
    ("Arquivo PKL",    "model/model_priority.pkl"),
    ("Algoritmo",      "RandomForestClassifier — classificação multiclasse (2=Alta, 3=Média, 4=Baixa)"),
    ("Dataset treino", "97.767 instâncias (80% de 122.209 incidentes com prio 2-4)"),
    ("Features",       "11 numéricas + TF-IDF top-50 tokens = 61 dimensões (scipy.sparse)"),
    ("F1-macro",       "0.8981  |  F1-weighted: 0.9084  |  Accuracy: 91.0%"),
    ("Prio 2 (Alta)",  "Precision 84% | Recall 93% | F1 88%  — 3.130 instâncias teste"),
    ("Prio 3 (Média)", "Precision 84% | Recall 94% | F1 88%  — 8.346 instâncias teste"),
    ("Prio 4 (Baixa)", "Precision 98% | Recall 88% | F1 93%  — 12.966 instâncias teste"),
]))
story.append(spacer(0.2))

story.append(Paragraph("Formato do Bundle PKL — Padrão de Inferência", sH2))
story.append(Paragraph("Ambos os modelos são salvos no mesmo formato de bundle dict:", sBody))
story.append(Paragraph('bundle = {"model": clf, "tfidf": TfidfVectorizer, "features": [lista_features]}', sCode))
story.append(Paragraph("Inferência:", sH3))
story.append(Paragraph('num = np.array([[row.get(f, 0) for f in feats]])  # shape (1, 11)', sCode))
story.append(Paragraph('txt = tfidf.transform([row.get("descricao", "")])  # shape (1, 50)', sCode))
story.append(Paragraph('X   = scipy.sparse.hstack([num, txt])              # shape (1, 61)', sCode))
story.append(Paragraph('proba = model.predict_proba(X)[0][1]               # Modelo A — prob. violação', sCode))
story.append(Paragraph('pred  = model.predict(X)[0]                        # Modelo B — prio 2/3/4', sCode))

story.append(PageBreak())

# ── 05 API ────────────────────────────────────────────────────
story.append(SectionHeader("CAMADA DE API REST", "05"))
story.append(spacer(0.3))

story.append(Paragraph("Visão Geral", sH2))
story.append(kv_table([
    ("Framework",    "FastAPI 0.104+  |  Uvicorn ASGI server  |  Python 3.11"),
    ("Deploy",       "Railway.app (Docker)  |  URL: aria-api-production.up.railway.app"),
    ("Documentação", "/docs (Swagger UI)  |  /redoc (ReDoc)"),
    ("CORS",         "allow_origins=['*'] — aceita requisições de qualquer origem"),
    ("Modelos",      "Carregados via joblib no startup — persistem em memória para baixa latência"),
    ("Banco",        "Escrita assíncrona no Oracle ADB — falha silenciosa se offline"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Endpoints Disponíveis", sH2))
story.append(endpoint_table([
    ("GET",  "/health",             "Status da API, modelos e conexão DB",      '{"status":"ok","modelos_carregados":true}'),
    ("POST", "/predict/ola",        "Probabilidade de violação OLA (0-100%)",   '{"probabilidade":0.72,"nivel_risco":"ALTO"}'),
    ("POST", "/predict/priority",   "Classificação de prioridade (2/3/4)",      '{"prioridade_predita":2,"label":"2 - Alta"}'),
    ("GET",  "/predictions/ola",    "Histórico de predições no Oracle ADB",     '[{"numero":"...","probabilidade":...}]'),
    ("GET",  "/encoders/info",      "Valores válidos nos LabelEncoders",        '{"produto":["Hospedagem",...],...}'),
]))
story.append(spacer(0.3))

story.append(Paragraph("Schema de Entrada — IncidentInput (Pydantic)", sH2))
story.append(Paragraph("Todos os campos numéricos têm valor default 0 para facilitar testes parciais:", sBody))
input_fields = [
    ["Campo", "Tipo", "Padrão", "Descrição"],
    ["prio_num", "int", "—", "Prioridade numérica 1-5 (obrigatório)"],
    ["hora_abertura", "int", "0", "Hora de abertura 0-23"],
    ["dia_semana", "int", "0", "Dia da semana 0-6 (0=Segunda)"],
    ["mes", "int", "1", "Mês 1-12"],
    ["is_monitoring", "int", "0", "1 se aberto por monitoramento automático"],
    ["has_parent", "int", "0", "1 se possui incidente pai"],
    ["produto_enc", "int", "0", "Produto codificado (ou use campo produto: str)"],
    ["grupo_enc", "int", "0", "Grupo codificado (ou use campo grupo: str)"],
    ["categoria_enc", "int", "0", "Categoria codificada"],
    ["subcategoria_enc", "int", "0", "Subcategoria codificada"],
    ["cod_fechamento_enc", "int", "0", "Código de fechamento codificado"],
    ["descricao", "str", '""', "Texto livre do incidente (NLP TF-IDF)"],
    ["numero", "str|None", "None", "Número do incidente para rastreabilidade"],
]
inp_t = Table(input_fields, colWidths=[4.0*cm, 2.0*cm, 2.0*cm, 8.0*cm])
inp_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#05132e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), BLUE2),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("FONTNAME",     (0,1), (0,-1), "Courier"),
    ("TEXTCOLOR",    (0,1), (0,-1), CYAN),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, BLUE2),
]))
story.append(inp_t)
story.append(spacer(0.3))

story.append(Paragraph("Exemplo cURL — Predição OLA", sH2))
curl_lines = [
    'curl -X POST https://aria-api-production.up.railway.app/predict/ola \\',
    '  -H "Content-Type: application/json" \\',
    '  -d \'{"prio_num": 2, "hora_abertura": 9, "dia_semana": 0, "mes": 4,',
    '       "is_monitoring": 1, "has_parent": 0, "produto_enc": 0, "grupo_enc": 0,',
    '       "descricao": "Servidor de producao fora do ar"}\'',
]
for line in curl_lines:
    story.append(Paragraph(line, sCode))

story.append(PageBreak())

# ── 06 DASHBOARD ──────────────────────────────────────────────
story.append(SectionHeader("CAMADA DE DASHBOARD", "06"))
story.append(spacer(0.3))

story.append(Paragraph("Visão Geral", sH2))
story.append(kv_table([
    ("Framework",    "Streamlit 1.28+  |  Plotly (gráficos interativos)"),
    ("Deploy",       "Streamlit Community Cloud  |  afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app"),
    ("Entry point",  "streamlit_app.py (raiz do repo) — redireciona para dashboard/app.py"),
    ("Tema",         "Glassmorphism dark — NAVY (#050e1f) + CYAN (#00D4FF) + gradientes azul"),
    ("Multi-page",   "Stubs em pages/ (raiz) fazem exec() das páginas reais em dashboard/pages/"),
    ("Gráficos",     "config={'scrollZoom': False} em todos os charts para não capturar scroll da página"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Estrutura das 6 Páginas", sH2))
pages_data = [
    ["Página", "URL", "Arquivo", "Conteúdo Principal"],
    ["Home", "/", "dashboard/app.py", "KPIs globais, overview modelos, links de navegação"],
    ["KPI Overview", "/kpi_overview", "1_kpi_overview.py", "6 gráficos: volume temporal, distribuição prioridade, heatmap, violações OLA"],
    ["Incidentes", "/incident_list", "2_incident_list.py", "Tabela filtrável por ano/grupo/prioridade, badges coloridos, export CSV"],
    ["Preditor OLA", "/ola_predictor", "3_ola_predictor.py", "Formulário interativo → gauge de probabilidade + nível de risco + recomendação"],
    ["Padrões", "/patterns", "4_patterns.py", "Heatmaps hora×dia, análise Team14, padrões recorrentes por produto/categoria"],
    ["API Live", "/api_predictor", "5_api_predictor.py", "3 abas: predição via API, histórico Oracle ADB, documentação de uso"],
]
pages_t = Table(pages_data, colWidths=[2.5*cm, 2.8*cm, 3.8*cm, 6.9*cm])
pages_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#04101f")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), CYAN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("FONTNAME",     (1,1), (2,-1), "Courier"),
    ("TEXTCOLOR",    (1,1), (2,-1), CYAN),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, CYAN),
]))
story.append(pages_t)
story.append(spacer(0.3))

story.append(Paragraph("Sistema de Tema (theme.py)", sH2))
story.append(Paragraph("Todas as páginas importam e aplicam o tema centralizado:", sBody))
story.append(Paragraph('from dashboard.utils.theme import inject_css, kpi_card, apply_plotly_theme', sCode))
story.append(Paragraph('inject_css()  # injeta ARIA_CSS via st.markdown(unsafe_allow_html=True)', sCode))
story.append(spacer(0.1))
story.append(kv_table([
    ("PLOTLY_LAYOUT",  "paper_bgcolor/plot_bgcolor transparentes, dragmode=False, title=dict(text=''), gridlines rgba"),
    ("inject_css()",   "Injeta ~320 linhas de CSS: fundo gradiente, glassmorphism, sidebar, KPI cards, tabs, inputs"),
    ("kpi_card()",     "Retorna HTML de card KPI com borda colorida, valor grande e sub-label"),
    ("apply_plotly_theme()", "Aplica PLOTLY_LAYOUT a qualquer figura Plotly via fig.update_layout()"),
], col_widths=[4.0*cm, 12*cm]))

story.append(PageBreak())

# ── 07 FLUXO DE DADOS ─────────────────────────────────────────
story.append(SectionHeader("FLUXO DE DADOS", "07"))
story.append(spacer(0.3))

story.append(Paragraph("Pipeline de Predição (Requisição ao /predict/ola)", sH2))
story.append(DataFlowTable())
story.append(spacer(0.2))
story.append(Paragraph(
    "O fluxo completo de uma requisição de predição ocorre em <b>&lt;100ms</b>: "
    "o payload JSON é validado pelo Pydantic, as strings opcionais são re-encodadas pelo LabelEncoder, "
    "as features numéricas e o TF-IDF são concatenados via scipy.sparse.hstack, "
    "o modelo prediz a probabilidade, e o resultado é persistido assincronamente no Oracle ADB.", sBody))
story.append(spacer(0.3))

story.append(Paragraph("Pipeline de Treinamento (model/aria_model.py)", sH2))
train_steps = [
    ("1. Ingestão",    "pd.read_excel(LW-DATASET.xlsx) → normalização de colunas → dtype_map"),
    ("2. Cleaning",    "Remoção de NaN em colunas críticas → conversão de tipos → strip de strings"),
    ("3. Features",    "Extração de hora/dia/mês → flags is_monitoring / has_parent → prio_num"),
    ("4. Encoding",    "LabelEncoder por coluna (produto, grupo, categoria, subcategoria, cod_fechamento)"),
    ("5. TF-IDF",      "TfidfVectorizer(max_features=50) em 'descricao_resumida' → sparse matrix"),
    ("6. Merge",       "scipy.sparse.hstack([num_array, tfidf_matrix]) → X shape (N, 61)"),
    ("7. SMOTE (A)",   "Somente Modelo A: imblearn SMOTE → equaliza classes (248 → 20.282 positivos)"),
    ("8. Train/Test",  "train_test_split(test_size=0.2, stratify=y) → garante proporção de classes"),
    ("9. Treino",      "XGBClassifier (Modelo A) / RandomForestClassifier (Modelo B) → fit(X_train, y_train)"),
    ("10. Avaliação",  "classification_report + roc_auc_score + confusion_matrix → evaluation_report.txt"),
    ("11. Export",     "joblib.dump({model, tfidf, features}) → model_ola.pkl / model_priority.pkl"),
]
for step, desc in train_steps:
    story.append(Paragraph(
        f'<font color="#00D4FF"><b>{step}</b></font>  {desc}', sBody))
story.append(spacer(0.3))

story.append(Paragraph("Fluxo de Histórico — Dashboard → API → Oracle ADB → Dashboard", sH2))
story.append(Paragraph(
    "A página <b>API Live</b> do dashboard consulta o endpoint <code>/predictions/ola</code> que retorna "
    "as últimas N predições persistidas no Oracle ADB. O banco é alimentado em cada chamada ao "
    "<code>/predict/ola</code> via insert assíncrono. O usuário pode visualizar o histórico com KPIs, "
    "gráfico temporal e exportar para CSV.", sBody))

story.append(PageBreak())

# ── 08 BANCO ──────────────────────────────────────────────────
story.append(SectionHeader("BANCO DE DADOS — ORACLE ADB", "08"))
story.append(spacer(0.3))

story.append(Paragraph("Configuração do Oracle Autonomous Database", sH2))
story.append(kv_table([
    ("Serviço",        "Oracle Autonomous Database — Always Free (20GB)"),
    ("Região",         "OCI sa-saopaulo-1  |  Host: adb.sa-saopaulo-1.oraclecloud.com:1522"),
    ("Modo",           "oracledb thin mode — sem Oracle Instant Client instalado"),
    ("DSN alias",      "ariaaiops_high (tnsnames.ora)  |  aliases disponíveis: high/medium/low/tp/tpurgent"),
    ("Wallet",         "ewallet.pem + tnsnames.ora — reconstruídos via base64 env vars no Railway"),
    ("Criação tabelas","ensure_tables() chamado em daemon thread no startup da API (ORA-00955 silenciado)"),
    ("Fallback",       "Todas as funções retornam None / [] silenciosamente se conexão falhar"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Tabela: aria_ola_predictions", sH2))
story.append(db_table("aria_ola_predictions", [
    ("id",            "NUMBER IDENTITY PK", "Chave primária auto-incremento"),
    ("numero",        "VARCHAR2(50)",        "Número do incidente (identificação externa)"),
    ("prio_num",      "NUMBER(1)",           "Prioridade numérica da entrada (1-5)"),
    ("hora_abertura", "NUMBER(2)",           "Hora de abertura do incidente (0-23)"),
    ("dia_semana",    "NUMBER(1)",           "Dia da semana (0=Segunda … 6=Domingo)"),
    ("is_monitoring", "NUMBER(1)",           "Flag de abertura automática por monitoramento"),
    ("descricao",     "VARCHAR2(500)",       "Texto da descrição truncado em 500 chars"),
    ("grupo",         "VARCHAR2(200)",       "Nome do grupo designado (string original)"),
    ("probabilidade", "NUMBER(6,4)",         "Probabilidade de violação OLA (0.0000 a 1.0000)"),
    ("nivel_risco",   "VARCHAR2(10)",        "BAIXO (<25%) | MEDIO (25-49%) | ALTO (>=50%)"),
    ("criado_em",     "TIMESTAMP",          "Timestamp de criação (DEFAULT SYSTIMESTAMP)"),
], color=ORANGE))
story.append(spacer(0.3))

story.append(Paragraph("Tabela: aria_priority_predictions", sH2))
story.append(db_table("aria_priority_predictions", [
    ("id",                  "NUMBER IDENTITY PK", "Chave primária auto-incremento"),
    ("numero",              "VARCHAR2(50)",        "Número do incidente"),
    ("prio_num_entrada",    "NUMBER(1)",           "Prioridade informada na entrada"),
    ("prioridade_predita",  "NUMBER(1)",           "Prioridade predita pelo modelo (2/3/4)"),
    ("descricao",           "VARCHAR2(500)",       "Texto da descrição truncado"),
    ("grupo",               "VARCHAR2(200)",       "Grupo designado"),
    ("criado_em",           "TIMESTAMP",          "Timestamp de criação"),
], color=GREEN))
story.append(spacer(0.3))

story.append(Paragraph("Variáveis de Ambiente Necessárias", sH2))
story.append(kv_table([
    ("ARIA_DB_USER",           "Usuário do banco — padrão: ADMIN"),
    ("ARIA_DB_PASSWORD",       "Senha do usuário ADMIN (definida ao criar o ADB no OCI)"),
    ("ARIA_DB_DSN",            "Alias TNS — ex: ariaaiops_high"),
    ("ARIA_WALLET_DIR",        "Caminho da wallet — padrão em Docker: /app/wallet"),
    ("ARIA_WALLET_PASSWORD",   "Senha da wallet (definida AO BAIXAR no OCI Console — diferente da senha ADMIN)"),
    ("ARIA_WALLET_EWALLET_B64","Conteúdo de ewallet.pem codificado em base64 (para deploy em container)"),
    ("ARIA_WALLET_TNSNAMES_B64","Conteúdo de tnsnames.ora codificado em base64 (para deploy em container)"),
]))

story.append(PageBreak())

# ── 09 INFRA/DEPLOY ───────────────────────────────────────────
story.append(SectionHeader("INFRAESTRUTURA E DEPLOY", "09"))
story.append(spacer(0.3))

story.append(Paragraph("Arquitetura de Deploy", sH2))
deploy_data = [
    ["Componente", "Plataforma", "URL", "Método"],
    ["API REST", "Railway.app", "aria-api-production.up.railway.app", "Docker via Dockerfile + entrypoint.sh"],
    ["Dashboard", "Streamlit Cloud", "afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app", "GitHub → Streamlit Cloud (auto-deploy)"],
    ["Banco", "OCI Always Free", "adb.sa-saopaulo-1.oraclecloud.com", "Oracle ADB provisionado via OCI Console"],
    ["Código", "GitHub", "github.com/afonsoas/aria-aiops", "Push para branch main aciona Railway re-build"],
]
dep_t = Table(deploy_data, colWidths=[2.5*cm, 3.0*cm, 6.5*cm, 4.0*cm])
dep_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0d1b3e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), CYAN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, CYAN),
]))
story.append(dep_t)
story.append(spacer(0.3))

story.append(Paragraph("Dockerfile — API", sH2))
docker_lines = [
    "FROM python:3.11-slim",
    "WORKDIR /app",
    "COPY requirements.txt .",
    "RUN pip install --no-cache-dir -r requirements.txt",
    "COPY api/ ./api/",
    "COPY model/ ./model/",
    "COPY entrypoint.sh .",
    "RUN chmod +x entrypoint.sh",
    "ENV ARIA_WALLET_DIR=/app/wallet",
    "EXPOSE 8000",
    'ENTRYPOINT ["./entrypoint.sh"]',
]
for line in docker_lines:
    story.append(Paragraph(line, sCode))
story.append(spacer(0.3))

story.append(Paragraph("entrypoint.sh — Reconstrução da Wallet Oracle", sH2))
story.append(Paragraph(
    "O Oracle ADB requer arquivos de wallet que não podem ser commitados no git. "
    "A solução é encodar os arquivos em base64 e decodificá-los no startup do container:", sBody))
entrypoint_lines = [
    "#!/bin/sh",
    "set -e",
    'WALLET_DIR="${ARIA_WALLET_DIR:-/app/wallet}"',
    'mkdir -p "$WALLET_DIR"',
    'if [ -n "$ARIA_WALLET_EWALLET_B64" ]; then',
    '    echo "$ARIA_WALLET_EWALLET_B64" | base64 -d > "$WALLET_DIR/ewallet.pem"',
    'fi',
    'if [ -n "$ARIA_WALLET_TNSNAMES_B64" ]; then',
    '    echo "$ARIA_WALLET_TNSNAMES_B64" | base64 -d > "$WALLET_DIR/tnsnames.ora"',
    'fi',
    'exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1',
]
for line in entrypoint_lines:
    story.append(Paragraph(line, sCode))
story.append(spacer(0.3))

story.append(Paragraph("Gerar Base64 da Wallet (Windows/Linux)", sH2))
story.append(Paragraph("# Windows PowerShell:", sCode))
story.append(Paragraph("[Convert]::ToBase64String([IO.File]::ReadAllBytes('wallet/ewallet.pem'))", sCode))
story.append(Paragraph("# Linux/Mac:", sCode))
story.append(Paragraph("base64 -w 0 wallet/ewallet.pem", sCode))

story.append(PageBreak())

# ── 10 MÉTRICAS ───────────────────────────────────────────────
story.append(SectionHeader("MÉTRICAS E QUALIDADE", "10"))
story.append(spacer(0.3))

story.append(Paragraph("Métricas dos Modelos ML", sH2))
story.append(metrics_row([
    ("0.84",  "ROC-AUC Modelo A", PURPLE),
    ("60%",   "Recall Violações", ORANGE),
    ("0.90",  "F1-Macro Modelo B", GREEN),
    ("91%",   "Accuracy Modelo B", BLUE),
]))
story.append(spacer(0.3))

story.append(Paragraph("Resultados Detalhados — Modelo A (OLA)", sH2))
story.append(kv_table([
    ("Dataset teste",    "5.120 instâncias (20% de 25.600)  |  50 violações reais"),
    ("Verdadeiros Positivos", "30 (de 50 violações → Recall 60%)"),
    ("Falsos Positivos", "751 alertas incorretos (Precision 4% — trade-off aceitável)"),
    ("Verdadeiros Negativos", "4.319 não-violações corretamente identificadas"),
    ("Falsos Negativos", "20 violações perdidas (não alertadas)"),
    ("Interpretação",    "Para cada 100 alertas ARIA, ~4 são violações reais — mas 60% das violações são detectadas antes"),
]))
story.append(spacer(0.2))

story.append(Paragraph("Resultados Detalhados — Modelo B (Prioridade)", sH2))
story.append(kv_table([
    ("Dataset teste",    "24.442 instâncias (20% de 122.209)"),
    ("Prio 2-Alta",      "2.898 corretos de 3.130  |  F1 88%  |  Precision 84%  |  Recall 93%"),
    ("Prio 3-Média",     "7.807 corretos de 8.346  |  F1 88%  |  Precision 84%  |  Recall 94%"),
    ("Prio 4-Baixa",     "11.466 corretos de 12.966  |  F1 93%  |  Precision 98%  |  Recall 88%"),
    ("Acurácia global",  "91%  |  22.171 de 24.442 predições corretas"),
]))
story.append(spacer(0.3))

story.append(Paragraph("Testes de Sistema Automatizados", sH2))
tc_data = [
    ["TC", "Tipo", "Descrição", "Status"],
    ["TC-01", "API", "GET /health retorna status 200 e campos obrigatórios", "✓ PASS"],
    ["TC-02", "API", "POST /predict/ola com payload mínimo retorna probabilidade 0-1", "✓ PASS"],
    ["TC-03", "API", "POST /predict/priority retorna prioridade 2, 3 ou 4", "✓ PASS"],
    ["TC-04", "API", "GET /predictions/ola retorna lista (pode ser vazia)", "✓ PASS"],
    ["TC-05", "API", "GET /encoders/info retorna dict com listas de strings", "✓ PASS"],
    ["TC-06", "API", "POST /predict/ola com descricao 'domain error' retorna ALTO", "✓ PASS"],
    ["TC-07", "API", "Nível de risco: <25% = BAIXO, 25-49% = MEDIO, >=50% = ALTO", "✓ PASS"],
    ["TC-17", "E2E", "Dashboard acessível em URL pública Streamlit Cloud", "✓ PASS"],
    ["TC-18", "CI",  "GitHub Actions: pip install sem erros em Python 3.11", "✓ PASS"],
]
tc_t = Table(tc_data, colWidths=[1.5*cm, 1.5*cm, 11.0*cm, 2.0*cm])
tc_t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#0d1b3e")),
    ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0), (-1,-1), 8),
    ("TEXTCOLOR",    (0,0), (-1,0), CYAN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0a1628"), colors.HexColor("#0d1438")]),
    ("GRID",         (0,0), (-1,-1), 0.4, GRAY3),
    ("TOPPADDING",   (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ("TEXTCOLOR",    (0,1), (-1,-1), GRAY1),
    ("TEXTCOLOR",    (-1,1), (-1,-1), GREEN),
    ("FONTNAME",     (-1,1), (-1,-1), "Helvetica-Bold"),
    ("LINEBELOW",    (0,0), (-1,0), 1.2, CYAN),
]))
story.append(tc_t)
story.append(spacer(0.3))

story.append(hr())
story.append(Paragraph(
    "Afonso Araujo dos Santos RM562671  |  Bernardo Mayrinck RM558055  |  Enrico Taraborelli Lara RM566064  |  "
    "Cluster 3 · 2TSCO  |  FIAP Enterprise Challenge Locaweb 2026", sMeta))


# ── Build PDF ─────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    leftMargin=2*cm,
    rightMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm,
    title="ARIA AIOps — Arquitetura Técnica",
    author="Cluster 3 — FIAP Enterprise Challenge 2026",
    subject="Documento de Arquitetura do Sistema ARIA",
)

doc.build(story, onFirstPage=on_first_page, onLaterPages=on_page)
print(f"PDF gerado: {OUTPUT}")
print(f"Tamanho: {OUTPUT.stat().st_size // 1024} KB")
