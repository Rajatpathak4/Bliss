"""
Vercel root entrypoint (Root Directory = backend).
Loads FastAPI `app` from src/main.py without circular imports.
"""
import importlib.util
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_ROOT, "src")
_SRC_MAIN = os.path.join(_SRC, "main.py")

if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

_spec = importlib.util.spec_from_file_location("bliss_src_main", _SRC_MAIN)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load FastAPI app from {_SRC_MAIN}")

_mod = importlib.util.module_from_spec(_spec)
sys.modules["bliss_src_main"] = _mod
_spec.loader.exec_module(_mod)

app = _mod.app
