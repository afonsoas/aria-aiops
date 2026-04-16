# ARIA — Automated Response & Incident Analysis

> *"Resposta certa, no tempo certo, pelo caminho certo."*

[![Dashboard](https://img.shields.io/badge/Dashboard-Online-00C87A?logo=streamlit&logoColor=white)](https://afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app)
[![API](https://img.shields.io/badge/API-Online-105BD8?logo=fastapi&logoColor=white)](https://aria-api-production.up.railway.app/health)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Oracle](https://img.shields.io/badge/DB-Oracle%20ADB-F80000?logo=oracle)](https://www.oracle.com/cloud/free/)
[![FIAP](https://img.shields.io/badge/FIAP-Enterprise%20Challenge%202026-ED1C24)](https://fiap.com.br)

---

## Links de Acesso

| Componente | URL | Status |
|---|---|---|
| **Dashboard** | [afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app](https://afonsoas-aria-aiops-streamlit-app-wsp1zy.streamlit.app) | 🟢 Online |
| **API REST** | [aria-api-production.up.railway.app](https://aria-api-production.up.railway.app/health) | 🟢 Online |
| **Swagger UI** | [aria-api-production.up.railway.app/docs](https://aria-api-production.up.railway.app/docs) | 🟢 Online |
| **Manual PDF** | [`docs/ARIA_Manual_Utilizacao.pdf`](docs/ARIA_Manual_Utilizacao.pdf) | 📄 14 páginas |

---

## O Problema

A Locaweb registra **122.543 incidentes/ano**, dos quais:

| Indicador | Valor |
|---|---|
| Violações de OLA | **248** (42 Alta + 206 Média) |
| Incidentes sem intervenção humana | **65%** |
| Abertos por monitoramento automático | **85%** |
| Concentração em um único time | **75% no Team14** |

## A Solução

ARIA é um sistema AIOps que **prediz violações de OLA antes que aconteçam**, classifica automaticamente a prioridade de incidentes e centraliza a gestão operacional em um dashboard analítico.

```
[Fonte de Dados]         [Processamento]          [Saída]
LW-DATASET.xlsx  ──►  Python + Pandas         ──►  Streamlit Dashboard
Monitoramento    ──►  XGBoost (OLA)           ──►  Alertas em tempo real
em tempo real    ──►  RandomForest (Prio)     ──►  API REST (FastAPI)
                 ──►  TF-IDF (Texto)          ──►  Oracle Autonomous DB
                 ──►  SMOTE (balanceamento)
```

### Métricas dos Modelos

| Modelo | Algoritmo | ROC-AUC / F1 | Dataset de Treino |
|---|---|---|---|
| Modelo A — Predição OLA | XGBoost + SMOTE | ROC-AUC **0.84** · Recall **60%** | 20.480 incidentes |
| Modelo B — Classificação Prioridade | Random Forest | F1-macro **0.90** · Accuracy **91%** | 97.767 incidentes |

---

## Páginas do Dashboard

| Página | URL | Descrição |
|---|---|---|
| Home | `/` | KPIs globais + visão geral dos modelos |
| KPI Overview | `/kpi_overview` | 6 gráficos de análise de indicadores |
| Incidentes | `/incident_list` | Tabela filtrável com todos os incidentes |
| Preditor OLA | `/ola_predictor` | Predição de risco de violação OLA em tempo real |
| Padrões | `/patterns` | Heatmaps e análise de comportamento |
| API Live | `/api_predictor` | Interface para testar a API REST + histórico ADB |

> **Documentação completa:** ver [`docs/ARIA_Manual_Utilizacao.pdf`](docs/ARIA_Manual_Utilizacao.pdf)

---

## Stack

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.12 |
| Data | Pandas, NumPy, OpenPyXL | >= 2.0 |
| ML | Scikit-learn, XGBoost, imbalanced-learn | >= 1.3 / 2.0 / 0.11 |
| NLP | TF-IDF + scipy.sparse | >= 1.11 |
| Dashboard | Streamlit + Plotly | >= 1.28 |
| API | FastAPI + Uvicorn | >= 0.104 |
| Banco | Oracle Autonomous DB (oracledb thin mode) | >= 2.0 |
| Deploy API | Railway.app (Docker) | Free tier |
| Deploy Dashboard | Streamlit Community Cloud | Free tier |

---

## Estrutura do Projeto

```
aria-aiops/
├── data/
│   └── LW-DATASET.xlsx          — dataset Locaweb (122.543 registros)
├── model/
│   ├── aria_model.py            — script de treinamento
│   ├── model_ola.pkl            — modelo XGBoost (OLA)
│   ├── model_priority.pkl       — modelo Random Forest (prioridade)
│   ├── encoders.pkl             — LabelEncoders
│   └── evaluation_report.txt   — métricas detalhadas
├── api/
│   ├── main.py                  — FastAPI app (5 endpoints)
│   ├── schemas.py               — Pydantic schemas
│   └── db.py                   — Oracle ADB (thin mode)
├── dashboard/
│   ├── app.py                   — Home / navegação
│   ├── pages/
│   │   ├── 1_kpi_overview.py    — KPIs + gráficos temporais
│   │   ├── 2_incident_list.py   — tabela filtrável + badges
│   │   ├── 3_ola_predictor.py   — preditor com gauge
│   │   ├── 4_patterns.py        — heatmaps + padrões
│   │   └── 5_api_predictor.py   — integração API REST + histórico ADB
│   └── utils/
│       ├── data_loader.py       — carrega e normaliza o dataset
│       ├── model_loader.py      — carrega modelos pkl
│       └── theme.py             — CSS glassmorphism + helpers Plotly
├── docs/
│   ├── build_manual.py          — gerador do PDF do manual
│   └── ARIA_Manual_Utilizacao.pdf
├── pages/                       — stubs para Streamlit Cloud (não editar)
├── eda/
│   └── aria_eda.py              — análise exploratória
├── streamlit_app.py             — entry point Streamlit Cloud
├── Dockerfile                   — imagem Docker para a API
├── docker-compose.yml           — orquestração local
├── entrypoint.sh                — init do container (wallet Oracle)
├── render.yaml                  — deploy alternativo Render.com
└── .env.example                 — template de variáveis de ambiente
```

---

## Instalação Local

```bash
git clone https://github.com/afonsoas/aria-aiops.git
cd aria-aiops
pip install -r requirements.txt
```

### Rodar a API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# Swagger UI: http://localhost:8000/docs
```

### Rodar o Dashboard

```bash
streamlit run dashboard/app.py
# Acesso: http://localhost:8501
```

### Rodar com Docker

```bash
cp .env.example .env    # preencha com suas credenciais
docker-compose up --build
# API:       http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

---

## Configuração do Oracle ADB

1. Crie um Autonomous Database no OCI (Always Free — 20GB grátis)
2. Baixe a Wallet: **OCI Console → Database → Connection → Download Wallet**
3. Extraia para `wallet/`
4. Configure as variáveis de ambiente:

| Variável | Descrição |
|---|---|
| `ARIA_DB_USER` | Usuário do banco (padrão: `ADMIN`) |
| `ARIA_DB_PASSWORD` | Senha do ADMIN |
| `ARIA_DB_DSN` | TNS alias (ex: `ariaaiops_high`) |
| `ARIA_WALLET_DIR` | Caminho para a pasta da wallet |
| `ARIA_WALLET_PASSWORD` | Senha definida ao baixar a wallet |

As tabelas `ARIA_OLA_PREDICTIONS` e `ARIA_PRIORITY_PREDICTIONS` são criadas automaticamente na primeira execução.

---

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Status: API, modelos e DB |
| `POST` | `/predict/ola` | Probabilidade de violação OLA (0–100%) |
| `POST` | `/predict/priority` | Classificação de prioridade (2, 3 ou 4) |
| `GET` | `/predictions/ola?limit=N` | Histórico do Oracle ADB |
| `GET` | `/encoders/info` | Valores válidos nos encoders |
| `GET` | `/docs` | Swagger UI interativo |

### Exemplo cURL — Predição OLA

```bash
curl -X POST https://aria-api-production.up.railway.app/predict/ola \
  -H "Content-Type: application/json" \
  -d '{
    "prio_num": 2,
    "hora_abertura": 9,
    "dia_semana": 0,
    "mes": 4,
    "is_monitoring": 1,
    "has_parent": 0,
    "produto_enc": 0,
    "grupo_enc": 0,
    "categoria_enc": 0,
    "subcategoria_enc": 0,
    "cod_fechamento_enc": 0,
    "descricao": "Servidor de producao fora do ar"
  }'
```

---

## Deploy — Streamlit Community Cloud

1. Push para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Repositório: `afonsoas/aria-aiops` · Branch: `main` · Main file: `streamlit_app.py`
4. **Advanced settings → Secrets:**
```toml
ARIA_API_URL = "https://aria-api-production.up.railway.app"
```
5. Clique em **Deploy**

## Deploy — Railway (API)

O deploy da API é automatizado via GitHub Actions. A cada push na `main`, Railway reconstrói a imagem Docker automaticamente.

Variáveis configuradas no Railway:
- `ARIA_DB_USER`, `ARIA_DB_PASSWORD`, `ARIA_DB_DSN`
- `ARIA_WALLET_PASSWORD`, `ARIA_WALLET_EWALLET_B64`, `ARIA_WALLET_TNSNAMES_B64`

---

## Sprints

| Sprint | Prazo | Status | Conteúdo |
|---|---|---|---|
| Sprint 1 | 27/04/2026 | ✅ Entregue | Ideação, problema, solução, pitch |
| Sprint 2 | 24/05/2026 | ✅ Entregue | Arquitetura, protótipos, planejamento |
| Sprint 3 | 23/08/2026 | ✅ Entregue | API FastAPI, Oracle ADB, Dashboard 5 páginas, modelos ML |
| Sprint 4 | 08/09/2026 | ⏳ Em andamento | Validação, refinamento, pitch final |

---

## Time — Cluster 3 · 2TSCO

| Membro | RM |
|---|---|
| Afonso | RM562671 |
| Bernardo | RM558055 |
| Enrico | RM566064 |
