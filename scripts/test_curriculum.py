#!/usr/bin/env python3
"""Assert curriculum.json matches the files on disk and CLI/web import it."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "max_env" / "phases"))
from curriculum import PHASES, missing_paths, pillar_path  # noqa: E402


def main() -> int:
    missing = missing_paths()
    if missing:
        print("MISSING")
        for item in missing:
            print(" ", item)
        return 1
    for phase, spec in PHASES.items():
        for pillar, rel in spec["pillars"].items():
            path = pillar_path(phase, pillar)
            assert path.is_file(), path
            assert path.as_posix().endswith(rel), (path, rel)
    print("curriculum map ok:", ", ".join(PHASES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
