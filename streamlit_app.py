# Entry point para Streamlit Community Cloud.
# Main file path recomendado: dashboard/app.py
#
# Este arquivo existe apenas como fallback. Se o Streamlit Cloud estiver
# configurado com streamlit_app.py como main file, redireciona para dashboard/app.py
# adicionando o root ao sys.path e executando com __file__ correto.

import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

# Executa app.py definindo __file__ corretamente para que Path(__file__) funcione
_app_path = ROOT / "dashboard" / "app.py"
exec(
    compile(open(_app_path).read(), str(_app_path), "exec"),
    {"__file__": str(_app_path), "__name__": "__main__", "__spec__": None}
)
