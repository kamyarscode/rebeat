import os
import sys

_backend = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, _backend)
sys.path.insert(0, os.path.join(_backend, "src"))

from app import app  # noqa: E402,F401
