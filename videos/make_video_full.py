"""
ARIA — Video de Entrega Profissional
Formato: 1920x1080 (16:9) | ~5:30 min | MP4 H264

Saída: videos/ARIA_Entrega_Completa.mp4

Uso:
  cd D:/AFONSO/aria-aiops
  python videos/make_video_full.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from PIL import ImageDraw
from moviepy import VideoClip, concatenate_videoclips, ImageClip
from moviepy.video.fx import FadeIn, FadeOut

from frame_engine import (
    scene_intro, scene_problema, scene_solucao, scene_metricas,
    scene_dashboard, scene_api, scene_encerramento,
    Canvas, BG, BG2, BG3, BLUE, CYAN, ORANGE, GREEN, PURPLE, WHITE, GRAY, GRAY2,
    ease_out, alpha_blend,
)

W, H = 1920, 1080
FPS  = 24
OUT  = Path(__file__).resolve().parent / "ARIA_Entrega_Completa.mp4"

FADE = 0.4   # segundos de fade entre cenas


def scene_playbooks(w, h, duration=3.5):
    """Playbooks sugeridos — top 5 padrões."""
    playbooks = [
        ("Check App Monitoring",    "28.728 casos", "Reiniciar serviço + checar certificado",  BLUE),
        ("Free disk space < 10%",   "4.770 casos",  "Limpar /tmp + expandir volume",           ORANGE),
        ("Unavailable by ICMP",     "4.133 casos",  "Verificar firewall + gateway + uptime",   CYAN),
        ("Apache Busy Workers",     "3.925 casos",  "Aumentar MaxRequestWorkers",              GREEN),
        ("Processor load P3 high",  "2.174 casos",  "Identificar processo + escalar",          PURPLE),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (7, 14, 30))
        c.gradient_rect(0, 0, w, 5, GREEN, CYAN)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("Playbooks Automáticos Sugeridos", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("ARIA detecta o padrão e sugere a ação corretiva antes da violação",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        card_h = int(h * 0.12)
        card_gap = int(h * 0.02)
        card_x = int(w * 0.04)
        card_w = int(w * 0.92)
        start_y = int(h * 0.19)

        for i, (nome, freq, acao, color) in enumerate(playbooks):
            delay = i * 0.4
            appear = ease_out(max(t - delay, 0), 0.4)
            if appear <= 0:
                continue
            cy = start_y + i * (card_h + card_gap)
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(card_x, cy, card_w, card_h, BG3, radius=8)
            tmp.rect(card_x, cy, 7, card_h, color, radius=3)

            # Badge número
            badge_r = int(card_h * 0.35)
            badge_cx = card_x + int(card_w * 0.035)
            tmp.circle(badge_cx, cy + card_h // 2, badge_r, color)
            num_size = max(int(w * 0.018), 11)
            tmp.text(str(i + 1),
                     badge_cx - badge_r + 3, cy + card_h // 2 - badge_r // 2,
                     size=num_size, weight="bold", color=(5, 14, 31))

            nome_size = max(int(w * 0.022), 13)
            freq_size = max(int(w * 0.016), 10)
            acao_size = max(int(w * 0.015), 9)

            tmp.text(nome, card_x + int(card_w * 0.08), cy + int(card_h * 0.1),
                     size=nome_size, weight="bold", color=color)
            tmp.text(freq, card_x + int(card_w * 0.08), cy + int(card_h * 0.55),
                     size=freq_size, color=GRAY2)
            tmp.text("→ " + acao, card_x + int(card_w * 0.35), cy + int(card_h * 0.3),
                     size=acao_size, color=GRAY)

            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


def scene_impacto(w, h, duration=3.5):
    """Impactos esperados — 3 colunas."""
    impactos = [
        ("Operacional", [
            "-60% violações OLA",
            "Triagem em < 2 segundos",
            "Playbooks para top 5 padrões",
            "Dashboard KPI tempo real",
        ], BLUE),
        ("Negócio", [
            "SLA garantido = retenção",
            "Menos penalidades contratuais",
            "NOC opera com menos esforço",
            "ROI no 1º trimestre de uso",
        ], GREEN),
        ("Técnico / ESG", [
            "100% open source — zero licença",
            "OCI Always Free — cloud gratuita",
            "IA em PT-BR com dados reais",
            "FastAPI + Streamlit + Oracle",
        ], CYAN),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (5, 12, 28))
        c.gradient_rect(0, 0, w, 5, BLUE, PURPLE)
        c.rect(0, 0, w, int(h * 0.16), BG2)

        title_size = max(int(w * 0.032), 20)
        c.text("Impactos Esperados", int(w * 0.04), int(h * 0.04),
               size=title_size, weight="bold", color=WHITE)
        c.text("Locaweb — benefícios operacionais, de negócio e de sustentabilidade",
               int(w * 0.04), int(h * 0.1),
               size=max(int(w * 0.018), 12), color=GRAY2)

        cols = len(impactos)
        margin = int(w * 0.04)
        gap = int(w * 0.015)
        card_w = (w - 2 * margin - (cols - 1) * gap) // cols
        card_h = int(h * 0.62)
        card_y = int(h * 0.2)

        for i, (titulo, items, color) in enumerate(impactos):
            delay = i * 0.5
            appear = ease_out(max(t - delay, 0), 0.5)
            if appear <= 0:
                continue
            cx = margin + i * (card_w + gap)
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(cx, card_y, card_w, card_h, BG3, radius=10)
            tmp.rect(cx, card_y, card_w, 6, color, radius=3)
            tmp.rect(cx, card_y, card_w, int(card_h * 0.16), BG2)
            title_sz = max(int(w * 0.022), 13)
            item_sz  = max(int(w * 0.016), 10)
            tmp.text(titulo, cx + int(card_w * 0.06), card_y + int(card_h * 0.04),
                     size=title_sz, weight="bold", color=color)
            for j, item in enumerate(items):
                iy = card_y + int(card_h * 0.22) + j * int(card_h * 0.16)
                tmp.rect(cx + int(card_w * 0.04), iy, int(card_w * 0.92),
                         int(card_h * 0.13), (10, 18, 38), radius=6)
                tmp.text("• " + item, cx + int(card_w * 0.07), iy + int(card_h * 0.025),
                         size=item_sz, color=GRAY)
            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


def make_transition(w, h, duration=FADE):
    """Fade to black."""
    def frame(t):
        pct = t / duration
        return np.full((h, w, 3), int(5 * (1 - pct) + 0 * pct), dtype=np.uint8)
    return VideoClip(frame, duration=duration)


def build_clip(make_frame_fn, duration, fade_in=True, fade_out=True):
    clip = VideoClip(make_frame_fn, duration=duration)
    effects = []
    if fade_in:
        effects.append(FadeIn(FADE))
    if fade_out:
        effects.append(FadeOut(FADE))
    if effects:
        clip = clip.with_effects(effects)
    return clip


# ── Narração (opcional — texto de apoio) ──────────────────────
NARRATION = """
=== NARRAÇÃO — ARIA Vídeo de Entrega (~5:30 min) ===

[0:00–0:10] INTRO
"ARIA — Automated Response & Incident Analysis.
 A solução AIOps desenvolvida para a Locaweb."

[0:10–0:50] O PROBLEMA
"A Locaweb registra mais de 122 mil incidentes por ano.
 85% são abertos automaticamente por monitoramento.
 Mas 248 violações de OLA ocorreram — e zero eram antecipadas.
 Um único grupo, o Team14, responde por 75% de todos os casos."

[0:50–1:30] A SOLUÇÃO
"A ARIA foi construída sobre 4 pilares:
 O Modelo A — XGBoost com SMOTE — prediz violações de OLA.
 O Modelo B — Random Forest — classifica prioridade automaticamente.
 Um dashboard Streamlit de 5 páginas centraliza a gestão.
 E uma API REST FastAPI expõe os modelos em tempo real."

[1:30–2:30] DASHBOARD
"O dashboard ARIA opera em modo escuro com glassmorphism.
 Temos KPI Overview com evolução mensal e heatmap de horários.
 Lista de incidentes com badge de risco OLA e exportação CSV.
 Preditor OLA com gauge de probabilidade e feature importance.
 E a página de padrões com treemap e playbooks automáticos."

[2:30–3:15] MÉTRICAS ML
"O Modelo A atingiu ROC-AUC de 0.84 com recall de 60%.
 Com apenas 248 violações em 25 mil registros, aplicamos SMOTE
 para gerar 20 mil exemplos sintéticos positivos.
 O Modelo B entregou 91% de acurácia e F1-macro de 0.90
 para as 3 classes de prioridade."

[3:15–3:45] PLAYBOOKS
"A análise dos padrões revelou que Check Application Monitoring
 representa 28 mil ocorrências — quase 1 em 4 incidentes.
 Para cada padrão, a ARIA sugere um playbook automático
 com as ações corretivas específicas."

[3:45–4:30] API REST
"A API FastAPI expõe 5 endpoints documentados via Swagger.
 POST /predict/ola retorna a probabilidade e o nível de risco
 em menos de 2 segundos.
 Todas as predições são persistidas no Oracle Autonomous Database
 no OCI, no tier gratuito."

[4:30–5:00] IMPACTOS
"Com a ARIA, esperamos redução de 60% nas violações de OLA,
 triagem automática de prioridade em menos de 2 segundos,
 e visibilidade operacional unificada para NOC e gestão.
 100% open source, rodando em OCI free tier."

[5:00–5:30] ENCERRAMENTO
"ARIA — Resposta certa, no tempo certo, pelo caminho certo.
 Código completo em github.com/afonsoas/aria-aiops.
 Locaweb Enterprise Challenge 2026 — FIAP 2TSCO — Cluster 3."
"""


# ── Build ─────────────────────────────────────────────────────
def main():
    print("Renderizando ARIA_Entrega_Completa.mp4 ...")
    print(f"Resolucao: {W}x{H} | FPS: {FPS}")

    scenes_def = [
        scene_intro(W, H, duration=2.5),
        scene_problema(W, H, duration=5.0),
        scene_solucao(W, H, duration=4.5),
        scene_dashboard(W, H, duration=5.0),
        scene_metricas(W, H, duration=4.5),
        scene_playbooks(W, H, duration=4.5),
        scene_api(W, H, duration=4.5),
        scene_impacto(W, H, duration=4.0),
        scene_encerramento(W, H, duration=4.0),
    ]

    clips = []
    for i, (make_frame, dur) in enumerate(scenes_def):
        print(f"  Cena {i+1}/{len(scenes_def)} ({dur:.1f}s)...")
        clip = build_clip(make_frame, dur,
                          fade_in=(i > 0),
                          fade_out=(i < len(scenes_def) - 1))
        clips.append(clip)

    print("Concatenando cenas...")
    final = concatenate_videoclips(clips, method="compose")

    total = sum(d for _, d in scenes_def)
    print(f"Duracao total estimada: {total:.0f}s ({total/60:.1f} min)")

    print(f"Escrevendo {OUT} ...")
    final.write_videofile(
        str(OUT),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        ffmpeg_params=["-crf", "20"],
        logger="bar",
    )
    print(f"\nPronto: {OUT}")
    print(NARRATION)


if __name__ == "__main__":
    main()
