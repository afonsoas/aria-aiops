"""Carregamento e cache do LW-DATASET para o dashboard ARIA."""
import os
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Caminho relativo ao root do projeto (funciona local e no Streamlit Cloud/OCI)
_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = Path(os.getenv("ARIA_DATA_FILE", str(_ROOT / "data" / "LW-DATASET.xlsx")))

@st.cache_data(show_spinner="Carregando dataset...")
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE, sheet_name="Dataset Geral", engine="openpyxl")
    df.columns = df.columns.str.strip()

    col_map = {
        "Número": "numero", "Numero": "numero",
        "Prioridade": "prioridade",
        "Produto": "produto",
        "Categoria": "categoria",
        "Subcategoria": "subcategoria",
        "Grupo designado": "grupo",
        "Item de configuração": "item_config", "Item de configuracao": "item_config",
        "Aberto": "aberto",
        "Resolvido": "resolvido",
        "Encerrado": "encerrado",
        "Duração": "duracao", "Duracao": "duracao",
        "Código de fechamento": "cod_fechamento", "Codigo de fechamento": "cod_fechamento",
        "Descrição resumida": "descricao", "Descricao resumida": "descricao",
        "Solução": "solucao", "Solucao": "solucao",
        "Aberto por": "aberto_por",
        "Incidente Pai": "incidente_pai",
        "Status": "status",
        "Entrou para KPI?": "entrou_kpi",
        "KPI Violado?": "kpi_violado",
    }
    df.rename(columns=col_map, inplace=True)

    # Limpeza
    df["prioridade"]  = df["prioridade"].astype(str).str.strip()
    df["kpi_violado"] = df["kpi_violado"].astype(str).str.strip().str.upper()
    df["entrou_kpi"]  = df["entrou_kpi"].astype(str).str.strip().str.upper()
    df["aberto_por"]  = df["aberto_por"].astype(str).str.strip()
    df["status"]      = df["status"].astype(str).str.strip()
    df["descricao"]   = df["descricao"].fillna("").astype(str)
    df["grupo"]       = df["grupo"].fillna("Desconhecido").astype(str).str.strip()
    df["produto"]     = df["produto"].fillna("Desconhecido").astype(str).str.strip()

    df["aberto"]    = pd.to_datetime(df["aberto"], errors="coerce")
    df["resolvido"] = pd.to_datetime(df["resolvido"], errors="coerce")
    df["encerrado"] = pd.to_datetime(df["encerrado"], errors="coerce")

    df["hora_abertura"] = df["aberto"].dt.hour
    df["dia_semana"]    = df["aberto"].dt.dayofweek
    df["mes"]           = df["aberto"].dt.month
    df["ano"]           = df["aberto"].dt.year
    df["ano_mes"]       = df["aberto"].dt.to_period("M").astype(str)

    def parse_prio(p):
        try:
            return int(str(p).strip()[0])
        except Exception:
            return np.nan

    df["prio_num"] = df["prioridade"].apply(parse_prio)

    df["is_monitoring"] = df["aberto_por"].str.lower().str.contains("monitoramento", na=False)
    df["has_parent"]    = (
        df["incidente_pai"].notna() &
        (df["incidente_pai"].astype(str).str.strip() != "") &
        (df["incidente_pai"].astype(str).str.strip().str.lower() != "nan")
    )

    return df


def prio_label(p) -> str:
    mapa = {"1": "1-Critica", "2": "2-Alta", "3": "3-Media", "4": "4-Baixa", "5": "5-Muito Baixa"}
    return mapa.get(str(p).strip()[0] if str(p).strip() else "?", str(p))


PRIO_COLORS = {
    "1-Critica":     "#E74C3C",
    "2-Alta":        "#FF6B35",
    "3-Media":       "#105BD8",
    "4-Baixa":       "#00C87A",
    "5-Muito Baixa": "#00D4FF",
}

NAVY   = "#0D1B3E"
BLUE   = "#105BD8"
CYAN   = "#00D4FF"
ORANGE = "#FF6B35"
GREEN  = "#00C87A"
