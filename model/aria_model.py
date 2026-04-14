"""
ARIA — Automated Response & Incident Analysis
Treinamento dos Modelos ML
  Modelo A: Predicao de violacao OLA (XGBoost, binario)
  Modelo B: Classificacao de prioridade (RandomForest, multiclasse)
Cluster 3 | 2TSCO | FIAP 2026
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import warnings
warnings.filterwarnings("ignore")

import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, f1_score, recall_score
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import scipy.sparse as sp

# ── Paths ────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
DATA_FILE  = Path(r"D:\AFONSO\enterprise_challenge\Material Locaweb\LW-DATASET.xlsx")
MODEL_OLA      = BASE_DIR / "model_ola.pkl"
MODEL_PRIORITY = BASE_DIR / "model_priority.pkl"
ENCODERS_FILE  = BASE_DIR / "encoders.pkl"
REPORT_FILE    = BASE_DIR / "evaluation_report.txt"

report_lines = []

def log(msg=""):
    print(msg)
    report_lines.append(str(msg))

# ════════════════════════════════════════════════════════════
# 1. CARREGAMENTO E LIMPEZA
# ════════════════════════════════════════════════════════════
log("=" * 60)
log("ARIA — Treinamento dos Modelos ML")
log("=" * 60)
log(f"\nCarregando: {DATA_FILE}")

dtype_map = {
    "Prioridade": str, "Produto": str, "Categoria": str,
    "Subcategoria": str, "Grupo designado": str,
    "Codigo de fechamento": str, "Descricao resumida": str,
    "Aberto por": str, "Incidente Pai": str, "Status": str,
    "Entrou para KPI?": str, "KPI Violado?": str,
}

df = pd.read_excel(DATA_FILE, sheet_name="Dataset Geral", engine="openpyxl")
df.columns = df.columns.str.strip()

# Renomear colunas com caracteres especiais para facilitar
col_map = {
    "Numero": "numero",
    "Número": "numero",
    "Prioridade": "prioridade",
    "Produto": "produto",
    "Categoria": "categoria",
    "Subcategoria": "subcategoria",
    "Grupo designado": "grupo",
    "Item de configuracao": "item_config",
    "Item de configuração": "item_config",
    "Aberto": "aberto",
    "Resolvido": "resolvido",
    "Encerrado": "encerrado",
    "Duracao": "duracao",
    "Duração": "duracao",
    "Codigo de fechamento": "cod_fechamento",
    "Código de fechamento": "cod_fechamento",
    "Descricao resumida": "descricao",
    "Descrição resumida": "descricao",
    "Solucao": "solucao",
    "Solução": "solucao",
    "Aberto por": "aberto_por",
    "Incidente Pai": "incidente_pai",
    "Status": "status",
    "Entrou para KPI?": "entrou_kpi",
    "KPI Violado?": "kpi_violado",
}
df.rename(columns=col_map, inplace=True)

log(f"Shape original: {df.shape}")

# Limpeza
df["prioridade"]   = df["prioridade"].astype(str).str.strip()
df["kpi_violado"]  = df["kpi_violado"].astype(str).str.strip().str.upper()
df["entrou_kpi"]   = df["entrou_kpi"].astype(str).str.strip().str.upper()
df["aberto_por"]   = df["aberto_por"].astype(str).str.strip()
df["descricao"]    = df["descricao"].fillna("").astype(str).str.strip()
df["grupo"]        = df["grupo"].fillna("Desconhecido").astype(str).str.strip()
df["produto"]      = df["produto"].fillna("Desconhecido").astype(str).str.strip()
df["categoria"]    = df["categoria"].fillna("Desconhecido").astype(str).str.strip()
df["subcategoria"] = df["subcategoria"].fillna("Desconhecido").astype(str).str.strip()

# Parse timestamps
df["aberto"] = pd.to_datetime(df["aberto"], errors="coerce")

# ════════════════════════════════════════════════════════════
# 2. ENGENHARIA DE FEATURES
# ════════════════════════════════════════════════════════════
log("\n--- Engenharia de Features ---")

# Extrair prioridade numerica (1-5)
def parse_prio(p):
    try:
        return int(str(p).strip()[0])
    except Exception:
        return np.nan

df["prio_num"] = df["prioridade"].apply(parse_prio)

# Features temporais
df["hora_abertura"] = df["aberto"].dt.hour.fillna(0).astype(int)
df["dia_semana"]    = df["aberto"].dt.dayofweek.fillna(0).astype(int)
df["mes"]           = df["aberto"].dt.month.fillna(1).astype(int)

# Features booleanas
df["is_monitoring"] = (df["aberto_por"].str.lower().str.contains("monitoramento", na=False)).astype(int)
df["has_parent"]    = (df["incidente_pai"].notna() & (df["incidente_pai"].astype(str).str.strip() != "") & (df["incidente_pai"].astype(str).str.strip().str.lower() != "nan")).astype(int)

# Label Encoders para categóricas
encoders = {}
for col in ["produto", "grupo", "categoria", "subcategoria", "cod_fechamento"]:
    le = LabelEncoder()
    df[f"{col}_enc"] = le.fit_transform(df[col].fillna("Desconhecido").astype(str))
    encoders[col] = le

log(f"Features criadas: hora_abertura, dia_semana, mes, is_monitoring, has_parent")
log(f"Encoders: produto ({df['produto'].nunique()}), grupo ({df['grupo'].nunique()}), "
    f"categoria ({df['categoria'].nunique()})")

# Features numericas base
NUM_FEATURES = [
    "prio_num", "hora_abertura", "dia_semana", "mes",
    "is_monitoring", "has_parent",
    "produto_enc", "grupo_enc", "categoria_enc", "subcategoria_enc",
]

# ════════════════════════════════════════════════════════════
# 3. MODELO A — PREDICAO DE VIOLACAO OLA
# ════════════════════════════════════════════════════════════
log("\n" + "=" * 50)
log("MODELO A — Predicao de Violacao OLA")
log("=" * 50)

# Filtrar apenas registros que entram no KPI
df_kpi = df[df["entrou_kpi"] == "SIM"].copy()
log(f"Registros elegíveis para KPI: {len(df_kpi):,}")

# Target binario: 1 = violou OLA, 0 = nao violou
df_kpi["target_ola"] = (df_kpi["kpi_violado"] == "SIM").astype(int)
log(f"Violacoes (target=1): {df_kpi['target_ola'].sum():,} ({df_kpi['target_ola'].mean()*100:.2f}%)")
log(f"Nao violacoes (target=0): {(df_kpi['target_ola']==0).sum():,}")

# Remover features que vazam informacao
LEAK_COLS = ["duracao", "resolvido", "encerrado", "kpi_violado", "entrou_kpi", "solucao"]
feat_cols_A = [c for c in NUM_FEATURES if c in df_kpi.columns and c not in LEAK_COLS]

# Substituir NaN nas features
X_num_A = df_kpi[feat_cols_A].fillna(0).values
y_A = df_kpi["target_ola"].values

# TF-IDF nas descricoes
log("Vetorizando descricoes (TF-IDF top-50)...")
tfidf_A = TfidfVectorizer(max_features=50, ngram_range=(1, 2), min_df=3)
X_tfidf_A = tfidf_A.fit_transform(df_kpi["descricao"])
X_A = sp.hstack([X_num_A, X_tfidf_A])

log(f"Shape X_A: {X_A.shape}")

# Split treino/teste estratificado
X_train_A, X_test_A, y_train_A, y_test_A = train_test_split(
    X_A, y_A, test_size=0.2, random_state=42, stratify=y_A
)
log(f"Treino: {X_train_A.shape[0]:,} | Teste: {X_test_A.shape[0]:,}")

# SMOTE para balancear
log("Aplicando SMOTE...")
sm = SMOTE(random_state=42, k_neighbors=5)
X_train_res, y_train_res = sm.fit_resample(X_train_A, y_train_A)
log(f"Apos SMOTE — pos: {y_train_res.sum():,} | neg: {(y_train_res==0).sum():,}")

# XGBoost
log("Treinando XGBoost...")
n_pos = (y_train_A == 1).sum()
n_neg = (y_train_A == 0).sum()
scale = n_neg / max(n_pos, 1)

model_A = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=scale,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
model_A.fit(X_train_res, y_train_res)

# Avaliacao
y_pred_A = model_A.predict(X_test_A)
y_prob_A = model_A.predict_proba(X_test_A)[:, 1]

log("\n--- Resultados Modelo A (XGBoost - OLA) ---")
log(classification_report(y_test_A, y_pred_A, target_names=["Nao Viola", "Viola OLA"]))
log(f"ROC-AUC:  {roc_auc_score(y_test_A, y_prob_A):.4f}")
log(f"Recall (violacoes): {recall_score(y_test_A, y_pred_A):.4f}")
log(f"F1 (violacoes):     {f1_score(y_test_A, y_pred_A):.4f}")

cm_A = confusion_matrix(y_test_A, y_pred_A)
log(f"Matriz de Confusao:\n{cm_A}")

# Feature importance
feat_names_A = feat_cols_A + tfidf_A.get_feature_names_out().tolist()
importances_A = model_A.feature_importances_
top_feat_A = sorted(zip(feat_names_A, importances_A), key=lambda x: x[1], reverse=True)[:10]
log("\nTop 10 features (Modelo A):")
for fname, fimp in top_feat_A:
    log(f"  {fname:<35} {fimp:.4f}")

# Salvar Modelo A
joblib.dump({"model": model_A, "tfidf": tfidf_A, "features": feat_cols_A}, MODEL_OLA)
log(f"\nModelo A salvo: {MODEL_OLA}")

# ════════════════════════════════════════════════════════════
# 4. MODELO B — CLASSIFICACAO DE PRIORIDADE
# ════════════════════════════════════════════════════════════
log("\n" + "=" * 50)
log("MODELO B — Classificacao de Prioridade")
log("=" * 50)

# Filtrar registros com prioridade valida (2, 3, 4 — remover 1 e 5 por volume)
df_b = df[df["prio_num"].isin([2, 3, 4])].copy()
log(f"Registros com prio 2-4: {len(df_b):,}")
log(df_b["prio_num"].value_counts().sort_index().to_string())

# Features sem prioridade (target)
feat_cols_B = [c for c in NUM_FEATURES if c != "prio_num" and c in df_b.columns]
X_num_B = df_b[feat_cols_B].fillna(0).values
y_B = df_b["prio_num"].values

# TF-IDF nas descricoes
log("Vetorizando descricoes (TF-IDF top-50)...")
tfidf_B = TfidfVectorizer(max_features=50, ngram_range=(1, 2), min_df=5)
X_tfidf_B = tfidf_B.fit_transform(df_b["descricao"])
X_B = sp.hstack([X_num_B, X_tfidf_B])

log(f"Shape X_B: {X_B.shape}")

# Split
X_train_B, X_test_B, y_train_B, y_test_B = train_test_split(
    X_B, y_B, test_size=0.2, random_state=42, stratify=y_B
)
log(f"Treino: {X_train_B.shape[0]:,} | Teste: {X_test_B.shape[0]:,}")

# Random Forest
log("Treinando Random Forest...")
model_B = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
model_B.fit(X_train_B.toarray(), y_train_B)

y_pred_B = model_B.predict(X_test_B.toarray())

log("\n--- Resultados Modelo B (Random Forest - Prioridade) ---")
log(classification_report(y_test_B, y_pred_B,
    target_names=["2-Alta", "3-Media", "4-Baixa"]))
log(f"F1-macro: {f1_score(y_test_B, y_pred_B, average='macro'):.4f}")
log(f"F1-weighted: {f1_score(y_test_B, y_pred_B, average='weighted'):.4f}")

cm_B = confusion_matrix(y_test_B, y_pred_B)
log(f"Matriz de Confusao:\n{cm_B}")

# Feature importance
feat_names_B = feat_cols_B + tfidf_B.get_feature_names_out().tolist()
importances_B = model_B.feature_importances_
top_feat_B = sorted(zip(feat_names_B, importances_B), key=lambda x: x[1], reverse=True)[:10]
log("\nTop 10 features (Modelo B):")
for fname, fimp in top_feat_B:
    log(f"  {fname:<35} {fimp:.4f}")

# Salvar Modelo B + encoders
joblib.dump({"model": model_B, "tfidf": tfidf_B, "features": feat_cols_B}, MODEL_PRIORITY)
joblib.dump(encoders, ENCODERS_FILE)
log(f"\nModelo B salvo: {MODEL_PRIORITY}")
log(f"Encoders salvos: {ENCODERS_FILE}")

# ════════════════════════════════════════════════════════════
# 5. SALVAR RELATORIO
# ════════════════════════════════════════════════════════════
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

log(f"\nRelatorio salvo: {REPORT_FILE}")
log("\nTreinamento concluido!")
