import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
_p = _ROOT / "dashboard" / "pages" / "4_patterns.py"
exec(compile(open(_p).read(), str(_p), "exec"), {"__file__": str(_p), "__name__": "__main__", "__spec__": None})
