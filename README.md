# ARIA — Automated Response & Incident Analysis

> *"Resposta certa, no tempo certo, pelo caminho certo."*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)
![Oracle](https://img.shields.io/badge/DB-Oracle%20ADB-F80000?logo=oracle)
![FIAP](https://img.shields.io/badge/FIAP-Enterprise%20Challenge%202026-ED1C24)

---

## O Problema

A Locaweb registra **122.543 incidentes/ano**, dos quais:

| Indicador | Valor |
|-----------|-------|
| Violações de OLA | **248** (42 Alta + 206 Média) |
| Incidentes sem intervenção humana | **65%** |
| Abertos por monitoramento automático | **85%** |
| Concentração em um único time | **75% no Team14** |

## A Solução

ARIA é um sistema AIOps que prediz violações de OLA antes que aconteçam, classifica automaticamente a prioridade de incidentes e centraliza a gestão operacional em um dashboard analítico.

```
[Fonte de Dados]         [Processamento]          [Saída]
LW-DATASET.xlsx  ──►  Python + Pandas         ──►  Streamlit Dashboard
Monitoramento    ──►  XGBoost (OLA)           ──►  Alertas em tempo real
em tempo real    ──►  RandomForest (Prio)     ──►  API REST (FastAPI)
                 ──►  TF-IDF (Texto)          ──►  Oracle Autonomous DB
                 ──►  SMOTE (balanceamento)
```

### Métricas dos Modelos

| Modelo | Algoritmo | Métrica Principal |
|--------|-----------|-------------------|
| Modelo A — Predição OLA | XGBoost + SMOTE | ROC-AUC **0.84** / Recall **60%** |
| Modelo B — Classificação Prioridade | Random Forest | F1-macro **0.90** / Accuracy **91%** |

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12 |
| Data | Pandas, NumPy, OpenPyXL |
| ML | Scikit-learn, XGBoost, imbalanced-learn |
| NLP | TF-IDF (sklearn) |
| Dashboard | Streamlit + Plotly |
| API | FastAPI + Uvicorn |
| Banco | Oracle Autonomous DB 19c (OCI Always Free) |
| Deploy | OCI Container Instance / Streamlit Community Cloud / Docker |
| Versionamento | GitHub |

---

## Estrutura do Projeto

```
aria-aiops/
  data/
    LW-DATASET.xlsx         — dataset Locaweb (122.543 registros)
  eda/
    aria_eda.py             — análise exploratória
    output/                 — gráficos e relatório
  model/
    aria_model.py           — script de treinamento
    model_ola.pkl           — modelo XGBoost (OLA)
    model_priority.pkl      — modelo Random Forest (prioridade)
    encoders.pkl            — LabelEncoders
    evaluation_report.txt   — métricas detalhadas
  api/
    main.py                 — FastAPI app (5 endpoints)
    schemas.py              — Pydantic schemas
    db.py                   — Oracle ADB (thin mode)
  dashboard/
    app.py                  — Home / navegação
    pages/
      1_kpi_overview.py     — KPIs + gráficos temporais
      2_incident_list.py    — tabela filtrável + badges
      3_ola_predictor.py    — preditor com gauge + SHAP simplificado
      4_patterns.py         — treemap + playbooks automáticos
      5_api_predictor.py    — integração com API REST + histórico ADB
    utils/
      data_loader.py        — carrega e normaliza o dataset
      model_loader.py       — carrega modelos pkl
      theme.py              — CSS glassmorphism + helpers Plotly
  streamlit_app.py          — entry point para Streamlit Cloud
  Dockerfile                — imagem Docker para a API
  docker-compose.yml        — orquestração local (API + Dashboard)
  .env.example              — template de variáveis de ambiente
  .streamlit/
    config.toml             — tema escuro + configurações
    secrets.toml.example    — template de secrets para Streamlit Cloud
  requirements.txt
```

---

## Instalação Local

```bash
git clone https://github.com/afonsoas/aria-aiops.git
cd aria-aiops
pip install -r requirements.txt
```

### Rodar EDA

```bash
python eda/aria_eda.py
```

### Treinar Modelos

```bash
python model/aria_model.py
```

### Rodar a API (FastAPI)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# Swagger UI: http://localhost:8000/docs
```

### Rodar o Dashboard (Streamlit)

```bash
streamlit run dashboard/app.py
# Acesso: http://localhost:8501
```

### Rodar com Docker (API + Dashboard)

```bash
cp .env.example .env          # preencha com suas credenciais
docker-compose up --build
# API:       http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

---

## Configuração do Oracle ADB

1. Crie um Autonomous Database no OCI (Always Free — 20GB grátis)
2. Baixe a Wallet em: **OCI Console → Autonomous Database → Database Connection → Download Wallet**
3. Extraia para a pasta `wallet/`
4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite .env com suas credenciais
```

| Variável | Descrição |
|----------|-----------|
| `ARIA_DB_USER` | Usuário do banco (padrão: `ADMIN`) |
| `ARIA_DB_PASSWORD` | Senha do usuário |
| `ARIA_DB_DSN` | DSN no formato `host:port/service_name` |
| `ARIA_WALLET_DIR` | Caminho para a pasta da wallet |

A API cria as tabelas automaticamente na primeira execução:
- `ARIA_OLA_PREDICTIONS` — histórico de predições OLA
- `ARIA_PRIORITY_PREDICTIONS` — histórico de classificações de prioridade

---

## Deploy — Streamlit Community Cloud (Dashboard)

1. Fork ou push para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Selecione o repositório e defina **Main file**: `streamlit_app.py`
4. Em **Settings → Secrets**, cole:

```toml
ARIA_API_URL = "https://URL-DA-SUA-API"
```

5. Clique em **Deploy**

---

## Deploy — OCI Container Instance (API)

```bash
# Build da imagem
docker build -t aria-api .

# Tag para Oracle Container Registry (OCIR)
docker tag aria-api <region>.ocir.io/<namespace>/aria-api:latest

# Push para OCIR
docker push <region>.ocir.io/<namespace>/aria-api:latest
```

No OCI Console:
1. **Containers → Container Instances → Create**
2. Selecione a imagem do OCIR
3. Defina as variáveis de ambiente (`ARIA_DB_*`)
4. Porta: **8000**
5. Shape: **CI.Standard.A1.Flex** (Always Free — 1 OCPU, 6GB RAM)

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Status da API, modelos e DB |
| `POST` | `/predict/ola` | Probabilidade de violação OLA |
| `POST` | `/predict/priority` | Classificação de prioridade (2–4) |
| `GET` | `/predictions/ola?limit=N` | Histórico do Oracle ADB |
| `GET` | `/encoders/info` | Valores válidos nos encoders |
| `GET` | `/docs` | Swagger UI interativo |

### Exemplo cURL

```bash
curl -X POST http://localhost:8000/predict/ola \
  -H "Content-Type: application/json" \
  -d '{
    "prio_num": 3,
    "hora_abertura": 14,
    "dia_semana": 1,
    "mes": 4,
    "is_monitoring": 1,
    "has_parent": 0,
    "produto_enc": 0,
    "grupo_enc": 0,
    "categoria_enc": 0,
    "subcategoria_enc": 0,
    "cod_fechamento_enc": 0,
    "descricao": "Problem: Check Application Monitoring",
    "grupo": "Team14"
  }'
```

---

## Sprints

| Sprint | Entrega | Status | Conteúdo |
|--------|---------|--------|----------|
| Sprint 1 | 27/04/2026 | ✅ Entregue | Ideação, problema, solução, pitch |
| Sprint 2 | 24/05/2026 | ✅ Entregue | Arquitetura, protótipos, planejamento |
| Sprint 3 | 23/08/2026 | ✅ Entregue | API FastAPI, Oracle ADB, Dashboard 5 páginas, modelos treinados |
| Sprint 4 | 08/09/2026 | ⏳ Em andamento | Validação, refinamento, pitch final |

---

## Time — Cluster 3 · 2TSCO

| Membro | RM |
|--------|----|
| Afonso | RM562671 |
| Bernardo | RM558055 |
| Enrico | RM566064 |
