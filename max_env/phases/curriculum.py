"""Machine-readable Trial of Fangorn map. CLI, web Oracle, and checks import this."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_DATA = json.loads((ROOT / "curriculum.json").read_text())
PHASES: dict[str, dict] = _DATA["phases"]
PILLARS = ("jax", "mlx", "max", "mojo")


def phase_ids() -> list[str]:
    return list(PHASES)


def phase_dir(phase: str) -> Path:
    spec = PHASES[phase]
    return ROOT / spec["dir"]


def pillar_rel(phase: str, pillar: str) -> str:
    return PHASES[phase]["pillars"][pillar]


def pillar_path(phase: str, pillar: str) -> Path:
    return phase_dir(phase) / pillar_rel(phase, pillar)


def grade_script(phase: str) -> Path:
    return phase_dir(phase) / "grademe.sh"


def missing_paths() -> list[str]:
    missing: list[str] = []
    for phase in phase_ids():
        if not grade_script(phase).is_file():
            missing.append(str(grade_script(phase)))
        for pillar in PILLARS:
            path = pillar_path(phase, pillar)
            if not path.is_file():
                missing.append(str(path))
    return missing
