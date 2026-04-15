"""
ARIA — Gerador de Vídeos com Narração (edge-tts, vozes neurais PT-BR)

Gera dois arquivos:
  videos/ARIA_Entrega_Narrado.mp4     — 1920x1080 (~2 min, entrega profissional)
  videos/ARIA_Instagram_Narrado.mp4   — 1080x1920 (~30s, Reels)

Vozes disponíveis:
  pt-BR-AntonioNeural        (masculino, profissional)
  pt-BR-FranciscaNeural      (feminina, clara)
  pt-BR-ThalitaMultilingualNeural (feminina, natural)

Uso:
  cd D:/AFONSO/aria-aiops
  python videos/make_video_narrated.py
"""
import sys, asyncio, os, tempfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from PIL import ImageDraw
import edge_tts
from moviepy import VideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from moviepy.video.fx import FadeIn, FadeOut

from frame_engine import (
    scene_intro, scene_problema, scene_solucao, scene_metricas,
    scene_dashboard, scene_api, scene_encerramento,
    Canvas, BG, BG2, BG3, BLUE, CYAN, ORANGE, GREEN, PURPLE, WHITE, GRAY, GRAY2,
    ease_out, alpha_blend,
    ig_scene_hook, ig_scene_aria, ig_scene_cta,
)

# ── Re-importa as cenas do full video ────────────────────────
from make_video_full import scene_playbooks, scene_impacto

OUT_DIR = Path(__file__).resolve().parent
FADE    = 0.3

# ══════════════════════════════════════════════════════════════
# SCRIPTS DE NARRAÇÃO
# ══════════════════════════════════════════════════════════════

# Voz para entrega: Antonio — masculino, profissional
# Voz para Instagram: Francisca — feminina, energética
VOICE_FULL = "pt-BR-AntonioNeural"
VOICE_IG   = "pt-BR-FranciscaNeural"
RATE_FULL  = "+8%"    # ligeiramente mais rápido que padrão
RATE_IG    = "+18%"   # mais dinâmico para Reels

# Narração do vídeo de entrega — 1 texto por cena
NARRATION_FULL = [
    # cena 0 — Intro
    "ARIA. Automated Response and Incident Analysis. "
    "A solução AIOps desenvolvida para a Locaweb.",

    # cena 1 — O Problema
    "A Locaweb registra mais de 122 mil incidentes por ano. "
    "85 por cento são abertos automaticamente pelo monitoramento. "
    "Mas 248 violações de OLA ocorreram — e nenhuma foi antecipada. "
    "Um único grupo, o Team14, responde por 75 por cento de todos os casos.",

    # cena 2 — A Solução
    "A ARIA opera sobre quatro pilares. "
    "O Modelo A, baseado em XGBoost com SMOTE, prediz violações de OLA. "
    "O Modelo B, com Random Forest, classifica prioridades automaticamente. "
    "Um dashboard Streamlit de cinco páginas centraliza a gestão. "
    "E uma API REST FastAPI expõe os modelos em tempo real.",

    # cena 3 — Dashboard
    "O dashboard ARIA opera em modo escuro com glassmorphism profissional. "
    "Temos KPI Overview com evolução mensal e heatmap de horários. "
    "Lista de incidentes com badge de risco OLA e exportação em CSV. "
    "Preditor com gauge de probabilidade e feature importance. "
    "E a nova página de API, conectada ao Oracle Autonomous Database.",

    # cena 4 — Métricas
    "O Modelo A atingiu ROC-AUC de 0,84 com recall de 60 por cento. "
    "Com apenas 248 violações em 25 mil registros, aplicamos SMOTE "
    "para gerar 20 mil exemplos sintéticos positivos. "
    "O Modelo B entregou 91 por cento de acurácia e F1-macro de 0,90 "
    "para as três classes de prioridade.",

    # cena 5 — Playbooks
    "A análise dos padrões revelou que Check Application Monitoring "
    "representa 28 mil ocorrências — quase um em cada quatro incidentes. "
    "Para cada padrão recorrente, a ARIA sugere um playbook automático "
    "com as ações corretivas específicas.",

    # cena 6 — API
    "A API FastAPI expõe cinco endpoints documentados via Swagger. "
    "POST /predict/ola retorna a probabilidade e o nível de risco "
    "em menos de dois segundos. "
    "Todas as predições são persistidas no Oracle Autonomous Database "
    "no OCI, no tier gratuito.",

    # cena 7 — Impacto
    "Com a ARIA, esperamos redução de 60 por cento nas violações de OLA, "
    "triagem automática de prioridade em menos de dois segundos, "
    "e visibilidade operacional unificada para NOC e gestão. "
    "100 por cento open source, rodando em OCI free tier.",

    # cena 8 — Encerramento
    "ARIA. Resposta certa, no tempo certo, pelo caminho certo. "
    "Código completo em github.com/afonsoas/aria-aiops. "
    "Locaweb Enterprise Challenge 2026. FIAP 2TSCO. Cluster 3.",
]

# Narração Instagram — curta e impactante
NARRATION_IG = [
    # cena 0 — Hook
    "Cento e vinte e dois mil incidentes. "
    "Duzentas e quarenta e oito violações de SLA. Zero antecipação.",

    # cena 1 — Números
    "ROC-AUC de 0,84. 91 por cento de acurácia. API em menos de 2 segundos.",

    # cena 2 — ARIA
    "ARIA. O sistema AIOps treinado com dados reais da Locaweb.",

    # cena 3 — Stack
    "Python. XGBoost. Random Forest. FastAPI. Oracle ADB. Streamlit. "
    "100 por cento open source.",

    # cena 4 — CTA
    "Resposta certa, no tempo certo, pelo caminho certo. "
    "github.com/afonsoas/aria-aiops",
]

# ══════════════════════════════════════════════════════════════
# GERADOR DE ÁUDIO
# ══════════════════════════════════════════════════════════════

async def _generate_segment(text: str, voice: str, rate: str, path: str):
    tts = edge_tts.Communicate(text, voice=voice, rate=rate)
    await tts.save(path)


def generate_audio_segments(
    texts: list[str], voice: str, rate: str, prefix: str
) -> list[tuple[str, float]]:
    """
    Gera um arquivo MP3 por segmento e retorna lista de (path, duration_s).
    """
    results = []
    for i, text in enumerate(texts):
        path = str(OUT_DIR / f"_narr_{prefix}_{i:02d}.mp3")
        print(f"    TTS cena {i+1}/{len(texts)}...", end=" ", flush=True)
        asyncio.run(_generate_segment(text, voice, rate, path))
        clip = AudioFileClip(path)
        dur  = clip.duration
        clip.close()
        print(f"{dur:.2f}s")
        results.append((path, dur))
    return results


def merge_audio_segments(
    segments: list[tuple[str, float]],
    scene_durations: list[float],
    output_path: str,
) -> AudioFileClip:
    """
    Concatena segmentos com silêncio para preencher a duração de cada cena.
    Retorna um AudioFileClip total.
    """
    from moviepy import concatenate_audioclips
    import numpy as np
    from moviepy.audio.AudioClip import AudioArrayClip

    clips = []
    for i, ((path, audio_dur), scene_dur) in enumerate(
        zip(segments, scene_durations)
    ):
        aclip = AudioFileClip(path)
        # Centraliza o áudio na cena (pequeno silêncio no início)
        lead_silence = max((scene_dur - audio_dur) * 0.15, 0.1)
        silence_arr  = np.zeros((max(int(lead_silence * 44100), 1), 2))
        silence      = AudioArrayClip(silence_arr, fps=44100)
        clips.append(silence)
        clips.append(aclip)
        # Silêncio de cauda para preencher a cena
        tail = scene_dur - audio_dur - lead_silence
        if tail > 0.05:
            tail_arr = np.zeros((max(int(tail * 44100), 1), 2))
            clips.append(AudioArrayClip(tail_arr, fps=44100))

    full = concatenate_audioclips(clips)
    full.write_audiofile(output_path, fps=44100, logger=None)
    full.close()
    return AudioFileClip(output_path)


def cleanup_segments(segments: list[tuple[str, float]]):
    for path, _ in segments:
        try:
            os.unlink(path)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
# BUILD VÍDEO COMPLETO COM NARRAÇÃO
# ══════════════════════════════════════════════════════════════

def build_full_video():
    W, H = 1920, 1080
    FPS  = 24
    OUT  = str(OUT_DIR / "ARIA_Entrega_Narrado.mp4")

    print("\n=== VÍDEO DE ENTREGA (1920x1080) ===")

    # 1. Gerar áudio por cena
    print("Gerando narração (Antonio Neural, PT-BR)...")
    segments = generate_audio_segments(
        NARRATION_FULL, VOICE_FULL, RATE_FULL, "full"
    )

    # 2. Calcular duração de cada cena = max(áudio + buffer, mínimo visual)
    VISUAL_MIN = [2.5, 5.0, 4.5, 5.0, 4.5, 4.5, 4.5, 4.0, 4.0]
    BUFFER = 1.2   # segundos após o áudio terminar antes de trocar a cena
    scene_durations = []
    for i, (_, audio_dur) in enumerate(segments):
        dur = max(audio_dur + BUFFER, VISUAL_MIN[i])
        scene_durations.append(round(dur, 2))
        print(f"    Cena {i+1}: áudio {audio_dur:.2f}s → cena {dur:.2f}s")

    total_dur = sum(scene_durations)
    print(f"  Duração total: {total_dur:.1f}s ({total_dur/60:.1f} min)")

    # 3. Montar áudio completo
    print("Montando áudio completo...")
    audio_path = str(OUT_DIR / "_narr_full_combined.wav")
    audio_clip  = merge_audio_segments(segments, scene_durations, audio_path)

    # 4. Renderizar vídeo com durações corretas
    print("Renderizando vídeo...")
    scene_fns = [
        scene_intro(W, H,        scene_durations[0]),
        scene_problema(W, H,     scene_durations[1]),
        scene_solucao(W, H,      scene_durations[2]),
        scene_dashboard(W, H,    scene_durations[3]),
        scene_metricas(W, H,     scene_durations[4]),
        scene_playbooks(W, H,    scene_durations[5]),
        scene_api(W, H,          scene_durations[6]),
        scene_impacto(W, H,      scene_durations[7]),
        scene_encerramento(W, H, scene_durations[8]),
    ]

    clips = []
    for i, (mf, dur) in enumerate(scene_fns):
        print(f"    Cena {i+1}/9 ({dur:.1f}s)...")
        clip = VideoClip(mf, duration=dur)
        effects = []
        if i > 0:   effects.append(FadeIn(FADE))
        if i < 8:   effects.append(FadeOut(FADE))
        if effects: clip = clip.with_effects(effects)
        clips.append(clip)

    print("  Concatenando...")
    video = concatenate_videoclips(clips, method="compose")

    # 5. Combinar vídeo + áudio
    print("  Combinando áudio + vídeo...")
    # Ajusta áudio ao tamanho exato do vídeo
    if audio_clip.duration > video.duration:
        audio_clip = audio_clip.with_end(video.duration)
    final = video.with_audio(audio_clip)

    print(f"  Escrevendo {OUT}...")
    final.write_videofile(
        OUT, fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", ffmpeg_params=["-crf", "20"], logger="bar",
    )

    # Cleanup
    audio_clip.close()
    try: os.unlink(audio_path)
    except Exception: pass
    cleanup_segments(segments)

    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"\nPronto: {OUT} ({size_mb:.1f} MB, {total_dur:.0f}s)")


# ══════════════════════════════════════════════════════════════
# BUILD INSTAGRAM COM NARRAÇÃO
# ══════════════════════════════════════════════════════════════

def ig_scene_numeros_static(w, h, duration):
    """Versão sem ImageDraw local — usa Canvas normalmente."""
    nums = [
        ("0.84",  "ROC-AUC modelo OLA",           BLUE,   0.0),
        ("60%",   "Recall — violações detectadas", ORANGE, 0.4),
        ("91%",   "Acurácia prioridade",           CYAN,   0.8),
        ("< 2s",  "Resposta da API",               GREEN,  1.2),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (8, 18, 42))
        c.gradient_rect(0, 0, w, 6, BLUE, CYAN)

        a = ease_out(t, 0.4)
        if a > 0:
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("Resultados reais.", 0, int(h * 0.05), size=int(w * 0.085),
                     weight="bold", color=WHITE, align="center", max_w=w)
            tmp.text("Dados da Locaweb.", 0, int(h * 0.13), size=int(w * 0.085),
                     weight="bold", color=CYAN, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, a)
            c.draw = ImageDraw.Draw(c.img)

        for i, (val, lbl, color, delay) in enumerate(nums):
            appear = ease_out(max(t - delay, 0), 0.35)
            if appear <= 0:
                continue
            cy = int(h * 0.25) + i * int(h * 0.165)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.rect(int(w * 0.06), cy, int(w * 0.88), int(h * 0.135), BG3, radius=14)
            tmp2.rect(int(w * 0.06), cy, int(w * 0.88), 5, color, radius=3)
            tmp2.text(val, int(w * 0.1), cy + int(h * 0.022), size=int(w * 0.12),
                      weight="black", color=color)
            tmp2.text(lbl, int(w * 0.1), cy + int(h * 0.088), size=int(w * 0.05), color=GRAY)
            c.img = alpha_blend(c.img, tmp2.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)
        return c.numpy()
    return make_frame, duration


def ig_scene_tech_static(w, h, duration):
    techs = [
        ("Python", BLUE), ("XGBoost", ORANGE), ("Random Forest", CYAN),
        ("FastAPI", GREEN), ("Oracle ADB", PURPLE), ("Streamlit", BLUE),
        ("SMOTE", ORANGE), ("TF-IDF", CYAN),
    ]

    def make_frame(t):
        c = Canvas(w, h)
        c.gradient_rect(0, 0, w, h, BG, (6, 14, 32))
        c.gradient_rect(0, 0, w, 6, PURPLE, BLUE)

        a = ease_out(t, 0.4)
        if a > 0:
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.text("Stack 100%", 0, int(h * 0.05), size=int(w * 0.085),
                     weight="bold", color=WHITE, align="center", max_w=w)
            tmp.text("open source.", 0, int(h * 0.13), size=int(w * 0.085),
                     weight="bold", color=CYAN, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp.img, a)
            c.draw = ImageDraw.Draw(c.img)

        chip_w = int(w * 0.42); chip_h = int(h * 0.07)
        chip_gap = int(w * 0.03); cols = 2
        start_x = int(w * 0.07); start_y = int(h * 0.26)

        for i, (tech, color) in enumerate(techs):
            appear = ease_out(max(t - i * 0.18, 0), 0.35)
            if appear <= 0:
                continue
            row = i // cols; col = i % cols
            cx = start_x + col * (chip_w + chip_gap)
            cy = start_y + row * (chip_h + int(h * 0.02))
            tmp = Canvas(w, h, (0, 0, 0))
            tmp.rect(cx, cy, chip_w, chip_h, BG3, radius=10)
            tmp.rect(cx, cy, 6, chip_h, color, radius=3)
            tmp.text(tech, cx + int(chip_w * 0.1), cy + int(chip_h * 0.22),
                     size=int(w * 0.05), weight="bold", color=color)
            c.img = alpha_blend(c.img, tmp.img, min(appear * 2, 1.0))
            c.draw = ImageDraw.Draw(c.img)

        if t > 1.6:
            a2 = ease_out(t - 1.6, 0.4)
            tmp2 = Canvas(w, h, (0, 0, 0))
            tmp2.text("Zero licença. Deploy OCI free.",
                      0, int(h * 0.88), size=int(w * 0.055),
                      color=GRAY2, align="center", max_w=w)
            c.img = alpha_blend(c.img, tmp2.img, a2)
            c.draw = ImageDraw.Draw(c.img)
        return c.numpy()
    return make_frame, duration


def build_instagram_video():
    W, H = 1080, 1920
    FPS  = 30
    OUT  = str(OUT_DIR / "ARIA_Instagram_Narrado.mp4")

    print("\n=== INSTAGRAM REELS (1080x1920) ===")

    # 1. Gerar áudio
    print("Gerando narração (Francisca Neural, PT-BR)...")
    segments = generate_audio_segments(
        NARRATION_IG, VOICE_IG, RATE_IG, "ig"
    )

    VISUAL_MIN = [3.0, 4.5, 4.0, 3.5, 4.5]
    BUFFER = 0.9
    scene_durations = []
    for i, (_, audio_dur) in enumerate(segments):
        dur = max(audio_dur + BUFFER, VISUAL_MIN[i])
        scene_durations.append(round(dur, 2))
        print(f"    Cena {i+1}: áudio {audio_dur:.2f}s → cena {dur:.2f}s")

    total_dur = sum(scene_durations)
    print(f"  Duração total: {total_dur:.1f}s")

    # 2. Áudio
    print("Montando áudio...")
    audio_path = str(OUT_DIR / "_narr_ig_combined.wav")
    audio_clip  = merge_audio_segments(segments, scene_durations, audio_path)

    # 3. Vídeo
    print("Renderizando vídeo...")
    scene_fns = [
        ig_scene_hook(W, H,             scene_durations[0]),
        ig_scene_numeros_static(W, H,   scene_durations[1]),
        ig_scene_aria(W, H,             scene_durations[2]),
        ig_scene_tech_static(W, H,      scene_durations[3]),
        ig_scene_cta(W, H,              scene_durations[4]),
    ]

    clips = []
    n = len(scene_fns)
    for i, (mf, dur) in enumerate(scene_fns):
        print(f"    Cena {i+1}/{n} ({dur:.1f}s)...")
        clip = VideoClip(mf, duration=dur)
        effects = []
        if i > 0:     effects.append(FadeIn(FADE))
        if i < n - 1: effects.append(FadeOut(FADE))
        if effects:   clip = clip.with_effects(effects)
        clips.append(clip)

    print("  Concatenando...")
    video = concatenate_videoclips(clips, method="compose")

    print("  Combinando áudio + vídeo...")
    if audio_clip.duration > video.duration:
        audio_clip = audio_clip.with_end(video.duration)
    final = video.with_audio(audio_clip)

    print(f"  Escrevendo {OUT}...")
    final.write_videofile(
        OUT, fps=FPS, codec="libx264", audio_codec="aac",
        preset="fast", ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )

    audio_clip.close()
    try: os.unlink(audio_path)
    except Exception: pass
    cleanup_segments(segments)

    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"\nPronto: {OUT} ({size_mb:.1f} MB, {total_dur:.0f}s)")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["full", "ig"], default=None,
                   help="Renderizar apenas um dos vídeos")
    args = p.parse_args()

    t0 = time.time()
    if args.only == "ig":
        build_instagram_video()
    elif args.only == "full":
        build_full_video()
    else:
        build_instagram_video()
        build_full_video()

    elapsed = time.time() - t0
    print(f"\nTempo total: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print("\nArquivos gerados:")
    for f in ["ARIA_Entrega_Narrado.mp4", "ARIA_Instagram_Narrado.mp4"]:
        p2 = OUT_DIR / f
        if p2.exists():
            print(f"  {f}  ({p2.stat().st_size/1024/1024:.1f} MB)")
