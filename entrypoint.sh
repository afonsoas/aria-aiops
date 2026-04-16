#!/bin/sh
# Entrypoint: reconstrói wallet Oracle ADB a partir de env vars (base64) e inicia API

set -e

WALLET_DIR="${ARIA_WALLET_DIR:-/app/wallet}"
mkdir -p "$WALLET_DIR"

# Decodifica ewallet.pem de env var base64 (se presente)
if [ -n "$ARIA_WALLET_EWALLET_B64" ]; then
    echo "$ARIA_WALLET_EWALLET_B64" | base64 -d > "$WALLET_DIR/ewallet.pem"
    echo "[entrypoint] ewallet.pem restaurado do env var"
fi

# Decodifica tnsnames.ora de env var base64 (se presente)
if [ -n "$ARIA_WALLET_TNSNAMES_B64" ]; then
    echo "$ARIA_WALLET_TNSNAMES_B64" | base64 -d > "$WALLET_DIR/tnsnames.ora"
    echo "[entrypoint] tnsnames.ora restaurado do env var"
fi

# sqlnet.ora padrão (thin mode não precisa de WALLET_LOCATION)
if [ ! -f "$WALLET_DIR/sqlnet.ora" ]; then
    echo "SSL_SERVER_DN_MATCH=yes" > "$WALLET_DIR/sqlnet.ora"
fi

echo "[entrypoint] Iniciando API ARIA..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
