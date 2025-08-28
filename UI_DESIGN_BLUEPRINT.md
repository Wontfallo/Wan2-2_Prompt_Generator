# Wan 2.2 Prompt Crafter - UI Design Blueprint

## Overview
A professional desktop application for generating AI video prompts with an integrated history system and resizable layout.

## Core Design Principles
1. **Professional Appearance** - Clean, modern interface with proper visual hierarchy
2. **Functional Layout** - Logical flow from configuration → input → generation → output
3. **Responsive Design** - Graceful handling of window resizing without element disappearance
4. **Visual Clarity** - Clear separation between functional areas with appropriate borders and spacing

## Window Structure

### Main Window Layout
```
┌─────────────────────────────────────────────────────────────┐
│                     Wan 2.2 Prompt Crafter                  │
├─────────────────────────────────────────────────────────────┤
│ CONFIG FRAME (Fixed Height, Compact)                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ LLM Service: [LM Studio ☑] [Ollama ☐]                 │ │
│ │ API Endpoint: [http://localhost:11434         ]         │ │
│ │ Model: [llama3.2:latest ▼] [⟳ Refresh]                  │ │
│ │ Creativity: [Moderate Freedom ☑] [High Freedom ☐]      │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ INPUT FRAME (Resizable)                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Your Idea or Basic Prompt                              │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ [Scrollable text area for user input]              │ │ │
│ │ │ [Minimum 4 lines, expands with frame]              │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [✨ Inspire Me] [Generate Wan 2.2 Prompt] [📚 History] │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT FRAME (Resizable, Largest)                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Generated Prompt                                        │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ [Scrollable text area for AI output]               │ │ │
│ │ │ [Expands with frame, shows full prompts]           │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [Copy to Clipboard]                                    │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ NEGATIVE PROMPT FRAME (Resizable)                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Negative Prompt (for Wan 2.2)                          │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ [Scrollable text area for negative prompt]         │ │ │
│ │ │ [Minimum 3 lines, expands with frame]              │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [Unlock to Edit ☑]                                    │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ HISTORY PANEL (Toggleable, Resizable)                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Prompt History (42)                                    │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 🔍 Search: [Search prompts and inputs...]             │ │
│ │ 🎛️ Filters:                                           │ │
│ │ Model: [All Models ▼]                                  │ │
│ │ Creativity: [All ▼]                                    │ │
│ │ Service: [All Services ▼]                              │ │
│ │ [🗑️ Clear Filters]                                     │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ [Scrollable list of history items]                     │ │
│ │ ├─────────────────────────────────────────────────────┤ │ │
│ │ │ 12/15/2024 2:30 PM                                │ │ │
│ │ │ llama3.2:latest • High Freedom • Ollama            │ │ │
│ │ │ Input: A serene lake at sunset...                  │ │ │
│ │ │ A cinematic wide shot of a tranquil lake...        │ │ │
│ │ │ [Use Prompt] [Copy] [Delete]                       │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ [📄 Export JSON] [📊 Export CSV] [🗑️ Clear All History] │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Frame Behavior Specifications

### Config Frame
- **Height**: Fixed at ~120px (3 rows of controls)
- **Width**: Expands with window but maintains compact layout
- **Behavior**: Never shrinks below minimum readable size
- **Controls**: All buttons and inputs maintain readable sizes

### Content Frames (Input/Output/Negative)
- **Height**: Resizable with window and each other
- **Width**: Always full width of main content area
- **Minimum Heights**:
  - Input: 120px
  - Output: 200px
  - Negative: 100px
- **Text Areas**: Always fit within their frames, no overflow

### History Panel
- **Width**: Resizable 300-500px range
- **Height**: Full height when visible
- **Toggle**: Smooth show/hide animation
- **Content**: Scrollable list with fixed-size items

## Resizing Rules

### Window Resize Behavior
1. **Minimum Window Size**: 900x650px (prevents cramping)
2. **Config Frame**: Maintains fixed height, width adjusts
3. **Content Frames**: Heights adjust proportionally
4. **History Panel**: Width adjusts within limits
5. **Text Areas**: Always fit their containers
6. **Buttons**: Never shrink below readable sizes
7. **Fonts**: Scale appropriately but never below 10pt

### Proportional Resizing
- **Input Frame**: 20% of content area
- **Output Frame**: 50% of content area (largest)
- **Negative Frame**: 30% of content area

## Visual Design

### Colors & Themes
- **Primary**: Dark theme with professional appearance
- **Text**: White/light gray on dark backgrounds
- **Borders**: Subtle gray borders for frame separation
- **Buttons**: Consistent sizing with clear visual feedback

### Typography
- **Headers**: 14pt bold for section titles
- **Body Text**: 12pt for input/output text
- **Buttons**: 11-12pt for button text
- **Labels**: 12pt for form labels

### Spacing
- **Frame Padding**: 15px internal, 10px external
- **Element Spacing**: 10-15px between related elements
- **Section Spacing**: 15px between major sections

## Interaction Design

### Button Behavior
- **Generate Button**: Most prominent, central placement
- **History Toggle**: Context-aware (shows panel state)
- **Action Buttons**: Consistent sizing and placement
- **Hover States**: Clear visual feedback

### Text Area Behavior
- **Input**: Multi-line with scroll when needed
- **Output**: Read-only with copy functionality
- **Negative**: Editable when unlocked
- **History**: Expandable previews with full text option

### Resize Handle Behavior
- **Visibility**: Clearly visible but not obtrusive
- **Responsiveness**: Smooth resizing without lag
- **Constraints**: Prevent unusable layouts

## Error Prevention

### Layout Constraints
1. **No Element Disappearance**: All elements remain visible during resize
2. **Minimum Sizes**: Prevent buttons/text from becoming unreadable
3. **Proportional Scaling**: Maintain visual balance
4. **Content Preservation**: No text truncation or overflow

### User Experience
1. **Intuitive Controls**: Clear button labels and functions
2. **Visual Feedback**: Loading states and progress indicators
3. **Error Handling**: Clear error messages with recovery options
4. **Accessibility**: Sufficient contrast and readable fonts

## Implementation Guidelines

### Code Structure
- **Separation of Concerns**: UI layout separate from business logic
- **Modular Design**: Reusable components and consistent patterns
- **Responsive Layout**: Grid and paned window systems
- **State Management**: Proper handling of UI state changes

### Performance Considerations
- **Efficient Rendering**: Minimize redraws during resize
- **Memory Management**: Clean up unused UI elements
- **Smooth Animation**: Fluid transitions for panel toggles

This blueprint serves as the definitive guide for the UI implementation, ensuring consistency and preventing the layout issues experienced previously.
---
# Definitive One‑Shot Implementation Spec (v2)

This appendix captures the exact, final UI and behavior that the current application implements. Handing only this file to a new engineer should be sufficient to recreate the app in a single pass.

References to concrete code locations:
- Core window and layout construction: [Wan2PromptApp.__init__()](app.py:8), [Wan2PromptApp.create_widgets()](app.py:46)
- Service-dependent UI behavior: [Wan2PromptApp.update_ui_for_service()](app.py:239)
- Threaded actions (refresh, pull, generate, inspire): [Wan2PromptApp.refresh_models()](app.py:269), [Wan2PromptApp.pull_model()](app.py:292), [Wan2PromptApp.run_generation()](app.py:327), [Wan2PromptApp.run_inspiration()](app.py:372)
- Backend API calls and history: [backend.py](backend.py:1), [generate_prompt()](backend.py:272), [get_inspiration()](backend.py:328), [history helpers](backend.py:26)

## Technology Stack
- Python 3.10+
- customtkinter (dark theme, Tk-based; not Qt)
- requests (HTTP)
- clipboard (for system clipboard integration)
- Packaging: PyInstaller (Windows .exe), with icon and splash

## Window, Panels, and Sizing
- Base window width: 800px to avoid truncation. See [Wan2PromptApp.__init__()](app.py:12) and width fields in [app.py](app.py:31).
- History panel: accordion-style side panel. Default collapsed so the main content stays focused. Expand shrinks/grows overall window width programmatically to keep content legible. See [toggle_history_panel()](app.py:402).

## Main Layout (Top → Bottom)
The main content is a single column containing:
1) Config Frame (compact, fixed-height with three internal rows)
2) Input Frame (blue section, high vertical priority)
3) Generate Button (primary CTA)
4) Output Frame (shares vertical space with Input)
5) Negative Prompt Frame (compact)

Grid fundamentals:
- The main frame fixes a content width and uses grid weights to distribute height primarily between Input and Output: [app.py](app.py:85), [app.py](app.py:104)
- All inner frames use sticky="ew" for full-width behavior, and appropriate row/column weights for flexible text areas.

## Config Frame: 3 Internal Rows (Exact, Final)
Column scheme inside config_frame (0..4):
- 0: Labels (LLM Service, API Endpoint label, Model:, Creativity:)
- 1: Large control cell (segmented button, model dropdown, creativity pills)
- 2: Compact action (Refresh)
- 3: Large control cell on the right (API entry or Pull entry)
- 4: Compact action (Pull Model button)

Row 0 (Services & Endpoint):
- “LLM Service” label, segmented switch [LM Studio | Ollama] in column 1
- “API Endpoint:” label in column 2, URL entry in column 3
- Snug padding. See [app.py](app.py:54)–[app.py](app.py:62)

Row 1 (Model + Pull: single dense row, no truncation):
- Label “Model:” in column 0 (very tight left padding)
- Model dropdown in column 1 (expands)
- “⟳ Refresh” button in column 2 (compact)
- Pull entry (placeholder: “e.g., llama3:latest”) in column 3 (expands)
- “Pull Model” button in column 4 (compact)
- This row is intentionally dense; keep label very close to dropdown. See [app.py](app.py:64)–[app.py](app.py:77)
- Service-specific visibility of pull section: shown for “Ollama”, hidden for “LM Studio”: [update_ui_for_service()](app.py:239)

Row 2 (Creativity):
- Label “Creativity:” in column 0
- Segmented button with two options: “Moderate Freedom”, “High Freedom” in column 1 (columnspan=4 so it never truncates)
- Padding remains tight but readable. See [app.py](app.py:79)–[app.py](app.py:83)

## Input Frame (Blue Section)
- Title left: “Your Idea or Basic Prompt”
- Action right: “✨ Inspire Me” on the same header row
- Below header: A large multiline CTkTextbox for the user input. Height and main grid weights give this section significant space, sharing vertically with Output. See [app.py](app.py:85)–[app.py](app.py:99)
- Behavior:
  - If “Inspire Me” clicked with empty input, app seeds a default idea then requests inspiration: [run_inspiration()](app.py:372) → [backend.get_inspiration()](backend.py:328)

## Generate Button (Primary CTA)
- Big centered “Generate Wan 2.2 Prompt” button between Input and Output, full-width row: [app.py](app.py:100)–[app.py](app.py:103)

## Output Frame
- Title left: “Generated Prompt”
- Action right: “Copy to Clipboard”
- Body: read-only multiline CTkTextbox; shares available height with the Input box due to weights: [app.py](app.py:104)–[app.py](app.py:120)
- Copy action reads content and sends to system clipboard: [copy_output()](app.py:258)

## Negative Prompt Frame
- Title: “Negative Prompt (for Wan 2.2)”
- Right action: checkbox “Unlock to Edit” (locked by default)
- Body: CTkTextbox seeded with a default negative prompt; disabled until unlocked: [app.py](app.py:116)–[app.py](app.py:136)
- Toggle logic: [toggle_neg_prompt_edit()](app.py:254)

## History Panel (Accordion)
- Collapsed by default. Toggle button is always visible on the right side panel.
- Expanding shows:
  - Search box (live filtering)
  - Dropdown filters (Service, Model, Creativity)
  - Scrollable history list with item actions
  - Clear/Export buttons
- Storage location: %APPDATA%/Wan2PromptGenerator/wan2_prompt_history.json
  - Paths and helpers: [backend.get_history_file_path()](backend.py:15), [load_history()](backend.py:26), [add_to_history()](backend.py:47)
- UI creation and item rendering: [create_history_panel()](app.py:132), [update_history_display()](app.py:444), [create_history_item()](app.py:458)
- Expand/Collapse implementation: [toggle_history_panel()](app.py:402)

## LLM Backends and Prompts
- Creativity modes drive the system prompt template selection: [get_system_prompt()](backend.py:177)
  - Moderate Freedom: enrich user idea directly
  - High Freedom: treat user idea as a seed and invent more
- Generate Prompt:
  - LM Studio: OpenAI-compatible /v1 chat completions
  - Ollama: /api/chat (non-stream), messages-based schema
  - Network code: [generate_prompt()](backend.py:272)
- Inspire Me:
  - Produces three one-liner ideas based on the current user input: [get_inspiration_prompt()](backend.py:212), [get_inspiration()](backend.py:328)

## Threading and UI State
- All long-running operations run on daemon threads and marshal UI updates via .after(0, ...):
  - Refresh models: [refresh_models()](app.py:268)
  - Pull model: [pull_model()](app.py:292)
  - Generate: [run_generation()](app.py:326)
  - Inspire: [run_inspiration()](app.py:372)
- A single UI-state switch controls enabling/disabling buttons while busy: [set_ui_loading()](app.py:220)

## Error and Edge Handling
- Model selection guardrails before generate/inspire: [run_generation()](app.py:327), [run_inspiration()](app.py:373)
- Empty input guardrails and seed: [run_inspiration()](app.py:377)–[app.py](app.py:381)
- Robust HTTP error reporting for both services: [backend.generate_prompt()](backend.py:320)–[backend.py](backend.py:325), [backend.get_inspiration()](backend.py:361)–[backend.py](backend.py:366)

## Packaging to Windows EXE
- Tool: PyInstaller (windowed, one-file)
- Icon and splash: use the same PNG: C:\Users\WontML\Pictures\1a\icon.png
- Recommended command (Windows PowerShell):
  - python -m pip install --upgrade pyinstaller
  - pyinstaller --noconfirm --clean --onefile --windowed app.py --name "Wan2PromptCrafter" --icon "C:\Users\WontML\Pictures\1a\icon.png" --splash "C:\Users\WontML\Pictures\1a\icon.png" --exclude-module PyQt5 --exclude-module PyQt6
- Output: dist\Wan2PromptCrafter.exe

## Dependency Summary
- pip packages required at runtime:
  - customtkinter
  - requests
  - clipboard
- Build-time:
  - pyinstaller

## Rebuild-from-Scratch Checklist
1) Create two modules: [app.py](app.py:1) and [backend.py](backend.py:1).
2) Implement UI per this spec in [Wan2PromptApp](app.py:8) with the exact 3-row Config Frame layout:
   - Row 0: LLM Service segmented + API endpoint entry
   - Row 1: Model label + dropdown + Refresh + Pull entry + Pull button on one dense row
   - Row 2: Creativity segmented (two options)
3) Implement Input/Output/Negative frames with the grid weights and read-only output behavior.
4) Implement the history panel as an accordion, collapsed by default, and file-backed at %APPDATA%.
5) Wrap all network and model operations in threads; synchronize back to UI using after(0, ...).
6) Use backend service calls for LM Studio and Ollama exactly as defined in [backend.generate_prompt()](backend.py:272) and [backend.get_inspiration()](backend.py:328).
7) Package with the PyInstaller command above and verify the EXE functions offline with local endpoints.