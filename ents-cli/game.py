"""Textual RPG over the Trial of Fangorn. Paths come from curriculum.json."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Log, Markdown

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "max_env" / "phases"))
from curriculum import grade_script, pillar_path  # noqa: E402

INTRO_LORE = """
# 🌳 ENTS: The Awakening
**"The Piscine of Fangorn"**

Welcome to your **Trial of Fangorn**. There is no hand-holding.
There is only the machine, the math, and the Oracle.

**Four Pillars:** JAX → MLX → MAX → Mojo.

Press **Enter Fangorn Forest** to begin.
"""

LEVEL_LORE = {
    -1: INTRO_LORE,
    0: """
# Level 00: The Seed
Find the embedding row for token ID `2`.
""",
    1: """
# Level 01: The Enting
Softmax the `hello` row of the 3×3 bigram logit table.
""",
    2: """
# Level 02: The Lexicon
Build the Tiny Shakespeare character vocab and encode `Fangorn`.
""",
}

PHASE_INDEX = {0: "00", 1: "01", 2: "02"}


class EntsGame(App):
    CSS = """
    Screen { background: $surface; }
    #main-container { height: 100%; layout: horizontal; }
    #left-panel { width: 60%; height: 100%; padding: 1; }
    #right-panel { width: 40%; height: 100%; padding: 1; }
    #lore-box { height: 60%; overflow-y: auto; border: round $secondary; background: $panel; }
    #action-box { height: 40%; layout: grid; grid-size: 2; grid-columns: 1fr 1fr; padding: 1; }
    Button { width: 100%; margin-bottom: 1; }
    #oracle-log { height: 100%; border: double $warning; background: black; color: lime; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit Game"),
        Binding("l", "read_lore", "Lore"),
    ]

    current_level = reactive(-1)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Markdown(LEVEL_LORE[-1], id="lore-box")
                with Horizontal(id="action-box"):
                    yield Button("🌲 Enter Fangorn Forest", id="btn_enter", variant="success")
            with Vertical(id="right-panel"):
                yield Log(id="oracle-log", highlight=True)
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#oracle-log", Log)
        log.write_line("🔮 The Oracle of Fangorn slumbers...")
        log.write_line("Click Enter Fangorn Forest to begin.")

    def watch_current_level(self, old: int, level: int) -> None:
        try:
            lore_box = self.query_one("#lore-box", Markdown)
            action_box = self.query_one("#action-box")
        except Exception:
            return
        lore_box.update(LEVEL_LORE.get(level, ""))
        if old == level:
            return
        self._mount_actions(action_box, level)

    def _mount_actions(self, action_box, level: int) -> None:
        action_box.remove_children()
        if level < 0:
            action_box.mount(Button("🌲 Enter Fangorn Forest", id="btn_enter", variant="success"))
            return
        action_box.mount(Button("📜 Read Level Lore", id="btn_lore", variant="primary"))
        action_box.mount(Button("🧮 Edit JAX (Math)", id="btn_jax", variant="default"))
        action_box.mount(Button("🍎 Edit MLX (Apple)", id="btn_mlx", variant="default"))
        action_box.mount(Button("🕸️ Edit MAX (Graph)", id="btn_max", variant="default"))
        action_box.mount(Button("🦀 Edit Mojo (Metal)", id="btn_mojo", variant="default"))
        action_box.mount(Button("🔮 Summon Oracle (Grade)", id="btn_grade", variant="warning"))
        action_box.mount(Button("⏭️ Next Level", id="btn_next", variant="success"))

    def action_read_lore(self) -> None:
        self.query_one("#lore-box", Markdown).update(LEVEL_LORE.get(self.current_level, ""))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one("#oracle-log", Log)
        phase = PHASE_INDEX.get(self.current_level)

        if event.button.id == "btn_enter":
            self.current_level = 0
            log.write_line("\n🌳 You step into the dark forest... Level 00 begins.")
            return

        if event.button.id == "btn_lore":
            self.action_read_lore()
            log.write_line(f"📜 Reading scrolls for Level {self.current_level:02}...")
            return

        if event.button.id == "btn_next":
            if self.current_level < 2:
                self.current_level += 1
                log.write_line(f"\n🌳 Advanced to Level {self.current_level:02}.")
            else:
                log.write_line("\n🚫 End of the current forest (C03 is not written).")
            return

        if phase is None:
            return

        pillar_ids = {"btn_jax": "jax", "btn_mlx": "mlx", "btn_max": "max", "btn_mojo": "mojo"}
        if event.button.id in pillar_ids:
            self.open_editor(pillar_path(phase, pillar_ids[event.button.id]))
            return

        if event.button.id == "btn_grade":
            log.write_line(f"\n🔮 Summoning the Oracle for Level {self.current_level:02}...")
            self.run_grader(grade_script(phase))

    def open_editor(self, path: Path) -> None:
        log = self.query_one("#oracle-log", Log)
        resolved = path.resolve()
        if not str(resolved).startswith(str(REPO) + os.sep):
            log.write_line("❌ Access denied.")
            return
        if not resolved.is_file():
            log.write_line("❌ This region of the forest has not grown yet.")
            return
        editor = os.environ.get("EDITOR", "nano")
        log.write_line(f"Opening {resolved.relative_to(REPO)} ...")
        with self.suspend():
            subprocess.run([editor, str(resolved)])

    def run_grader(self, script: Path) -> None:
        log = self.query_one("#oracle-log", Log)
        if not script.is_file():
            log.write_line("❌ Grading script not found.")
            return
        try:
            result = subprocess.run(
                [f"./{script.name}"],
                cwd=str(script.parent),
                capture_output=True,
                text=True,
            )
        except Exception as exc:
            log.write_line(f"❌ Oracle error: {exc}")
            return
        for line in (result.stdout or "").splitlines():
            log.write_line(line)
        if "✅ PASS" in (result.stdout or "") and "❌ FAIL" not in (result.stdout or ""):
            log.write_line("\n🌟 LEVEL COMPLETE!")
        else:
            log.write_line("\n⚠️ The Oracle rejects your offering.")


if __name__ == "__main__":
    missing = []
    from curriculum import missing_paths

    missing = missing_paths()
    if missing:
        print("Curriculum map is stale. Missing:")
        for item in missing:
            print(" ", item)
        raise SystemExit(1)
    EntsGame().run()
