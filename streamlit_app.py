# Entry point para Streamlit Community Cloud.
# No painel do Streamlit Cloud, defina "Main file path" como: streamlit_app.py
#
# Estratégia: muda o diretório de trabalho para dashboard/ antes de executar,
# para que o Streamlit descubra pages/ corretamente.

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

# Muda para dashboard/ — Streamlit descobre pages/ a partir daqui
os.chdir(ROOT / "dashboard")

# Executa app.py como __main__
exec(open(ROOT / "dashboard" / "app.py").read())
