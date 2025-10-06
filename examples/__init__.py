import sys
from pathlib import Path

# Add <repo_root>/src to sys.path when running examples directly
root = Path(__file__).resolve().parents[1]
src_path = root / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
