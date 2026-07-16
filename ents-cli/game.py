import os
import sys
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Markdown, Log
from textual.reactive import reactive
from textual.binding import Binding

INTRO_LORE = """
# 🌳 ENTS: The Awakening
**"The Piscine of Fangorn"**

*“Many are the strange words of the Elves, and many the models of the Silicon.”*

Welcome to your **Trial of Fangorn**. If you have ever attended a 42 Piscine, you will recognize this feeling: there is no hand-holding. There is only the machine, the math, and the Oracle.

You will master the **Four Pillars** of modern AI:
1. 🧮 **JAX** (The theoretical math)
2. 🍎 **MLX** (Apple Silicon parallelization) - *(Skipped on Linux)*
3. 🕸️ **MAX** (The computational graph)
4. 🦀 **Mojo** (Bare-metal memory access)

Your code must be perfect. The Oracle of Fangorn will accept no less.

**Press [ 🌲 Enter Fangorn Forest ] to begin.**
"""

LEVEL_00_LORE = """
# Level 00: The Seed
*“You must understand the soil before you can grow the tree.”*

An "Embedding" is just a lookup table that turns a word into a row of numbers. Your goal in this module is simple: find the row of numbers for Token ID `2`.

**Your Quests:**
- Edit `soil.py` to use JAX arrays.
- Edit `branch.py` to use MLX arrays.
- Edit `roots.py` to build an ONNX Graph and run MAX.
- Edit `sprout.mojo` to access raw memory.
"""

class EntsGame(App):
    """The main TUI for the Ents AI RPG."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        height: 100%;
        layout: horizontal;
    }
    
    #left-panel {
        width: 60%;
        height: 100%;
        padding: 1;
    }
    
    #right-panel {
        width: 40%;
        height: 100%;
        padding: 1;
    }
    
    #lore-box {
        height: 60%;
        overflow-y: auto;
        border: round $secondary;
        background: $panel;
    }
    
    #action-box {
        height: 40%;
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
    
    current_level = reactive(-1)
    
    # Store dynamic lore for levels
    LEVEL_LORE = {
        -1: INTRO_LORE,
        0: LEVEL_00_LORE,
        1: """
# Level 01: The Enting
*“A single seed cannot speak. It must learn the probability of the next word.”*

When an AI tries to guess the next word, it spits out raw, messy scores called "Logits" (e.g., `[-1.0, 5.0]`). A higher score means it likes that word more. To turn these messy scores into clean percentages, we use **Softmax**. Your job is to build that math function.

**Your Quests:**
- Edit `bigram.py` to use JAX Softmax.
- Edit `leaf.py` to use MLX Softmax.
- Edit `bigram_graph.py` to build an ONNX Softmax node.
- Edit `bigram.mojo` to manually calculate Softmax in Mojo.
""",
        2: """
# Level 02: The Lexicon
*“Before you can speak the ancient tongue, you must learn to read its letters.”*

A computer cannot read the letter 'A'. It only understands numbers. A Tokenizer is a secret decoder ring that assigns a unique number to every letter or piece of a word.

**Your Quests:**
- Edit `lexicon.py` to tokenize in JAX.
- Edit `lexicon.py` to tokenize in MLX.
- Edit `lexicon_graph.py` to structure it in MAX.
- Edit `tokenizer.mojo` to run it in Mojo.
"""
    }

    LEVEL_PATHS = {
        0: {
            "jax": "max_env/phases/00_The_Seed/ex00_jax_soil/soil.py",
            "mlx": "max_env/phases/00_The_Seed/ex01_mlx_branch/branch.py",
            "max": "max_env/phases/00_The_Seed/ex02_max_roots/roots.py",
            "mojo": "max_env/phases/00_The_Seed/ex03_mojo_sprout/sprout.mojo",
            "grade_dir": "max_env/phases/00_The_Seed"
        },
        1: {
            "jax": "max_env/phases/01_The_Enting/ex00_jax_bigram/bigram.py",
            "mlx": "max_env/phases/01_The_Enting/ex01_mlx_leaf/leaf.py",
            "max": "max_env/phases/01_The_Enting/ex02_max_bigram/bigram_graph.py",
            "mojo": "max_env/phases/01_The_Enting/ex03_mojo_bigram/bigram.mojo",
            "grade_dir": "max_env/phases/01_The_Enting"
        },
        2: {
            "jax": "max_env/phases/02_The_Lexicon/ex00_jax_lexicon/lexicon.py",
            "mlx": "max_env/phases/02_The_Lexicon/ex01_mlx_lexicon/lexicon.py",
            "max": "max_env/phases/02_The_Lexicon/ex02_max_lexicon/lexicon_graph.py",
            "mojo": "max_env/phases/02_The_Lexicon/ex03_mojo_lexicon/tokenizer.mojo",
            "grade_dir": "max_env/phases/02_The_Lexicon"
        }
    }
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Markdown(self.LEVEL_LORE.get(self.current_level, ""), id="lore-box")
                with Horizontal(id="action-box"):
                    if self.current_level == -1:
                        yield Button("🌲 Enter Fangorn Forest", id="btn_enter", variant="success")
                    else:
                        yield Button("📜 Read Level Lore", id="btn_lore", variant="primary")
                        yield Button("🧮 Edit JAX (Math)", id="btn_jax", variant="default")
                        yield Button("🍎 Edit MLX (Apple)", id="btn_mlx", variant="default")
                        yield Button("🕸️ Edit MAX (Graph)", id="btn_max", variant="default")
                        yield Button("🦀 Edit Mojo (Metal)", id="btn_mojo", variant="default")
                        yield Button("🔮 Summon Oracle (Grade)", id="btn_grade", variant="warning")
                        yield Button("⏭️ Next Level", id="btn_next", variant="success")
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
        
        paths = self.LEVEL_PATHS.get(self.current_level, self.LEVEL_PATHS.get(0))
        
        if event.button.id == "btn_enter":
            self.current_level = 0
            lore_box.update(self.LEVEL_LORE[self.current_level])
            log.write_line("\n[bold green]🌳 You step into the dark forest... Level 00 begins.[/]")
            self.recompose_action_box()
            
        elif event.button.id == "btn_lore":
            lore_box.update(self.LEVEL_LORE.get(self.current_level, "No lore found."))
            log.write_line(f"📜 Reading ancient scrolls for Level {self.current_level:02}...")
            
        elif event.button.id == "btn_jax":
            log.write_line(f"🧮 Opening JAX Editor...")
            self.open_editor(paths["jax"])
            
        elif event.button.id == "btn_mlx":
            log.write_line(f"🍎 Opening MLX Editor...")
            self.open_editor(paths["mlx"])
            
        elif event.button.id == "btn_max":
            log.write_line(f"🕸️ Opening MAX Editor...")
            self.open_editor(paths["max"])
            
        elif event.button.id == "btn_mojo":
            log.write_line(f"🦀 Opening Mojo Editor...")
            self.open_editor(paths["mojo"])
            
        elif event.button.id == "btn_grade":
            log.write_line(f"\n[bold yellow]🔮 Summoning the Oracle for Level {self.current_level:02}...[/]")
            self.run_grader(paths["grade_dir"])
            
        elif event.button.id == "btn_next":
            if self.current_level < 2:
                self.current_level += 1
                log.write_line(f"\n[bold green]🌳 You have advanced to Level {self.current_level:02}![/]")
                lore_box.update(self.LEVEL_LORE[self.current_level])
            else:
                log.write_line(f"\n[bold red]🚫 You have reached the end of the current forest.[/]")

    def recompose_action_box(self) -> None:
        """Dynamically replace buttons when entering the first level."""
        action_box = self.query_one("#action-box")
        action_box.remove_children()
        action_box.mount(Button("📜 Read Level Lore", id="btn_lore", variant="primary"))
        action_box.mount(Button("🧮 Edit JAX (Math)", id="btn_jax", variant="default"))
        action_box.mount(Button("🍎 Edit MLX (Apple)", id="btn_mlx", variant="default"))
        action_box.mount(Button("🕸️ Edit MAX (Graph)", id="btn_max", variant="default"))
        action_box.mount(Button("🦀 Edit Mojo (Metal)", id="btn_mojo", variant="default"))
        action_box.mount(Button("🔮 Summon Oracle (Grade)", id="btn_grade", variant="warning"))
        action_box.mount(Button("⏭️ Next Level", id="btn_next", variant="success"))

    def open_editor(self, rel_path: str) -> None:
        log = self.query_one("#oracle-log", Log)
        editor = os.environ.get('EDITOR', 'nano')
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        safe_filepath = os.path.abspath(os.path.join(base_dir, rel_path))
        
        # Security: Prevent directory traversal
        if not safe_filepath.startswith(base_dir):
            log.write_line("❌ Oracle says: Access denied. You shall not pass.")
            return
            
        if not os.path.exists(os.path.dirname(safe_filepath)):
            log.write_line(f"❌ Oracle says: This region of the forest has not grown yet.")
            return
            
        with self.suspend():
            subprocess.run([editor, safe_filepath])

    def run_grader(self, grade_dir: str) -> None:
        log = self.query_one("#oracle-log", Log)
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cwd = os.path.join(base_dir, grade_dir)
        script_path = os.path.join(cwd, "grademe.sh")
        
        if not os.path.exists(script_path):
            log.write_line("❌ Oracle says: Grading script not found!")
            return
            
        try:
            result = subprocess.run(["./grademe.sh"], cwd=cwd, capture_output=True, text=True)
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
