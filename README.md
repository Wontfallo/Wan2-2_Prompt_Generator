# Wan 2.2 Prompt Crafter

A desktop app for crafting high‑quality Wan 2.2 video prompts with a clean CustomTkinter UI, controllable creativity modes, and a persistent prompt history. Core UI and logic live in [app.py](app.py:1) and [backend.py](backend.py:1). The complete one‑shot spec is documented in [UI_DESIGN_BLUEPRINT.md](UI_DESIGN_BLUEPRINT.md:1).

[!alt](wan2-2_Prompt_Gen.png)

## New One File .HTML option with bonus features of QWEN and FLUX Prompts

[!alt](wan2.2_onefile_PRompter.png)

## Quick Start (Windows EXE)

- Built EXE path after packaging: dist\Wan2PromptCrafter.exe
- Double‑click the EXE to launch the app.
- For best results, have either LM Studio or Ollama running locally before generating prompts.

Notes:
- History is automatically persisted to %APPDATA%\Wan2PromptGenerator\wan2_prompt_history.json (see [get_history_file_path()](backend.get_history_file_path():15)).

## Run From Source

Prereqs:
- Python 3.10+
- Windows recommended (packaging config targets Windows)

Install runtime dependencies:
- pip install customtkinter requests clipboard

Run:
- python [app.py](app.py:769)

## Build a Portable EXE (PyInstaller)

The build is already proven with icon + splash:
- python -m pip install --upgrade pyinstaller
- pyinstaller --noconfirm --clean --onefile --windowed app.py --name "Wan2PromptCrafter" --icon "C:\Users\WontML\Pictures\1a\icon.png" --splash "C:\Users\WontML\Pictures\1a\icon.png" --exclude-module PyQt5 --exclude-module PyQt6

Result:
- dist\Wan2PromptCrafter.exe

Optional size trim (when Qt or qtpy sneaks in via transitive deps):
- Add: --exclude-module qtpy --exclude-module PySide2 --exclude-module PySide6

## UI Overview

The application layout and behavior are fully specified in [UI_DESIGN_BLUEPRINT.md](UI_DESIGN_BLUEPRINT.md:1). Implementation entry points:
- Window setup and layout: [Wan2PromptApp.__init__()](app.Wan2PromptApp.__init__():9), [Wan2PromptApp.create_widgets()](app.Wan2PromptApp.create_widgets():46)
- History side panel (accordion): [Wan2PromptApp.create_history_panel()](app.Wan2PromptApp.create_history_panel():132), [Wan2PromptApp.toggle_history_panel()](app.Wan2PromptApp.toggle_history_panel():402)

Config frame (3 rows), exact final layout:
1) Services & Endpoint row (compact): [app.py](app.py:54)–[app.py](app.py:62)
2) Model + Pull on one dense row with tight spacing: [app.py](app.py:64)–[app.py](app.py:77)
3) Creativity row (two options, no truncation): [app.py](app.py:79)–[app.py](app.py:83)

Input / Output:
- Input (blue) and Output split vertical space via grid weights: [app.py](app.py:85)–[app.py](app.py:110)
- “Inspire Me” lives in the Input header (top‑right): [app.py](app.py:97)–[app.py](app.py:99)
- “Generate Wan 2.2 Prompt” is the primary CTA between Input and Output: [app.py](app.py:100)–[app.py](app.py:103)
- Output supports “Copy to Clipboard”: [Wan2PromptApp.copy_output()](app.Wan2PromptApp.copy_output():258)

Negative Prompt (locked by default):
- Frame + “Unlock to Edit” checkbox: [app.py](app.py:116)–[app.py](app.py:136)
- Toggle logic: [Wan2PromptApp.toggle_neg_prompt_edit()](app.Wan2PromptApp.toggle_neg_prompt_edit():254)

## LLM Backends

- Creativity‑aware system prompt assembly: [get_system_prompt()](backend.get_system_prompt():177)
- Generate Prompt:
  - LM Studio (OpenAI chat‑compat): [generate_prompt()](backend.generate_prompt():272)
  - Ollama (/api/chat, non‑stream): [generate_prompt()](backend.generate_prompt():287)
- Inspire Me:
  - Request 3 short scene ideas: [get_inspiration_prompt()](backend.get_inspiration_prompt():212), [get_inspiration()](backend.get_inspiration():328)

Networking and threading:
- All long jobs are threaded and UI updates are marshalled using .after(0, ...):
  - Refresh models: [Wan2PromptApp.refresh_models()](app.Wan2PromptApp.refresh_models():268)
  - Pull model: [Wan2PromptApp.pull_model()](app.Wan2PromptApp.pull_model():292)
  - Generate: [Wan2PromptApp.run_generation()](app.Wan2PromptApp.run_generation():327)
  - Inspire: [Wan2PromptApp.run_inspiration()](app.Wan2PromptApp.run_inspiration():372)

## History

Where:
- %APPDATA%\Wan2PromptGenerator\wan2_prompt_history.json
  - Created on first write: [get_history_file_path()](backend.get_history_file_path():15)

Operations:
- Add: [add_to_history()](backend.add_to_history():47)
- Load: [load_history()](backend.load_history():26)
- Delete one: [delete_from_history()](backend.delete_from_history():72)
- Clear: [clear_history()](backend.clear_history():80)
- Export JSON/CSV: [export_history()](backend.export_history():152)

UI:
- Search and filter (service/model/creativity): [app.py](app.py:167)–[app.py](app.py:193), [app.py](app.py:680)–[app.py](app.py:716)

## Endpoints

- LM Studio default: http://localhost:1234/v1/chat/completions (see [DEFAULT_LM_STUDIO_URL](backend.py:8))
- Ollama default: http://localhost:11434 (see [DEFAULT_OLLAMA_URL](backend.py:9))

Switching service updates defaults and pull controls visibility: [Wan2PromptApp.update_ui_for_service()](app.Wan2PromptApp.update_ui_for_service():239)

## Troubleshooting

- “No models found”:
  - Ensure the service is running locally and the correct endpoint is in the API input (Row 0).
  - Press “⟳ Refresh” after starting the service. See [refresh_models()](app.Wan2PromptApp.refresh_models():268).

- Packaging pulls in Qt (PySide/qtpy) unexpectedly:
  - Use additional excludes if the binary is too large:
    - --exclude-module qtpy --exclude-module PySide2 --exclude-module PySide6

- Antivirus/SmartScreen warnings:
  - Common for unsigned EXEs. Sign the binary or keep it locally.

- Tcl/Tk splash issues:
  - PyInstaller should embed Tcl/Tk data automatically (verified in the logs). If it fails, ensure Python’s tk/tcl is installed and not stripped.

## Project Structure

- [app.py](app.py:1): UI, threading, history panel, and actions
- [backend.py](backend.py:1): HTTP requests, prompt assembly, history I/O, exports
- [UI_DESIGN_BLUEPRINT.md](UI_DESIGN_BLUEPRINT.md:1): One‑shot implementation spec and visual layout contract
- dist\Wan2PromptCrafter.exe: portable build output (after packaging)

## License

No license specified. Add a LICENSE file if you intend to distribute.

## Acknowledgements

- CustomTkinter for modern dark‑themed Tk UI
- LM Studio / Ollama for local LLM inference
## One‑Click Builder (Windows)

- Use the provided batch script to go from zero to EXE automatically:
  - Double‑click [build_exe.bat](build_exe.bat:1)
  - What it does:
    - Detects Python (prefers py, falls back to python). If not installed, downloads and silently installs Python 3.10.11 x64.
    - Ensures pip is available and upgraded.
    - Installs dependencies from [requirements.txt](requirements.txt:1) (or a minimal set if the file is missing).
    - Runs PyInstaller with icon + splash + module excludes to produce dist\Wan2PromptCrafter.exe.
  - Icon/splash path assumed: C:\Users\WontML\Pictures\1a\icon.png. If the file is missing, the script builds without icon/splash and notifies you in the console.

Troubleshooting:
- If Python installation just finished, the shell PATH may need a new session; the script attempts to refresh PATH heuristically. If it still cannot find python/py, close the terminal and run the batch again.
- To reduce EXE size further, adjust excludes inside [build_exe.bat](build_exe.bat:1).
