# 🌳 ents-pi-mod Architecture

The `ents-pi-mod` is an extension for the [pi coding agent](https://github.com/earendil-works/pi-coding-agent), designed to seamlessly integrate the Ents Awakening environment (JAX, MLX, MAX, and Mojo) into Pi's workflow.

## Overview

`ents-pi-mod` acts as a magical bridge between Pi and the Trial of Fangorn. It will be loaded as a project-local extension (`.pi/extensions/ents-pi-mod.ts`) providing the following capabilities:

1. **Custom Tools (`pi.registerTool`)**
2. **Commands (`pi.registerCommand`)**
3. **Event Interception (`pi.on(...)`)**
4. **Custom TUI Components (`ctx.ui.custom`)**

## Component Breakdown

### 1. The Oracle Grader Command (`/ents-grade`)
Instead of manually navigating to the phase folder and running `grademe.sh`, the user or Pi can invoke the `/ents-grade <level>` command.
- **Implementation**: We will register a command `pi.registerCommand('ents-grade', ...)` that executes the corresponding `grademe.sh` script.
- **TUI Integration**: If a human types it, it could show a custom UI window (`ctx.ui.custom()`) with the grading output colored appropriately (green for ✅ PASS, red for ❌ FAIL).

### 2. Environment Tools
Pi needs tools to effectively navigate the four pillars:
- `ents_run_mojo`: A tool to compile and run `.mojo` files through the pixi environment.
- `ents_build_max_graph`: A tool to trigger ONNX graph generation for MAX models.
- `ents_run_mlx`: A tool specifically for Apple Silicon execution with proper environment variables.

### 3. File Protection (Event Interception)
The Oracle demands that students write the code. We can add an educational mode where Pi is restricted from modifying certain files or simply providing the final answers.
- **Hook**: `pi.on('preToolCall')`
- **Logic**: If the tool is `edit` or `write` and the file is a core `grademe.sh` script or read-only `SUBJECT.md`, the extension will throw a `CallAbortedError("The Oracle forbids tampering with the trial parameters.")`.

### 4. Custom Fangorn Theme (Optional)
The extension can adjust Pi's appearance to fit the Ents theme.
- **Hook**: Provide custom rendering via `renderToolCall` or by adjusting console colors to match the dark forest greens, browns, and magical glowing text (lime).

## Setup & Deployment

1. **Directory**: Place the extension at `ents/.pi/extensions/ents_mod.ts`.
2. **Dependencies**: None strictly required beyond Pi's `ExtensionAPI`, as it will execute shell commands to leverage the existing `pixi` environments.
3. **State Management**: Use `pi.appendEntry()` to record when a user passes a level, keeping a persistent ledger of their progress.

## Future Enhancements
- **Memory Crystal Sync**: Automatically update `AGENT_STATE.md` using `pi.on('postToolCall')` or periodic triggers when milestones are met.
- **Interactive NPC**: Implement Treebeard as a custom prompt or an interactive TUI component (`ctx.ui.custom()`) offering hints.
