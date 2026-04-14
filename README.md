# ARIA — Automated Response & Incident Analysis

> *"Resposta certa, no tempo certo, pelo caminho certo."*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit)
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

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12 |
| Data | Pandas, NumPy, OpenPyXL |
| ML | Scikit-learn, XGBoost, imbalanced-learn |
| NLP | TF-IDF (sklearn) |
| Dashboard | Streamlit + Plotly |
| Banco | Oracle Autonomous DB 19c (OCI Always Free) |
| Deploy | OCI Container Instance / Streamlit Community Cloud |
| Versionamento | GitHub |

---

## Estrutura do Projeto

```
aria-aiops/
  data/                   — dataset (não versionado — ver .gitignore)
  eda/
    aria_eda.py           — análise exploratória
    output/               — gráficos e relatório gerados
  model/
    aria_model.py         — treinamento dos modelos ML
    model_ola.pkl         — modelo de predição de violação OLA
    model_priority.pkl    — modelo de classificação de prioridade
  dashboard/
    app.py                — aplicação Streamlit principal
    pages/
      1_kpi_overview.py
      2_incident_list.py
      3_ola_predictor.py
      4_patterns.py
    utils/
      data_loader.py
      model_loader.py
    assets/
      logo_aria.png
  docs/                   — apresentações e documentação
```

---

## Instalação

```bash
git clone https://github.com/afonsoas/aria-aiops.git
cd aria-aiops
py -3.12 -m pip install -r requirements.txt
```

Copie o dataset para `data/`:
```
data/LW-DATASET.xlsx
```

## Rodando

**EDA:**
```bash
py -3.12 eda/aria_eda.py
```

**Treinamento dos modelos:**
```bash
py -3.12 model/aria_model.py
```

**Dashboard:**
```bash
py -3.12 -m streamlit run dashboard/app.py
```

---

## Sprints

| Sprint | Entrega | Status | Conteúdo |
|--------|---------|--------|----------|
| Sprint 1 | 27/04/2026 | ✅ Entregue | Ideação, problema, solução, pitch |
| Sprint 2 | 24/05/2026 | 🔄 Em andamento | Arquitetura, protótipos, planejamento |
| Sprint 3 | 23/08/2026 | ⏳ | MVP funcional, modelos treinados |
| Sprint 4 | 08/09/2026 | ⏳ | Validação, refinamento, pitch final |

---

## Time — Cluster 3 · 2TSCO

| Membro | RM |
|--------|----|
| Afonso | RM562671 |
| Bernardo | RM558055 |
| Enrico | RM566064 |
