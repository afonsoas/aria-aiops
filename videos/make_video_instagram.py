"""
ARIA — Vídeo Instagram Reels
Formato: 1080x1920 (9:16 portrait) | ~55 segundos | MP4 H264

Saída: videos/ARIA_Instagram_Reels.mp4

Uso:
  cd D:/AFONSO/aria-aiops
  python videos/make_video_instagram.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from PIL import ImageDraw
from moviepy import VideoClip, concatenate_videoclips
from moviepy.video.fx import FadeIn, FadeOut

from frame_engine import (
    ig_scene_hook, ig_scene_aria, ig_scene_cta,
    Canvas, BG, BG2, BG3, BLUE, CYAN, ORANGE, GREEN, PURPLE, WHITE, GRAY, GRAY2,
    ease_out, ease_in_out, alpha_blend,
)

W, H = 1080, 1920
FPS  = 30
OUT  = Path(__file__).resolve().parent / "ARIA_Instagram_Reels.mp4"

FADE = 0.25


def ig_scene_numeros(w, h, duration=3.0):
    """Métricas dos modelos numa tela só — impacto visual."""
    nums = [
        ("0.84",  "ROC-AUC modelo OLA",         BLUE,   0.0),
        ("60%",   "Recall violações detectadas", ORANGE, 0.5),
        ("91%",   "Acurácia prioridade",         CYAN,   1.0),
        ("< 2s",  "Resposta da API",             GREEN,  1.5),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 18, 42))
        c.gradient_rect(0, 0, w, 6, BLUE, CYAN)

        title_a = ease_out(t, 0.4)
        if title_a > 0:
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("Resultados reais.", 0, int(h * 0.05),
                     size=int(w * 0.085), weight="bold", color=WHITE,
                     align="center", max_w=w)
            tmp.text("Dados da Locaweb.", 0, int(h * 0.13),
                     size=int(w * 0.085), weight="bold", color=CYAN,
                     align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, title_a)
            c.draw = ImageDraw.Draw(c.img)

        for i, (val, lbl, color, delay) in enumerate(nums):
            appear = ease_out(max(t - delay, 0), 0.4)
            if appear <= 0:
                continue
            cy = int(h * 0.25) + i * int(h * 0.165)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.rect(int(w * 0.06), cy, int(w * 0.88), int(h * 0.135), BG3, radius=14)
            tmp2.rect(int(w * 0.06), cy, int(w * 0.88), 5, color, radius=3)
            tmp2.text(val, int(w * 0.1), cy + int(h * 0.022),
                      size=int(w * 0.12), weight="black", color=color)
            tmp2.text(lbl, int(w * 0.1), cy + int(h * 0.088),
                      size=int(w * 0.05), color=GRAY)
            c.img = alpha_blend(c.img, tmp2.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration


def ig_scene_tech(w, h, duration=2.5):
    """Stack tecnológico em chips."""
    techs = [
        ("Python", BLUE), ("XGBoost", ORANGE), ("Random Forest", CYAN),
        ("FastAPI", GREEN), ("Oracle ADB", PURPLE), ("Streamlit", BLUE),
        ("SMOTE", ORANGE), ("TF-IDF", CYAN),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (6, 14, 32))
        c.gradient_rect(0, 0, w, 6, PURPLE, BLUE)

        title_a = ease_out(t, 0.4)
        if title_a > 0:
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("Stack 100%", 0, int(h * 0.05),
                     size=int(w * 0.085), weight="bold", color=WHITE,
                     align="center", max_w=w)
            tmp.text("open source.", 0, int(h * 0.13),
                     size=int(w * 0.085), weight="bold", color=CYAN,
                     align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, title_a)
            c.draw = ImageDraw.Draw(c.img)

        # Grid de chips
        chip_w = int(w * 0.42)
        chip_h = int(h * 0.07)
        chip_gap = int(w * 0.03)
        cols = 2
        start_x = int(w * 0.07)
        start_y = int(h * 0.26)

        for i, (tech, color) in enumerate(techs):
            delay = i * 0.2
            appear = ease_out(max(t - delay, 0), 0.35)
            if appear <= 0:
                continue
            row = i // cols
            col = i % cols
            cx = start_x + col * (chip_w + chip_gap)
            cy = start_y + row * (chip_h + int(h * 0.02))
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(cx, cy, chip_w, chip_h, BG3, radius=10)
            tmp.rect(cx, cy, 6, chip_h, color, radius=3)
            tmp.text(tech, cx + int(chip_w * 0.1), cy + int(chip_h * 0.22),
                     size=int(w * 0.05), weight="bold", color=color)
            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        if t > 1.8:
            a = ease_out(t - 1.8, 0.4)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.text("Zero licença. Deploy OCI free.",
                      0, int(h * 0.88), size=int(w * 0.055),
                      color=GRAY2, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp2.img, a)
            c.draw = ImageDraw.Draw(c.img)

        return c.numpy()
    return make_frame, duration




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


NARRATION_IG = """
=== NARRAÇÃO — Instagram Reels ARIA (~55s) ===

Legenda sugerida:
  "Construí um sistema de IA que prevê falhas de TI antes de acontecerem 🤖
   122K incidentes reais da Locaweb → XGBoost + Random Forest → API REST + Oracle ADB
   ROC-AUC 0.84 | 91% acurácia | latência < 2s
   100% open source 🔗 github.com/afonsoas/aria-aiops
   #AIOps #MachineLearning #Python #FastAPI #FIAP #DataScience"

[0:00–0:03] Hook — números agressivos
[0:03–0:09] O problema real da Locaweb
[0:09–0:19] Resultados dos modelos
[0:19–0:29] ARIA — logo + 3 métricas chave
[0:29–0:42] Stack tecnológico
[0:42–0:55] Call to action + GitHub
"""


def main():
    print("Renderizando ARIA_Instagram_Reels.mp4 ...")
    print(f"Resolucao: {W}x{H} (9:16) | FPS: {FPS}")

    scenes_def = [
        ig_scene_hook(W, H, duration=3.0),       # 0:00–0:03 hook
        ig_scene_numeros(W, H, duration=5.0),     # 0:03–0:08 resultados
        ig_scene_aria(W, H, duration=4.5),        # 0:08–0:17 ARIA + métricas
        ig_scene_tech(W, H, duration=4.0),        # 0:17–0:28 stack
        ig_scene_cta(W, H, duration=5.0),         # 0:28–0:38 CTA + GitHub
    ]

    # Versão curta ajustada para ~55s
    clips = []
    for i, (make_frame, dur) in enumerate(scenes_def):
        print(f"  Cena {i+1}/{len(scenes_def)} ({dur:.1f}s)...")
        clip = build_clip(make_frame, dur,
                          fade_in=(i > 0),
                          fade_out=(i < len(scenes_def) - 1))
        clips.append(clip)

    print("Concatenando...")
    final = concatenate_videoclips(clips, method="compose")
    total = sum(d for _, d in scenes_def)
    print(f"Duracao total: {total:.0f}s")

    print(f"Escrevendo {OUT} ...")
    final.write_videofile(
        str(OUT),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print(f"\nPronto: {OUT}")
    print(NARRATION_IG)


if __name__ == "__main__":
    main()
