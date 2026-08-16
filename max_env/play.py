"""Compatibility launcher. The TUI lives in ents-cli/game.py."""

from pathlib import Path
import runpy
import sys

GAME = Path(__file__).resolve().parents[1] / "ents-cli" / "game.py"
if not GAME.exists():
    sys.exit("ents-cli/game.py is missing")
runpy.run_path(str(GAME), run_name="__main__")
