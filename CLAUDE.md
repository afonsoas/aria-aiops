# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Contexto do Projeto

**ARIA — Automated Response & Incident Analysis**  
Solução AIOps para a Locaweb, desenvolvida como Enterprise Challenge FIAP 2026 (Turma 2TSCO, Cluster 3).  
Dataset: `D:\AFONSO\enterprise_challenge\Material Locaweb\LW-DATASET.xlsx` — 122.543 incidentes reais (Jan/2023–Dez/2025).

---

## Comandos Essenciais

```bash
# Dashboard Streamlit (porta padrão 8501)
streamlit run dashboard/app.py

# API FastAPI (porta 8000, com hot-reload)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Treinar modelos ML (sobrescreve model/*.pkl)
python model/aria_model.py

# EDA (gera gráficos em eda/output/)
python eda/aria_eda.py

# Gerar PPTs das sprints
python enterprise_challenge/build_sprint1.py   # Sprint 1 — Ideação
python enterprise_challenge/build_sprint2.py   # Sprint 2 — Arquitetura
python enterprise_challenge/build_sprint3.py   # Sprint 3 — MVP Preliminar
python enterprise_challenge/build_sprint4.py   # Sprint 4 — Solução Final
```

**Variáveis de ambiente para Oracle ADB (opcionais — API funciona offline sem elas):**
```bash
ARIA_DB_USER=ADMIN
ARIA_DB_PASSWORD=...
ARIA_DB_DSN=host:1521/service_name
ARIA_WALLET_DIR=/caminho/wallet
ARIA_WALLET_PASSWORD=...
```

---

## Arquitetura

```
aria-aiops/
├── api/                          # FastAPI REST backend (Sprint 3)
│   ├── main.py                   # App principal, endpoints, startup
│   ├── schemas.py                # Pydantic I/O: IncidentInput, OLAPrediction, etc.
│   └── db.py                     # Oracle ADB (oracledb thin mode, fallback offline)
│
├── dashboard/
│   ├── app.py                    # Página Home (5 KPIs + destaques ML)
│   ├── utils/
│   │   ├── theme.py              # Sistema de tema: ARIA_CSS, PLOTLY_LAYOUT, helpers
│   │   ├── data_loader.py        # @st.cache_data — carrega e transforma LW-DATASET
│   │   └── model_loader.py       # @st.cache_resource — carrega model/*.pkl
│   └── pages/
│       ├── 1_kpi_overview.py     # Evolução temporal, heatmap, top grupos, taxa OLA
│       ├── 2_incident_list.py    # Tabela filtrável + badge de risco + exportar CSV
│       ├── 3_ola_predictor.py    # Formulário → gauge + feature importance
│       ├── 4_patterns.py         # Top N descrições, treemap, playbooks, hora do dia
│       └── 5_api_predictor.py    # Chama API REST, exibe histórico Oracle ADB
│
├── model/
│   ├── aria_model.py             # Treina Modelo A (XGBoost) e Modelo B (RF)
│   ├── model_ola.pkl             # Bundle: {model, tfidf, features}
│   ├── model_priority.pkl        # Bundle: {model, tfidf, features}
│   ├── encoders.pkl              # Dict de LabelEncoders por coluna
│   └── evaluation_report.txt     # Métricas detalhadas do último treinamento
│
└── eda/
    ├── aria_eda.py               # EDA com gráficos matplotlib/seaborn
    └── output/                   # PNGs gerados pelo EDA
```

---

## Padrões Críticos

### Imports no Streamlit multi-page
Todas as páginas em `dashboard/pages/` adicionam a raiz ao path antes de qualquer import local:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dashboard.utils.theme import inject_css, ...
from dashboard.utils.data_loader import load_data
```

### Modelo: estrutura dos bundles pkl
```python
# model_ola.pkl e model_priority.pkl têm a mesma estrutura:
bundle = {
    "model":    <XGBClassifier ou RandomForestClassifier>,
    "tfidf":    <TfidfVectorizer fitted>,
    "features": ["prio_num", "hora_abertura", "dia_semana", "mes",
                 "is_monitoring", "has_parent",
                 "produto_enc", "grupo_enc", "categoria_enc",
                 "subcategoria_enc", "cod_fechamento_enc"],
}
# Inferência: sp.hstack([num_array, tfidf_matrix]) → model.predict_proba(X)
```

### Tema Plotly — bug "undefined"
`PLOTLY_LAYOUT` em `theme.py` usa `title=dict(text="", ...)` — nunca `title_font=dict(...)` solto.  
`title_font` sem `title.text` definido causa renderização de "undefined" no topo dos gráficos.

### Texto cortado em barras Plotly
Sempre usar `cliponaxis=False` + `yaxis range` com 18–25% de headroom + margem `r` suficiente (≥ 80px) para barras horizontais com valores à direita.

### Selectboxes com NaN
```python
# CORRETO — evita TypeError: '<' not supported between 'str' and 'float'
st.selectbox("X", sorted(df["col"].dropna().unique()))
```

### API: fallback offline
`api/db.py` retorna `None` sem lançar exceção quando credenciais não configuradas.  
Todos os `insert_*` e `fetch_*` verificam `if conn is None: return`.  
A API responde normalmente — apenas não persiste/lê do banco.

---

## Modelos ML — Métricas do Último Treinamento

| | Modelo A — OLA (XGBoost + SMOTE) | Modelo B — Prioridade (RF) |
|---|---|---|
| Dataset | 25.600 elegíveis KPI | 122.209 incidentes prio 2-4 |
| Train/Test | 20.480 / 5.120 | 97.767 / 24.442 |
| ROC-AUC | **0.8382** | — |
| Recall (alvo) | **60%** (violações) | — |
| F1-macro | 0.50 | **0.8981** |
| Accuracy | 85% | **91%** |
| Precision (violação) | 4% (esperado com 0,97% base rate) | — |

**Top features Modelo A:** `domain`, `not running`, `recipes`, `is_monitoring`, `on`, `grupo_enc`  
**Top features Modelo B:** `has_parent`, `problem`, `check application`, `subcategoria_enc`, `application monitoring`

---

## Dataset — Colunas após data_loader.py

Colunas originais renomeadas + derivadas:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `numero` | str | ID do incidente |
| `prioridade` | str | Ex: "3 - Média" |
| `prio_num` | int | Extraído do início da string (1–5) |
| `produto`, `categoria`, `subcategoria`, `grupo` | str | Campos textuais limpos |
| `aberto`, `resolvido`, `encerrado` | datetime | Parseados com `errors="coerce"` |
| `hora_abertura` | int | 0–23 |
| `dia_semana` | int | 0=Seg … 6=Dom |
| `mes`, `ano` | int | |
| `ano_mes` | str | Ex: "2024-03" (Period→str) |
| `is_monitoring` | bool | True se "monitoramento" em `aberto_por` |
| `has_parent` | bool | True se `incidente_pai` preenchido |
| `kpi_violado` | str | "SIM" / "NÃO" (uppercase) |
| `entrou_kpi` | str | "SIM" / "NÃO" (uppercase) |
| `status` | str | Valor original limpo |
| `aberto_por` | str | Ex: "Monitoramento Zabbix" |

---

## API REST — Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/health` | Status: modelos + DB |
| POST | `/predict/ola` | Prob. violação OLA (XGBoost) |
| POST | `/predict/priority` | Prioridade predita 2/3/4 (RF) |
| GET | `/predictions/ola?limit=N` | Histórico Oracle ADB |
| GET | `/encoders/info` | Valores válidos dos LabelEncoders |
| GET | `/docs` | Swagger UI interativo |

**Payload POST `/predict/ola`:**
```json
{
  "prio_num": 3, "hora_abertura": 14, "dia_semana": 1,
  "mes": 6, "is_monitoring": 1, "has_parent": 0,
  "produto_enc": 0, "grupo_enc": 0, "categoria_enc": 0,
  "subcategoria_enc": 0, "cod_fechamento_enc": 0,
  "descricao": "Problem: Check Application Monitoring",
  "numero": "INC0012345",
  "produto": "Hospedagem",
  "grupo": "Team14"
}
```

---

## Sprints — Status

| Sprint | Tema | Prazo | Status | PPT |
|--------|------|-------|--------|-----|
| 1 | Ideação | 27/04/2026 | ✅ Entregue | `ARIA_Sprint1_Ideacao_Cluster3.pptx` |
| 2 | Arquitetura + Protótipos | 24/05/2026 | ✅ Entregue | `ARIA_Sprint2_Arquitetura_Cluster3.pptx` |
| 3 | MVP Preliminar | 23/08/2026 | ✅ Entregue | `ARIA_Sprint3_MVP_Cluster3.pptx` |
| 4 | Solução Final | 08/09/2026 | 🔄 Em desenvolvimento | `ARIA_Sprint4_SolucaoFinal_Cluster3.pptx` |

Todos os PPTs gerados programaticamente via `D:\AFONSO\enterprise_challenge\build_sprint*.py`.

---

## GitHub

Repositório: `https://github.com/afonsoas/aria-aiops`  
Branch principal: `main`  
Último commit Sprint 3: `ff26114`
