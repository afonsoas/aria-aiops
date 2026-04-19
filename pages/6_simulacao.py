import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
exec(compile(open(Path(__file__).resolve().parent.parent / "dashboard" / "pages" / "6_simulacao.py").read(),
             str(Path(__file__).resolve().parent.parent / "dashboard" / "pages" / "6_simulacao.py"), "exec"))
