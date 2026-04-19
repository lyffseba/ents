import os
import sys
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Markdown, Log
from textual.reactive import reactive
from textual.binding import Binding

LORE_TEXT = """
# 🌳 ENTS: The Awakening
**A Terminal RPG for AI Engineers**

You stand at the edge of Fangorn Forest. The ancient language models are slumbering.
Your quest is to wake them up, one mathematical layer at a time.

You must master the **Four Pillars**:
1. 🧮 **JAX** (The theoretical math)
2. 🍎 **MLX** (Apple Silicon parallelization) - *Coming soon*
3. 🕸️ **MAX** (The computational graph)
4. 🦀 **Mojo** (Bare-metal memory access)

---
### Currently Unlocked Levels:
*   **Level 00:** The Seed (Embeddings)
*   **Level 01:** The Enting (Bigrams & Softmax)
"""

LEVEL_00_LORE = """
# Level 00: The Seed
*“You must understand the soil before you can grow the tree.”*

An "Embedding" is just a lookup table that turns a word into a row of numbers. Your goal in this module is simple: find the row of numbers for Token ID `2`.

**Your Quests:**
- Edit `soil.py` to use JAX arrays.
- Edit `roots.py` to build an ONNX Graph and run MAX.
- Edit `sprout.mojo` to access raw memory.
"""

class EntsGame(App):
    """The main TUI for the Ents AI RPG."""
    
    CSS = """
    Screen {
        background: $surface-dark;
    }
    
    #main-container {
        height: 100%;
        layout: horizontal;
    }
    
    #left-panel {
        width: 60%;
        height: 100%;
        border-right: solid $primary;
        padding: 1;
    }
    
    #right-panel {
        width: 40%;
        height: 100%;
        padding: 1;
    }
    
    #lore-box {
        height: 70%;
        overflow-y: auto;
        border: round $secondary;
        background: $panel;
    }
    
    #action-box {
        height: 30%;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        padding: 1;
    }
    
    Button {
        width: 100%;
        margin-bottom: 1;
    }
    
    #oracle-log {
        height: 100%;
        border: double $warning;
        background: black;
        color: lime;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit Game"),
        Binding("l", "toggle_lore", "Toggle Lore"),
    ]
    
    current_level = reactive(0)
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Markdown(LORE_TEXT, id="lore-box")
                with Horizontal(id="action-box"):
                    yield Button("📜 Read Level Lore", id="btn_lore", variant="primary")
                    yield Button("🧮 Edit JAX (Math)", id="btn_jax", variant="default")
                    yield Button("🕸️ Edit MAX (Graph)", id="btn_max", variant="default")
                    yield Button("🦀 Edit Mojo (Metal)", id="btn_mojo", variant="default")
                    yield Button("🔮 Summon Oracle (Grade)", id="btn_grade", variant="warning")
            with Vertical(id="right-panel"):
                yield Log(id="oracle-log", highlight=True)
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#oracle-log", Log)
        log.write_line("🔮 The Oracle of Fangorn slumbers...")
        log.write_line("Type or click to begin your journey.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one("#oracle-log", Log)
        lore_box = self.query_one("#lore-box", Markdown)
        
        if event.button.id == "btn_lore":
            lore_box.update(LEVEL_00_LORE)
            log.write_line("📜 Reading ancient scrolls...")
            
        elif event.button.id == "btn_jax":
            log.write_line("🧮 Opening JAX Editor (soil.py)...")
            self.open_editor("phases/C00_The_Seed/ex00_jax_soil/soil.py")
            
        elif event.button.id == "btn_max":
            log.write_line("🕸️ Opening MAX Editor (roots.py)...")
            self.open_editor("phases/C00_The_Seed/ex01_max_roots/roots.py")
            
        elif event.button.id == "btn_mojo":
            log.write_line("🦀 Opening Mojo Editor (sprout.mojo)...")
            self.open_editor("phases/C00_The_Seed/ex02_mojo_sprout/sprout.mojo")
            
        elif event.button.id == "btn_grade":
            log.write_line("\n[bold yellow]🔮 Summoning the Oracle...[/]")
            self.run_grader()

    def open_editor(self, filepath: str) -> None:
        editor = os.environ.get('EDITOR', 'nano')
        # We suspend the TUI temporarily to open the terminal editor
        with self.suspend():
            subprocess.run([editor, filepath])

    def run_grader(self) -> None:
        log = self.query_one("#oracle-log", Log)
        try:
            # Run the bash script synchronously and capture output
            result = subprocess.run(["./grademe.sh"], cwd="phases/C00_The_Seed", capture_output=True, text=True)
            for line in result.stdout.splitlines():
                log.write_line(line)
                
            if "✅ PASS" in result.stdout and "❌ FAIL" not in result.stdout:
                log.write_line("\n🌟 LEVEL COMPLETE! 🌟")
            else:
                log.write_line("\n⚠️ The Oracle rejects your offering.")
        except Exception as e:
            log.write_line(f"❌ Error communicating with the Oracle: {e}")

if __name__ == "__main__":
    app = EntsGame()
    app.run()
