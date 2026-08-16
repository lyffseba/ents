#!/usr/bin/env python3
"""Headless check: Enter Fangorn remounts the action buttons."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ents-cli"))
from game import EntsGame  # noqa: E402


def main() -> int:
    app = EntsGame()
    async def run():
        async with app.run_test() as pilot:
            ids = [w.id for w in app.query("Button")]
            if ids != ["btn_enter"]:
                print("intro buttons wrong:", ids)
                return 1
            await pilot.click("#btn_enter")
            await pilot.pause()
            ids = [w.id for w in app.query("Button")]
            need = {"btn_lore", "btn_jax", "btn_mlx", "btn_max", "btn_mojo", "btn_grade", "btn_next"}
            if not need.issubset(set(ids)):
                print("level 00 buttons missing:", ids)
                return 1
            print("cli remount ok:", ids)
            return 0

    return app.run(run()) if False else __import__("asyncio").run(run())


if __name__ == "__main__":
    raise SystemExit(main())
