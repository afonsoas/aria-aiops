"""
ARIA — Automated Response & Incident Analysis
Análise Exploratória de Dados (EDA) — LW-DATASET.xlsx
Cluster 3 | 2TSCO | FIAP 2026
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração de paths
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_FILE  = Path(r"D:\AFONSO\enterprise_challenge\Material Locaweb\LW-DATASET.xlsx")
OUTPUT_DIR = BASE_DIR / "eda" / "output"
REPORT_TXT = OUTPUT_DIR / "eda_report.txt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Paleta ARIA
# ---------------------------------------------------------------------------
NAVY   = "#0D1B3E"
BLUE   = "#105BD8"
CYAN   = "#00D4FF"
ORANGE = "#FF6B35"
GREEN  = "#00C87A"
PALETTE = [BLUE, ORANGE, GREEN, CYAN, "#9B59B6", "#E74C3C", "#F1C40F"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.edgecolor":   "#CCCCCC",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
    "font.family":      "sans-serif",
})

report_lines = []

def log(msg: str):
    print(msg)
    report_lines.append(msg)

def save(fig, name: str):
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> Salvo: {path.name}")

# ---------------------------------------------------------------------------
# 1. Carregamento
# ---------------------------------------------------------------------------
log("=" * 60)
log("ARIA — EDA Report")
log("=" * 60)
log(f"\nCarregando dataset: {DATA_FILE}")

dtype_map = {
    "Número":              str,
    "Prioridade":          str,
    "Produto":             str,
    "Categoria":           str,
    "Subcategoria":        str,
    "Grupo designado":     str,
    "Código de fechamento":str,
    "Descrição resumida":  str,
    "Aberto por":          str,
    "Incidente Pai":       str,
    "Status":              str,
    "Entrou para KPI?":    str,
    "KPI Violado?":        str,
}

df = pd.read_excel(
    DATA_FILE,
    sheet_name="Dataset Geral",
    dtype=dtype_map,
    engine="openpyxl",
)

log(f"Shape: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
log(f"Colunas: {list(df.columns)}\n")

# Limpeza básica
df.columns = df.columns.str.strip()
df["Prioridade"] = df["Prioridade"].str.strip()
df["KPI Violado?"] = df["KPI Violado?"].str.strip().str.upper()
df["Entrou para KPI?"] = df["Entrou para KPI?"].str.strip().str.upper()
df["Aberto por"] = df["Aberto por"].str.strip()
df["Status"] = df["Status"].str.strip()

# Timestamps
for col in ["Aberto", "Resolvido", "Encerrado"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

if "Aberto" in df.columns:
    df["hora_abertura"] = df["Aberto"].dt.hour
    df["dia_semana"]    = df["Aberto"].dt.dayofweek
    df["mes"]           = df["Aberto"].dt.month
    df["ano"]           = df["Aberto"].dt.year

# ---------------------------------------------------------------------------
# 2. Estatísticas gerais
# ---------------------------------------------------------------------------
log("\n--- Estatísticas Gerais ---")
log(f"Total de incidentes: {len(df):,}")
log(f"Período: {df['Aberto'].min()} → {df['Aberto'].max()}" if "Aberto" in df.columns else "")

pct_monitor = (df["Aberto por"].str.lower().str.contains("monitoramento", na=False).sum() / len(df) * 100)
log(f"Abertos por Monitoramento: {pct_monitor:.1f}%")

sem_interv = (df["Status"].str.contains("Sem Interven", na=False, case=False).sum() / len(df) * 100)
log(f"Status 'Sem Intervenção': {sem_interv:.1f}%")

kpi_df    = df[df["Entrou para KPI?"] == "SIM"]
violados  = (kpi_df["KPI Violado?"] == "SIM").sum()
log(f"Entrou para KPI: {len(kpi_df):,}")
log(f"KPI Violado (SIM): {violados:,}")

# ---------------------------------------------------------------------------
# 3. Gráfico 1 — Distribuição de Prioridades
# ---------------------------------------------------------------------------
log("\n--- Plot 1: Distribuição de Prioridades ---")
prio_map = {
    "1": "1-Crítica", "1-crítica": "1-Crítica", "1-Crítica": "1-Crítica",
    "2": "2-Alta",    "2-alta": "2-Alta",        "2-Alta": "2-Alta",
    "3": "3-Média",   "3-média": "3-Média",      "3-Média": "3-Média",
    "4": "4-Baixa",   "4-baixa": "4-Baixa",      "4-Baixa": "4-Baixa",
    "5": "5-Muito Baixa", "5-muito baixa": "5-Muito Baixa", "5-Muito Baixa": "5-Muito Baixa",
}
df["Prioridade_Label"] = df["Prioridade"].map(lambda x: next((v for k, v in prio_map.items() if str(x).strip().lower() == k.lower()), str(x)))
prio_counts = df["Prioridade_Label"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(prio_counts.index, prio_counts.values, color=[NAVY, ORANGE, BLUE, GREEN, CYAN][:len(prio_counts)])
ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=9)
ax.set_title("Distribuição de Incidentes por Prioridade", fontweight="bold", color=NAVY)
ax.set_xlabel("Prioridade")
ax.set_ylabel("Qtd. Incidentes")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig.tight_layout()
save(fig, "01_distribuicao_prioridade")

for p, n in zip(prio_counts.index, prio_counts.values):
    log(f"  {p}: {n:,}")

# ---------------------------------------------------------------------------
# 4. Gráfico 2 — Taxa de Violação OLA por Prioridade
# ---------------------------------------------------------------------------
log("\n--- Plot 2: Taxa de Violação OLA por Prioridade ---")
kpi_prio = (
    kpi_df
    .groupby("Prioridade_Label" if "Prioridade_Label" in kpi_df.columns else "Prioridade")["KPI Violado?"]
    .value_counts(normalize=True)
    .unstack(fill_value=0)
    .get("SIM", pd.Series(dtype=float))
    * 100
)

if len(kpi_prio) > 0:
    fig, ax = plt.subplots(figsize=(7, 4))
    kpi_prio.sort_index().plot(kind="bar", ax=ax, color=ORANGE, edgecolor=NAVY)
    ax.set_title("Taxa de Violação OLA (%) por Prioridade", fontweight="bold", color=NAVY)
    ax.set_xlabel("Prioridade")
    ax.set_ylabel("% de Violação")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    save(fig, "02_taxa_violacao_ola")
    log(kpi_prio.to_string())

# ---------------------------------------------------------------------------
# 5. Gráfico 3 — Top 20 Descrições mais frequentes
# ---------------------------------------------------------------------------
log("\n--- Plot 3: Top 20 Descrições ---")
if "Descrição resumida" in df.columns:
    top20 = df["Descrição resumida"].value_counts().head(20)
    fig, ax = plt.subplots(figsize=(10, 6))
    top20[::-1].plot(kind="barh", ax=ax, color=BLUE)
    ax.set_title("Top 20 Descrições de Incidentes Mais Frequentes", fontweight="bold", color=NAVY)
    ax.set_xlabel("Frequência")
    fig.tight_layout()
    save(fig, "03_top20_descricoes")
    log(top20.to_string())

# ---------------------------------------------------------------------------
# 6. Gráfico 4 — Evolução temporal (por mês)
# ---------------------------------------------------------------------------
log("\n--- Plot 4: Evolução Temporal ---")
if "mes" in df.columns and "ano" in df.columns:
    df["ano_mes"] = df["Aberto"].dt.to_period("M")
    tempo = df.groupby("ano_mes").size().sort_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(tempo.index.astype(str), tempo.values, color=BLUE, linewidth=2, marker="o", markersize=3)
    ax.fill_between(range(len(tempo)), tempo.values, alpha=0.15, color=CYAN)
    ax.set_title("Evolução Mensal de Incidentes", fontweight="bold", color=NAVY)
    ax.set_ylabel("Qtd. Incidentes")
    ax.set_xlabel("Mês")
    step = max(1, len(tempo) // 10)
    ax.set_xticks(range(0, len(tempo), step))
    ax.set_xticklabels([str(tempo.index[i]) for i in range(0, len(tempo), step)], rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    save(fig, "04_evolucao_temporal")

# ---------------------------------------------------------------------------
# 7. Gráfico 5 — Top 10 Grupos × Violação
# ---------------------------------------------------------------------------
log("\n--- Plot 5: Heatmap Grupo × Prioridade ---")
if "Grupo designado" in df.columns:
    top_grupos = df["Grupo designado"].value_counts().head(10).index
    heatmap_df = (
        df[df["Grupo designado"].isin(top_grupos)]
        .groupby(["Grupo designado", "Prioridade_Label" if "Prioridade_Label" in df.columns else "Prioridade"])
        .size()
        .unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap_df, annot=True, fmt=",d", cmap="Blues", linewidths=0.5, ax=ax)
    ax.set_title("Heatmap: Top 10 Grupos × Prioridade", fontweight="bold", color=NAVY)
    ax.set_xlabel("Prioridade")
    ax.set_ylabel("Grupo Designado")
    fig.tight_layout()
    save(fig, "05_heatmap_grupo_prioridade")

    top5_grupos = df["Grupo designado"].value_counts().head(5)
    log("\nTop 5 grupos:")
    log(top5_grupos.to_string())

# ---------------------------------------------------------------------------
# 8. Gráfico 6 — Distribuição por hora do dia
# ---------------------------------------------------------------------------
log("\n--- Plot 6: Distribuição por Hora ---")
if "hora_abertura" in df.columns:
    hora_counts = df["hora_abertura"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(hora_counts.index, hora_counts.values, color=CYAN, edgecolor=NAVY, linewidth=0.5)
    ax.set_title("Distribuição de Abertura por Hora do Dia", fontweight="bold", color=NAVY)
    ax.set_xlabel("Hora")
    ax.set_ylabel("Qtd. Incidentes")
    ax.set_xticks(range(0, 24))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    save(fig, "06_abertura_por_hora")

# ---------------------------------------------------------------------------
# 9. Salvar relatório
# ---------------------------------------------------------------------------
log("\n--- Features relevantes para ML ---")
log("Numéricas: hora_abertura, dia_semana, mes, is_monitoring, has_parent")
log("Categóricas: Prioridade, Produto, Grupo designado, Categoria, Subcategoria")
log("Texto: Descrição resumida (TF-IDF top-50)")
log("Target A (OLA): KPI Violado? == 'SIM' (filtrar Entrou para KPI? == 'SIM')")
log("Target B (Prioridade): Prioridade (1-5, agrupar 1+2 se necessário)")

with open(REPORT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n✓ Relatório salvo em: {REPORT_TXT}")
print(f"✓ Gráficos salvos em: {OUTPUT_DIR}")
print("EDA concluída!")
