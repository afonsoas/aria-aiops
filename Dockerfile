FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema (oracledb thin mode não precisa de Oracle Client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY api/      api/
COPY model/    model/
COPY data/     data/

# Expõe porta da API
EXPOSE 8000

# Variáveis de ambiente com defaults seguros
ENV ARIA_DB_USER=ADMIN \
    ARIA_DB_PASSWORD="" \
    ARIA_DB_DSN="" \
    ARIA_WALLET_DIR="" \
    ARIA_WALLET_PASSWORD=""

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
