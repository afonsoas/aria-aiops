"""
ARIA Video Frame Engine
Renderiza frames PIL para os videos de entrega e Instagram.
"""
from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# ── Fontes ────────────────────────────────────────────────────
_FONT_DIR = Path("C:/Windows/Fonts")

def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = {
        "black":   ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf"],
        "bold":    ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf"],
        "regular": ["arial.ttf",   "segoeui.ttf",  "calibri.ttf"],
        "light":   ["segoeui.ttf", "arial.ttf",    "calibri.ttf"],
    }
    for fname in candidates.get(name, candidates["regular"]):
        p = _FONT_DIR / fname
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

# ── Paleta ────────────────────────────────────────────────────
BG      = (5,  14,  31)
BG2     = (13, 29,  62)
BG3     = (8,  18,  40)
BLUE    = (16,  91, 216)
CYAN    = (0,  212, 255)
ORANGE  = (255, 107, 53)
GREEN   = (0,  200, 122)
PURPLE  = (124, 58, 237)
WHITE   = (255, 255, 255)
GRAY    = (226, 232, 248)
GRAY2   = (136, 153, 187)
BLACK   = (0,   0,   0)

# ── Helpers ───────────────────────────────────────────────────
def ease_out(t: float, total: float = 1.0) -> float:
    """Easing out cubic."""
    x = min(t / total, 1.0)
    return 1 - (1 - x) ** 3

def ease_in_out(t: float, total: float = 1.0) -> float:
    x = min(t / total, 1.0)
    return x * x * (3 - 2 * x)

def alpha_blend(base: Image.Image, overlay: Image.Image, alpha: float) -> Image.Image:
    """Blend overlay onto base with alpha [0..1]."""
    if alpha <= 0:
        return base
    if alpha >= 1:
        return Image.alpha_composite(base.convert("RGBA"), overlay.convert("RGBA")).convert("RGB")
    ov = overlay.convert("RGBA")
    r, g, b, a = ov.split()
    a = a.point(lambda x: int(x * alpha))
    ov.putalpha(a)
    result = base.convert("RGBA")
    result.alpha_composite(ov)
    return result.convert("RGB")


class Canvas:
    """Wrapper PIL que facilita desenho de elementos ARIA."""

    def __init__(self, w: int, h: int, bg=BG):
        self.w = w
        self.h = h
        self.img = Image.new("RGB", (w, h), bg)
        self.draw = ImageDraw.Draw(self.img)

    def copy(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.img = self.img.copy()
        c.draw = ImageDraw.Draw(c.img)
        return c

    # ── Primitivos ────────────────────────────────────────────
    def rect(self, x, y, w, h, color, radius=0):
        if radius > 0:
            self.draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=color)
        else:
            self.draw.rectangle([x, y, x+w, y+h], fill=color)
        return self

    def line_h(self, x, y, w, h=3, color=CYAN):
        self.draw.rectangle([x, y, x+w, y+h], fill=color)
        return self

    def gradient_rect(self, x, y, w, h, color_l, color_r):
        """Gradiente horizontal simples."""
        for i in range(w):
            t = i / max(w - 1, 1)
            r = int(color_l[0] * (1 - t) + color_r[0] * t)
            g = int(color_l[1] * (1 - t) + color_r[1] * t)
            b = int(color_l[2] * (1 - t) + color_r[2] * t)
            self.draw.line([(x+i, y), (x+i, y+h)], fill=(r, g, b))
        return self

    def text(self, txt: str, x, y, size=28, weight="regular",
             color=WHITE, align="left", max_w=None):
        f = _font(weight, size)
        if align == "center" and max_w:
            bbox = self.draw.textbbox((0, 0), txt, font=f)
            tw = bbox[2] - bbox[0]
            x = x + (max_w - tw) // 2
        elif align == "right" and max_w:
            bbox = self.draw.textbbox((0, 0), txt, font=f)
            tw = bbox[2] - bbox[0]
            x = x + max_w - tw
        self.draw.text((x, y), txt, font=f, fill=color)
        return self

    def text_w(self, txt: str, size=28, weight="regular") -> int:
        f = _font(weight, size)
        bbox = self.draw.textbbox((0, 0), txt, font=f)
        return bbox[2] - bbox[0]

    def bar_h(self, x, y, w, h, pct, color=BLUE, bg=BG3, radius=4):
        self.rect(x, y, w, h, bg, radius)
        fill_w = max(int(w * pct), 0)
        if fill_w > 0:
            self.rect(x, y, fill_w, h, color, radius)
        return self

    def circle(self, cx, cy, r, color):
        self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        return self

    def numpy(self) -> np.ndarray:
        return np.array(self.img)

    def paste(self, other: "Canvas", x=0, y=0):
        self.img.paste(other.img, (x, y))
        self.draw = ImageDraw.Draw(self.img)
        return self


# ══════════════════════════════════════════════════════════════
# CENAS — retornam funções make_frame(t) → np.ndarray
# ══════════════════════════════════════════════════════════════

def scene_intro(w, h, duration=2.5):
    """Logo ARIA com fade-in e barra animada."""
    def make_frame(t):
        progress = ease_out(t, duration * 0.6)
        c = Canvas(w, h)

        # Fundo gradiente
        c.gradient_rect(0, 0, w, h, BG, (10, 20, 50))

        # Linha de acento superior
        bar_w = int(w * min(t / 0.8, 1.0))
        c.gradient_rect(0, 0, bar_w, 5, BLUE, CYAN)

        # ARIA — fade + slide up
        if progress > 0:
            offset = int(40 * (1 - progress))
            alpha_val = progress
            aria_size = int(w * 0.18)
            txt = "ARIA"
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text(txt, 0, 0, size=aria_size, weight="black", color=WHITE,
                     align="center", max_w=w)
            ty = h // 2 - int(aria_size * 0.6) - offset
            c.img = alpha_blend(c.img, tmp.img, alpha_val)
            c.draw = ImageDraw.Draw(c.img)

        # Subtitulo
        if t > 0.7:
            sub_alpha = ease_out(t - 0.7, 0.6)
            sub = "Automated Response & Incident Analysis"
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.text(sub, 0, h // 2 + int(w * 0.11), size=int(w * 0.022),
                      weight="regular", color=CYAN, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp2.img, sub_alpha)
            c.draw = ImageDraw.Draw(c.img)

        # Linha inferior
        if t > 1.2:
            line_alpha = ease_out(t - 1.2, 0.5)
            lw = int(w * 0.3 * line_alpha)
            lx = (w - int(w * 0.3)) // 2
            ly = h // 2 + int(w * 0.155)
            c.gradient_rect(lx, ly, lw, 3, PURPLE, CYAN)

        return c.numpy()
    return make_frame, duration


def scene_problema(w, h, duration=4.0):
    """Contador animado dos problemas reais."""
    data = [
        ("122.543",   "incidentes registrados / ano",     BLUE,   0.0),
        ("85%",        "abertos por monitoramento automático", CYAN, 0.6),
        ("248",        "violações de OLA (0,97% dos elegíveis)", ORANGE, 1.2),
        ("75%",        "em apenas 1 grupo — Team14",      PURPLE, 1.8),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 16, 35))
        c.line_h(0, 0, w, 5, ORANGE)
        c.rect(0, 0, w, int(h * 0.15), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("O Problema Real", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("Locaweb — Jan/2023 a Dez/2025 — 122.543 incidentes",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        card_h = int(h * 0.14)
        card_gap = int(h * 0.02)
        card_y_start = int(h * 0.18)
        card_x = int(w * 0.04)
        card_w = int(w * 0.92)

        colors = [BLUE, CYAN, ORANGE, PURPLE]
        for i, (val, label, color, delay) in enumerate(data):
            appear = ease_out(max(t - delay, 0), 0.45)
            if appear <= 0:
                continue
            cy = card_y_start + i * (card_h + card_gap)
            # card bg
            c.rect(card_x, cy, card_w, card_h, BG3, radius=8)
            c.rect(card_x, cy, 6, card_h, color, radius=3)

            # barra de progresso anima
            c.bar_h(card_x + 10, cy + card_h - 8, card_w - 20, 4,
                    appear, color, bg=(20, 28, 48))

            val_size = max(int(w * 0.048), 24)
            lbl_size = max(int(w * 0.02), 12)
            c.text(val, card_x + int(w * 0.03), cy + int(card_h * 0.12),
                   size=val_size, weight="black", color=color)
            c.text(label, card_x + int(w * 0.03), cy + int(card_h * 0.6),
                   size=lbl_size, color=GRAY)

        return c.numpy()
    return make_frame, duration


def scene_solucao(w, h, duration=3.5):
    """4 pilares ARIA com aparição sequencial."""
    pilares = [
        ("Modelo A",  "XGBoost + SMOTE",  "ROC-AUC 0.84\nRecall 60%",  BLUE),
        ("Modelo B",  "Random Forest",     "F1 0.90\nAccuracy 91%",     CYAN),
        ("Dashboard", "Streamlit 5 pag.",  "Tema escuro\nGlassmorphism",GREEN),
        ("API REST",  "FastAPI + Oracle",  "< 2s latência\nSwagger UI", PURPLE),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (5, 15, 35))
        c.line_h(0, 0, w, 5, CYAN)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("A Solução ARIA", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text('"Resposta certa, no tempo certo, pelo caminho certo."',
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=CYAN)

        n = len(pilares)
        margin = int(w * 0.04)
        gap = int(w * 0.015)
        card_w = (w - 2 * margin - (n - 1) * gap) // n
        card_h = int(h * 0.58)
        card_y = int(h * 0.22)

        for i, (nome, tech, detalhe, color) in enumerate(pilares):
            delay = i * 0.45
            appear = ease_out(max(t - delay, 0), 0.5)
            if appear <= 0:
                continue
            cx = margin + i * (card_w + gap)

            # card bg com alpha
            if appear < 1:
                tmp = Canvas(w, h, (0, 0, 0))
                slide_offset = int(30 * (1 - appear))
                tmp.rect(cx, card_y - slide_offset, card_w, card_h, BG3, radius=10)
                tmp.rect(cx, card_y - slide_offset, card_w, 5, color, radius=3)
                c.img = alpha_blend(c.img, tmp.img, appear)
                c.draw = ImageDraw.Draw(c.img)
            else:
                c.rect(cx, card_y, card_w, card_h, BG3, radius=10)
                c.rect(cx, card_y, card_w, 5, color, radius=3)

                num_size = max(int(w * 0.016), 10)
                c.text(str(i + 1), cx + int(card_w * 0.82),
                       card_y + int(card_h * 0.04),
                       size=num_size, weight="bold", color=color)

                nome_size = max(int(w * 0.024), 14)
                tech_size = max(int(w * 0.016), 10)
                det_size  = max(int(w * 0.014), 9)

                c.text(nome, cx + int(card_w * 0.08), card_y + int(card_h * 0.12),
                       size=nome_size, weight="bold", color=color)
                c.text(tech, cx + int(card_w * 0.08), card_y + int(card_h * 0.3),
                       size=tech_size, color=GRAY2)

                for j, line in enumerate(detalhe.split("\n")):
                    c.text(line, cx + int(card_w * 0.08),
                           card_y + int(card_h * 0.5) + j * int(card_h * 0.14),
                           size=det_size, color=GRAY)

        return c.numpy()
    return make_frame, duration


def scene_metricas(w, h, duration=3.5):
    """Cards de métricas animados com barra de preenchimento."""
    metrics = [
        ("0.84",  "ROC-AUC",        "Modelo A — XGBoost",       BLUE,   0.84),
        ("60%",   "Recall OLA",     "Detecta 6 de 10 violações", ORANGE, 0.60),
        ("91%",   "Accuracy",       "Modelo B — Random Forest",  CYAN,   0.91),
        ("0.90",  "F1-macro",       "Classes 2/3/4 equilibradas",GREEN,  0.90),
        ("< 2s",  "Latência API",   "FastAPI + sparse matrix",   PURPLE, 0.85),
        ("122K",  "Incidentes",     "3 anos de dados reais",     GRAY2,  1.00),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 16, 38))
        c.line_h(0, 0, w, 5, GREEN)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("Resultados dos Modelos ML", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("Validação em holdout 20% — dados reais Locaweb",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        cols = 3
        margin = int(w * 0.04)
        gap = int(w * 0.018)
        card_w = (w - 2 * margin - (cols - 1) * gap) // cols
        card_h = int(h * 0.3)

        for i, (val, label, sub, color, pct) in enumerate(metrics):
            row = i // cols
            col = i % cols
            delay = i * 0.3
            appear = ease_out(max(t - delay, 0), 0.5)
            bar_p  = ease_out(max(t - delay - 0.2, 0), 0.6) * pct
            if appear <= 0:
                continue

            cx = margin + col * (card_w + gap)
            cy = int(h * 0.22) + row * (card_h + gap)

            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(cx, cy, card_w, card_h, BG3, radius=10)
            tmp.rect(cx, cy, card_w, 4, color, radius=3)

            val_size = max(int(w * 0.04), 20)
            lbl_size = max(int(w * 0.018), 11)
            sub_size = max(int(w * 0.013), 9)

            tmp.text(val, cx + int(card_w * 0.08), cy + int(card_h * 0.12),
                     size=val_size, weight="black", color=color)
            tmp.text(label, cx + int(card_w * 0.08), cy + int(card_h * 0.52),
                     size=lbl_size, weight="bold", color=WHITE)
            tmp.text(sub, cx + int(card_w * 0.08), cy + int(card_h * 0.68),
                     size=sub_size, color=GRAY2)
            tmp.bar_h(cx + int(card_w * 0.08), cy + card_h - 14,
                      int(card_w * 0.84), 6, bar_p, color)

            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


def scene_dashboard(w, h, duration=4.0):
    """Mockup das 5 páginas do dashboard."""
    pages = [
        ("Home",         "5 KPIs globais + destaques ML",    BLUE),
        ("KPI Overview", "Evolução temporal + heatmap",       CYAN),
        ("Incidentes",   "Tabela filtrável + badge de risco", ORANGE),
        ("Preditor OLA", "Formulário + gauge probabilidade",  PURPLE),
        ("API Predictor","Histórico Oracle ADB em tempo real",GREEN),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (6, 14, 32))
        c.line_h(0, 0, w, 5, BLUE)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("Dashboard ARIA — 5 Páginas", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("Interface Streamlit com glassmorphism e tema escuro profissional",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        # "Browser mockup" central
        bx = int(w * 0.04)
        by = int(h * 0.19)
        bw = int(w * 0.92)
        bh = int(h * 0.64)

        c.rect(bx, by, bw, bh, BG3, radius=10)
        # barra de abas
        c.rect(bx, by, bw, int(h * 0.06), (12, 22, 50), radius=10)

        tab_w = bw // 5
        for i, (name, desc, color) in enumerate(pages):
            delay = i * 0.5
            appear = ease_out(max(t - delay, 0), 0.4)
            tx = bx + i * tab_w
            is_active = int(t * 0.9) % 5 == i

            tab_c = color if is_active else (22, 35, 65)
            alpha = 0.9 if is_active else min(appear, 0.6)
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(tx + 2, by + 2, tab_w - 4, int(h * 0.055),
                     tab_c, radius=6)
            tab_size = max(int(w * 0.013), 9)
            tmp.text(name, tx + 4, by + int(h * 0.018),
                     size=tab_size, weight="bold" if is_active else "regular",
                     color=WHITE if is_active else GRAY2)
            c.img = alpha_blend(c.img, tmp.img, alpha)
            c.draw = ImageDraw.Draw(c.img)

        # Content mockup com barras fictícias
        cx2 = bx + int(bw * 0.04)
        cy2 = by + int(h * 0.09)
        cw2 = bw - int(bw * 0.08)
        ch2 = bh - int(h * 0.12)

        # KPI cards simulados
        kpi_colors = [BLUE, CYAN, ORANGE, GREEN]
        kpi_labels = ["122.543", "248", "85%", "65%"]
        kpi_subs   = ["Incidentes", "Violações OLA", "Monitoramento", "Sem Intervenção"]
        kc_w = (cw2 - int(cw2 * 0.06)) // 4
        for i in range(4):
            kx = cx2 + i * (kc_w + int(cw2 * 0.02))
            c.rect(kx, cy2, kc_w, int(ch2 * 0.22), BG2, radius=8)
            c.rect(kx, cy2, kc_w, 4, kpi_colors[i])
            c.text(kpi_labels[i], kx + int(kc_w * 0.1), cy2 + int(ch2 * 0.04),
                   size=max(int(w * 0.022), 13), weight="black", color=kpi_colors[i])
            c.text(kpi_subs[i], kx + int(kc_w * 0.1), cy2 + int(ch2 * 0.14),
                   size=max(int(w * 0.012), 8), color=GRAY2)

        # Barras de gráfico simuladas
        bar_y = cy2 + int(ch2 * 0.28)
        bar_section_h = int(ch2 * 0.55)
        bar_count = 8
        bw3 = cw2 // bar_count
        bar_heights = [0.85, 0.65, 0.90, 0.55, 0.70, 0.80, 0.45, 0.60]
        bar_anim = ease_out(max(t - 0.8, 0), 1.0)
        for i in range(bar_count):
            bh3 = int(bar_section_h * bar_heights[i] * bar_anim)
            bx3 = cx2 + i * bw3 + int(bw3 * 0.1)
            by3 = bar_y + bar_section_h - bh3
            grad_c = BLUE if i % 2 == 0 else CYAN
            c.rect(bx3, by3, int(bw3 * 0.8), bh3, grad_c, radius=3)

        return c.numpy()
    return make_frame, duration


def scene_api(w, h, duration=3.5):
    """Demonstração da API REST."""
    endpoints = [
        ("GET",  "/health",            "Status modelos + Oracle DB",       CYAN),
        ("POST", "/predict/ola",       "Probabilidade violação OLA",       ORANGE),
        ("POST", "/predict/priority",  "Classificação prioridade 2/3/4",   BLUE),
        ("GET",  "/predictions/ola",   "Histórico persistido Oracle ADB",  GREEN),
        ("GET",  "/docs",              "Swagger UI — documentação viva",    PURPLE),
    ]

    response_lines = [
        ('  "probabilidade": 0.1823,',  GRAY),
        ('  "percentual": "18.2%",',    GRAY),
        ('  "nivel_risco": "BAIXO",',   GREEN),
        ('  "recomendacao": "Normal...',GRAY),
        ('  "timestamp": "2026-04-15"', GRAY2),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 15, 35))
        c.line_h(0, 0, w, 5, PURPLE)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("API REST — FastAPI", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("Documentação Swagger em /docs  ·  Latência < 2s  ·  Oracle ADB integrado",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        # Painel esquerdo: endpoints
        ep_x = int(w * 0.04)
        ep_y = int(h * 0.19)
        ep_w = int(w * 0.5)
        c.rect(ep_x, ep_y, ep_w, int(h * 0.64), BG3, radius=10)
        c.text("Endpoints disponíveis", ep_x + int(ep_w * 0.05),
               ep_y + int(h * 0.025),
               size=max(int(w * 0.018), 11), weight="bold", color=CYAN)

        for i, (method, path, desc, color) in enumerate(endpoints):
            delay = i * 0.4
            appear = ease_out(max(t - delay, 0), 0.4)
            if appear <= 0:
                continue
            ey = ep_y + int(h * 0.08) + i * int(h * 0.11)
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(ep_x + int(ep_w * 0.04), ey,
                     int(ep_w * 0.92), int(h * 0.095), BG2, radius=6)
            method_c = {"GET": CYAN, "POST": ORANGE}.get(method, BLUE)
            tmp.rect(ep_x + int(ep_w * 0.04), ey,
                     int(ep_w * 0.13), int(h * 0.095), method_c, radius=6)
            tmp.text(method, ep_x + int(ep_w * 0.05), ey + int(h * 0.025),
                     size=max(int(w * 0.014), 9), weight="bold", color=BLACK)
            tmp.text(path, ep_x + int(ep_w * 0.2), ey + int(h * 0.015),
                     size=max(int(w * 0.016), 10), weight="bold", color=color)
            tmp.text(desc, ep_x + int(ep_w * 0.2), ey + int(h * 0.055),
                     size=max(int(w * 0.013), 9), color=GRAY2)
            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        # Painel direito: resposta JSON
        rp_x = int(w * 0.57)
        rp_y = int(h * 0.19)
        rp_w = int(w * 0.39)
        c.rect(rp_x, rp_y, rp_w, int(h * 0.64), (3, 7, 18), radius=10)
        c.text("Resposta POST /predict/ola", rp_x + int(rp_w * 0.05),
               rp_y + int(h * 0.025),
               size=max(int(w * 0.015), 9), weight="bold", color=ORANGE)
        c.text("{", rp_x + int(rp_w * 0.05), rp_y + int(h * 0.075),
               size=max(int(w * 0.015), 9), color=GRAY)
        for i, (line, color) in enumerate(response_lines):
            line_appear = ease_out(max(t - 1.0 - i * 0.25, 0), 0.4)
            if line_appear > 0:
                tmp = Canvas(w, h, (0, 0, 0))
                ly = rp_y + int(h * 0.115) + i * int(h * 0.09)
                tmp.text(line, rp_x + int(rp_w * 0.05), ly,
                         size=max(int(w * 0.013), 8), color=color)
                c.img = alpha_blend(c.img, tmp.img, min(line_appear * 2, 1.0))
                c.draw = ImageDraw.Draw(c.img)

        if t > 2.2:
            c.text("}", rp_x + int(rp_w * 0.05),
                   rp_y + int(h * 0.115) + 5 * int(h * 0.09),
                   size=max(int(w * 0.015), 9), color=GRAY)

        return c.numpy()
    return make_frame, duration


def scene_encerramento(w, h, duration=3.0):
    """Slide final com tagline e GitHub."""
    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (5, 10, 25))

        # Linha topo
        bar_w = int(w * min(t / 0.5, 1.0))
        c.gradient_rect(0, 0, bar_w, 6, GREEN, CYAN)

        progress = ease_out(max(t - 0.3, 0), 0.8)
        if progress > 0:
            # ARIA grande
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("ARIA", 0, int(h * 0.15), size=int(w * 0.16),
                     weight="black", color=WHITE, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, progress)
            c.draw = ImageDraw.Draw(c.img)

        if t > 0.8:
            sub_a = ease_out(t - 0.8, 0.6)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.text('"Resposta certa, no tempo certo, pelo caminho certo."',
                      0, int(h * 0.52), size=max(int(w * 0.022), 13),
                      color=CYAN, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp2.img, sub_a)
            c.draw = ImageDraw.Draw(c.img)

        if t > 1.3:
            info_a = ease_out(t - 1.3, 0.5)
            c.gradient_rect(int(w * 0.2), int(h * 0.65), int(w * 0.6), 2,
                            (0, 0, 0), GREEN)
            tmp3 = Canvas(w, h, (0, 0, 0))
            tmp3.text("github.com/afonsoas/aria-aiops",
                      0, int(h * 0.69), size=max(int(w * 0.018), 11),
                      color=GREEN, align="center", max_w=w)
            tmp3.text("Locaweb Enterprise Challenge 2026  ·  FIAP 2TSCO  ·  Cluster 3",
                      0, int(h * 0.77), size=max(int(w * 0.015), 9),
                      color=GRAY2, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp3.img, info_a)
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


# ══════════════════════════════════════════════════════════════
# CENAS INSTAGRAM (9:16 portrait)
# ══════════════════════════════════════════════════════════════

def ig_scene_hook(w, h, duration=2.5):
    """Hook agressivo — primeiros 3 segundos do Reels."""
    lines = [
        ("122.543", ORANGE, 0.0),
        ("incidentes por ano", GRAY, 0.3),
        ("248 violações de OLA", CYAN, 0.7),
        ("zero antecipação.", WHITE, 1.1),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (10, 20, 50))
        c.gradient_rect(0, 0, w, 6, ORANGE, CYAN)

        center_y = h // 2
        for i, (txt, color, delay) in enumerate(lines):
            appear = ease_out(max(t - delay, 0), 0.35)
            if appear <= 0:
                continue
            is_big = i == 0 or i == 2
            size = int(w * 0.14) if is_big else int(w * 0.07)
            offset = int(20 * (1 - appear))
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text(txt, 0,
                     center_y - int(h * 0.25) + i * int(h * 0.12) - offset,
                     size=size, weight="black" if is_big else "regular",
                     color=color, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, appear)
            c.draw = ImageDraw.Draw(c.img)

        # linha decorativa
        c.gradient_rect(int(w * 0.15), int(h * 0.82), int(w * 0.7), 3, ORANGE, CYAN)

        return c.numpy()
    return make_frame, duration


def ig_scene_aria(w, h, duration=2.5):
    """Apresenta ARIA e os 3 números chave."""
    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 18, 42))
        c.gradient_rect(0, 0, w, 6, CYAN, BLUE)

        # Logo
        logo_a = ease_out(max(t - 0.0, 0), 0.5)
        if logo_a > 0:
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("ARIA", 0, int(h * 0.08), size=int(w * 0.22),
                     weight="black", color=WHITE, align="center", max_w=w)
            tmp.text("AIOps · Locaweb", 0, int(h * 0.27), size=int(w * 0.06),
                     color=CYAN, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, logo_a)
            c.draw = ImageDraw.Draw(c.img)

        # 3 métricas
        metrics_ig = [
            ("0.84", "ROC-AUC", BLUE,   0.6),
            ("91%",  "Accuracy", CYAN,  0.9),
            ("< 2s", "Latência", GREEN, 1.2),
        ]
        mw = int(w * 0.28)
        mx_start = int(w * 0.05)
        for i, (val, lbl, color, delay) in enumerate(metrics_ig):
            appear = ease_out(max(t - delay, 0), 0.4)
            if appear <= 0:
                continue
            mx = mx_start + i * (mw + int(w * 0.025))
            my = int(h * 0.42)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.rect(mx, my, mw, int(h * 0.18), BG3, radius=12)
            tmp2.rect(mx, my, mw, 5, color, radius=3)
            tmp2.text(val, mx, my + int(h * 0.04),
                      size=int(w * 0.09), weight="black", color=color,
                      align="center", max_w=mw)
            tmp2.text(lbl, mx, my + int(h * 0.125),
                      size=int(w * 0.045), color=WHITE,
                      align="center", max_w=mw)
            c.img = alpha_blend(c.img, tmp2.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        if t > 1.5:
            sub_a = ease_out(t - 1.5, 0.4)
            tmp3 = Canvas(w, h, (0, 0, 0))
            tmp3.text("2 modelos ML · API REST · Oracle ADB",
                      0, int(h * 0.65), size=int(w * 0.055),
                      color=GRAY2, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp3.img, sub_a)
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


def ig_scene_cta(w, h, duration=3.0):
    """Call to action final Instagram."""
    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (5, 12, 28))
        c.gradient_rect(0, 0, w, 6, GREEN, CYAN)

        # Tagline
        if t > 0.2:
            a = ease_out(t - 0.2, 0.6)
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text('"Resposta certa,', 0, int(h * 0.15),
                     size=int(w * 0.09), weight="bold", color=WHITE,
                     align="center", max_w=w)
            tmp.text("no tempo certo,", 0, int(h * 0.25),
                     size=int(w * 0.09), weight="bold", color=WHITE,
                     align="center", max_w=w)
            tmp.text('pelo caminho certo."', 0, int(h * 0.35),
                     size=int(w * 0.09), weight="bold", color=WHITE,
                     align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, a)
            c.draw = ImageDraw.Draw(c.img)

        # ARIA
        if t > 0.8:
            a2 = ease_out(t - 0.8, 0.5)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.text("ARIA", 0, int(h * 0.5),
                      size=int(w * 0.28), weight="black", color=CYAN,
                      align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp2.img, a2)
            c.draw = ImageDraw.Draw(c.img)

        # GitHub
        if t > 1.5:
            a3 = ease_out(t - 1.5, 0.5)
            tmp3 = Canvas(w, h, (0, 0, 0))
            tmp3.text("github.com/afonsoas/aria-aiops",
                      0, int(h * 0.73), size=int(w * 0.055),
                      color=GREEN, align="center", max_w=w)
            tmp3.text("FIAP Enterprise Challenge 2026 · Locaweb AIOps",
                      0, int(h * 0.8), size=int(w * 0.04),
                      color=GRAY2, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp3.img, a3)
            c.draw = ImageDraw.Draw(c.img)

        # Barra inferior
        c.gradient_rect(0, h - 6, int(w * min(t / duration, 1.0)), 6, CYAN, GREEN)
        return c.numpy()
    return make_frame, duration
