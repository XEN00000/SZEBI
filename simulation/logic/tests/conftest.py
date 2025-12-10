import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # points to .../szebi
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))