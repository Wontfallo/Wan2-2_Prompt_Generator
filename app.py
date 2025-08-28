import customtkinter as ctk
import backend
import threading
import clipboard
from tkinter import messagebox
from datetime import datetime

class Wan2PromptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Wan 2.2 Prompt Crafter")
        # Start with narrower size so expand button is always visible
        self.base_width = 800  # Wider main content to prevent truncation
        # START COLLAPSED - window size includes collapsed button area
        collapsed_width = self.base_width + 60  # base + button area
        self.geometry(f"{collapsed_width}x850")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configure grid for main content and history panel
        self.grid_columnconfigure(0, weight=0)  # Main content - fixed width
        self.grid_columnconfigure(1, weight=0)  # History panel - fixed width, no expansion
        self.grid_rowconfigure(0, weight=1)

        # --- Default Negative Prompt ---
        self.DEFAULT_NEGATIVE_PROMPT = "bright colors, overexposed, static, blurred details, subtitles, style, artwork, painting, picture, still, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, malformed limbs, fused fingers, still picture, cluttered background, three legs, many people in the background, walking backwards"

        # --- Main Frame - Narrower width so expand button is visible ---
        self.main_frame = ctk.CTkFrame(self, width=780)
        self.main_frame.grid(row=0, column=0, padx=15, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_propagate(False)  # Maintain fixed width

        # --- History Panel ---
        self.create_history_panel()

        # --- WIDGETS ---
        self.create_widgets()
        self.update_ui_for_service() # Set initial state
        self.load_history() # Load initial history
        
        # History panel starts collapsed - no need to toggle it

    def create_widgets(self):
        # --- Top Configuration Frame - Compact Layout ---
        config_frame = ctk.CTkFrame(self.main_frame)
        config_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(2, weight=0)
        config_frame.grid_columnconfigure(3, weight=1)

        # Row 0: Service Selector and API Endpoint (shortened)
        ctk.CTkLabel(config_frame, text="LLM Service:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.service_var = ctk.StringVar(value="Ollama")
        self.service_switch = ctk.CTkSegmentedButton(config_frame, values=["LM Studio", "Ollama"], variable=self.service_var, command=self.service_switch_callback)
        self.service_switch.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(config_frame, text="API Endpoint:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.api_url_entry = ctk.CTkEntry(config_frame, width=180)  # Shortened from 300 to 180
        self.api_url_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Row 1: Model Selector and Refresh Button
        ctk.CTkLabel(config_frame, text="Model:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=2, pady=6, sticky="w")
        self.model_var = ctk.StringVar(value="Loading...")
        self.model_menu = ctk.CTkOptionMenu(config_frame, variable=self.model_var, values=[""], state="disabled")
        self.model_menu.grid(row=1, column=1, padx=2, pady=6, sticky="ew")
        
        self.refresh_button = ctk.CTkButton(config_frame, text="⟳ Refresh", width=80, command=self.refresh_models)
        self.refresh_button.grid(row=1, column=2, padx=2, pady=6, sticky="w")

        # Row 2: Pull Model Entry and Button (moved under model row)
        self.ollama_pull_entry = ctk.CTkEntry(config_frame, placeholder_text="e.g., llama3:latest", width=220)
        self.ollama_pull_entry.grid(row=1, column=3, padx=6, pady=6, sticky="ew")
        self.ollama_pull_button = ctk.CTkButton(config_frame, text="Pull Model", width=80, command=self.pull_model)
        self.ollama_pull_button.grid(row=1, column=4, padx=6, pady=6, sticky="w")

        # Row 3: Creativity Level
        ctk.CTkLabel(config_frame, text="Creativity:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=6, sticky="w")
        self.creativity_var = ctk.StringVar(value="High Freedom")
        self.creativity_switch = ctk.CTkSegmentedButton(config_frame, values=["Moderate Freedom", "High Freedom"], variable=self.creativity_var)
        self.creativity_switch.grid(row=2, column=1, columnspan=4, padx=10, pady=6, sticky="ew")
        
        # --- User Input Frame ---
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=1)
        # Let input and output split available vertical space evenly
        self.main_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Your Idea or Basic Prompt", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.user_input_textbox = ctk.CTkTextbox(input_frame, height=160, wrap="word")
        self.user_input_textbox.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        self.inspire_button = ctk.CTkButton(input_frame, text="✨ Inspire Me", command=self.run_inspiration)
        self.inspire_button.grid(row=0, column=1, padx=10, pady=(10,5), sticky="e")
        
        # --- Generation Button ---
        self.generate_button = ctk.CTkButton(self.main_frame, text="Generate Wan 2.2 Prompt", height=40, font=ctk.CTkFont(size=16, weight="bold"), command=self.run_generation)
        self.generate_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Output Frame ---
        output_frame = ctk.CTkFrame(self.main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        output_header_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_header_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        output_header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(output_header_frame, text="Generated Prompt", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")
        self.copy_button = ctk.CTkButton(output_header_frame, text="Copy to Clipboard", command=self.copy_output)
        self.copy_button.grid(row=0, column=1, sticky="e")
        
        self.output_textbox = ctk.CTkTextbox(output_frame, wrap="word", state="disabled")
        self.output_textbox.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")

        # --- Negative Prompt Frame ---
        neg_prompt_frame = ctk.CTkFrame(self.main_frame)
        neg_prompt_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        neg_prompt_frame.grid_columnconfigure(0, weight=1)
        
        neg_header_frame = ctk.CTkFrame(neg_prompt_frame, fg_color="transparent")
        neg_header_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        neg_header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(neg_header_frame, text="Negative Prompt (for Wan 2.2)", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w")
        self.edit_neg_prompt_check = ctk.CTkCheckBox(neg_header_frame, text="Unlock to Edit", command=self.toggle_neg_prompt_edit)
        self.edit_neg_prompt_check.grid(row=0, column=1, sticky="e")

        self.neg_prompt_textbox = ctk.CTkTextbox(neg_prompt_frame, height=80, wrap="word")
        self.neg_prompt_textbox.insert("1.0", self.DEFAULT_NEGATIVE_PROMPT)
        self.neg_prompt_textbox.configure(state="disabled")
        self.neg_prompt_textbox.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="ew")

    def create_history_panel(self):
        """Create the collapsible history side panel"""
        # History panel container - START COLLAPSED
        self.history_panel = ctk.CTkFrame(self, width=40)  # Start narrow
        self.history_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.history_panel.grid_columnconfigure(0, weight=1)
        self.history_panel.grid_rowconfigure(1, weight=1)
        self.history_panel.grid_propagate(False)  # Maintain fixed width

        # History panel header with toggle button (collapsed by default)
        self.history_header = ctk.CTkFrame(self.history_panel, fg_color="transparent")
        # Start compact so the button is always visible
        self.history_header.grid(row=0, column=0, padx=2, pady=(5,5), sticky="ew")
        self.history_header.grid_columnconfigure(0, weight=1)

        # Title label (hidden while collapsed so it doesn't push the button off-screen)
        self.history_title_label = ctk.CTkLabel(self.history_header, text="📚 Prompt History", font=ctk.CTkFont(size=14, weight="bold"))
        # Do not grid the label yet (keeps header narrow). It will be shown on expand.

        # Toggle button is always visible
        self.history_toggle_btn = ctk.CTkButton(self.history_header, text="▶", width=30, command=self.toggle_history_panel)
        self.history_toggle_btn.grid(row=0, column=1, sticky="e")

        # Collapsible content frame - START HIDDEN
        self.history_content_frame = ctk.CTkFrame(self.history_panel)
        # DON'T grid it yet - it should start hidden
        self.history_content_frame.grid_columnconfigure(0, weight=1)
        self.history_content_frame.grid_rowconfigure(2, weight=1)  # Make history list expand, not button area

        # Search bar
        search_frame = ctk.CTkFrame(self.history_content_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        self.history_search_var = ctk.StringVar()
        self.history_search_entry = ctk.CTkEntry(search_frame, textvariable=self.history_search_var, placeholder_text="Search prompts...")
        self.history_search_entry.grid(row=1, column=0, pady=(5,0), sticky="ew")
        self.history_search_entry.bind("<KeyRelease>", self.on_search_change)

        # Filter controls
        filter_frame = ctk.CTkFrame(self.history_content_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        filter_frame.grid_columnconfigure([0, 2], weight=1)

        ctk.CTkLabel(filter_frame, text="🎛️ Filters:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,5))

        # Service filter
        ctk.CTkLabel(filter_frame, text="Service:", font=ctk.CTkFont(size=11)).grid(row=1, column=0, sticky="w")
        self.history_service_filter = ctk.CTkOptionMenu(filter_frame, values=["All", "LM Studio", "Ollama"], command=self.on_filter_change)
        self.history_service_filter.grid(row=2, column=0, sticky="ew", pady=(0,5))

        # Model filter
        ctk.CTkLabel(filter_frame, text="Model:", font=ctk.CTkFont(size=11)).grid(row=1, column=1, sticky="w")
        self.history_model_filter = ctk.CTkOptionMenu(filter_frame, values=["All"], command=self.on_filter_change)
        self.history_model_filter.grid(row=2, column=1, sticky="ew", pady=(0,5))

        # Creativity filter
        ctk.CTkLabel(filter_frame, text="Creativity:", font=ctk.CTkFont(size=11)).grid(row=1, column=2, sticky="w")
        self.history_creativity_filter = ctk.CTkOptionMenu(filter_frame, values=["All", "Moderate Freedom", "High Freedom"], command=self.on_filter_change)
        self.history_creativity_filter.grid(row=2, column=2, sticky="ew", pady=(0,5))

        # History listbox with scrollbar - use full available space
        self.history_listbox = ctk.CTkScrollableFrame(self.history_content_frame)
        self.history_listbox.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # History management buttons
        button_frame = ctk.CTkFrame(self.history_content_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=10, pady=(5,10), sticky="ew")
        button_frame.grid_columnconfigure([0, 1], weight=1)

        self.clear_history_btn = ctk.CTkButton(button_frame, text="🗑️ Clear All", command=self.clear_history)
        self.clear_history_btn.grid(row=0, column=0, padx=(0,5), sticky="ew")

        self.export_history_btn = ctk.CTkButton(button_frame, text="📤 Export", command=self.export_history)
        self.export_history_btn.grid(row=0, column=1, padx=(5,0), sticky="ew")

        # Initialize filter defaults
        self.history_service_filter.set("All")
        self.history_model_filter.set("All")
        self.history_creativity_filter.set("All")

        # History data
        self.history_data = []
        self.filtered_history = []

    # --- UI Logic and Callbacks ---
    
    def set_ui_loading(self, is_loading):
        """Disables/Enables buttons during generation."""
        state = "disabled" if is_loading else "normal"
        self.generate_button.configure(state=state, text="Generating..." if is_loading else "Generate Wan 2.2 Prompt")
        self.inspire_button.configure(state=state)
        self.refresh_button.configure(state=state)
        self.ollama_pull_button.configure(state=state)
        self.service_switch.configure(state=state)

    def service_switch_callback(self, value):
        self.update_ui_for_service()
        self.refresh_models()

    def update_ui_for_service(self):
        service = self.service_var.get()
        if service == "LM Studio":
            self.api_url_entry.delete(0, "end")
            self.api_url_entry.insert(0, backend.DEFAULT_LM_STUDIO_URL)
            # Hide pull section
            self.ollama_pull_entry.grid_remove()
            self.ollama_pull_button.grid_remove()
        else: # Ollama
            self.api_url_entry.delete(0, "end")
            self.api_url_entry.insert(0, backend.DEFAULT_OLLAMA_URL)
            # Show pull section
            self.ollama_pull_entry.grid(row=1, column=3, padx=6, pady=6, sticky="ew")
            self.ollama_pull_button.grid(row=1, column=4, padx=6, pady=6, sticky="w")
    
    def update_output_text(self, text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", text)
        self.output_textbox.configure(state="disabled")

    def toggle_neg_prompt_edit(self):
        is_checked = self.edit_neg_prompt_check.get()
        self.neg_prompt_textbox.configure(state="normal" if is_checked else "disabled")

    def copy_output(self):
        text_to_copy = self.output_textbox.get("1.0", "end-1c")
        if text_to_copy:
            clipboard.copy(text_to_copy)
            messagebox.showinfo("Copied!", "The prompt has been copied to your clipboard.")
        else:
            messagebox.showwarning("Empty!", "There is no prompt to copy.")
            
    # --- Threaded Backend Calls ---
    
    def refresh_models(self):
        self.model_menu.configure(state="disabled")
        self.model_var.set("Fetching...")
        threading.Thread(target=self._refresh_models_thread, daemon=True).start()

    def _refresh_models_thread(self):
        service = self.service_var.get()
        api_url = self.api_url_entry.get()
        
        if service == "LM Studio":
            models = backend.get_lm_studio_models(api_url)
        else:
            models = backend.get_ollama_models(api_url)
            
        def update_gui():
            if models:
                self.model_menu.configure(values=models, state="normal")
                self.model_var.set(models[0])
            else:
                self.model_menu.configure(values=["No models found"], state="disabled")
                self.model_var.set("No models found")
        
        self.after(0, update_gui)

    def pull_model(self):
        model_name = self.ollama_pull_entry.get()
        if not model_name:
            messagebox.showwarning("Warning", "Please enter a model name to pull.")
            return
        
        self.set_ui_loading(True)
        self.update_output_text(f"Pulling model: {model_name}...\nThis can take a while. See console for progress.")
        threading.Thread(target=self._pull_model_thread, args=(model_name,), daemon=True).start()

    def _pull_model_thread(self, model_name):
        api_url = self.api_url_entry.get()
        
        def progress_update(data):
            # Simple progress print to console, can be made more elaborate in GUI
            status = data.get('status', '')
            if 'total' in data and 'completed' in data:
                percent = (data['completed'] / data['total']) * 100
                print(f"\rPulling {model_name}: {status} - {percent:.1f}%", end="")
            else:
                print(f"\rPulling {model_name}: {status}", end="")

        success, message = backend.pull_ollama_model(model_name, api_url, progress_update)
        print() # Newline after progress bar
        
        def update_gui():
            self.set_ui_loading(False)
            self.update_output_text(message)
            if success:
                self.refresh_models() # Refresh list to include new model
        
        self.after(0, update_gui)


    def run_generation(self):
        if self.model_var.get() in ["Loading...", "No models found", ""]:
             messagebox.showerror("Error", "Please select a valid model first.")
             return
        if not self.user_input_textbox.get("1.0", "end-1c").strip():
            messagebox.showerror("Error", "The input idea cannot be empty.")
            return

        self.set_ui_loading(True)
        self.update_output_text("The LLM is crafting your prompt...")

        params = {
            "service": self.service_var.get(),
            "api_url": self.api_url_entry.get(),
            "model": self.model_var.get(),
            "creativity_level": self.creativity_var.get(),
            "user_idea": self.user_input_textbox.get("1.0", "end-1c")
        }
        
        threading.Thread(target=self._run_generation_thread, args=(params,), daemon=True).start()

    def _run_generation_thread(self, params):
        result = backend.generate_prompt(**params)
        def update_gui():
            self.update_output_text(result)
            self.set_ui_loading(False)

            # Save to history if generation was successful (not an error message)
            if result and not result.startswith("API Error:") and not result.startswith("Invalid service"):
                try:
                    backend.add_to_history(
                        user_idea=params['user_idea'],
                        generated_prompt=result,
                        service=params['service'],
                        model=params['model'],
                        creativity_level=params['creativity_level'],
                        api_url=params.get('api_url', '')
                    )
                    # Reload history display
                    self.load_history()
                except Exception as e:
                    print(f"Error saving to history: {e}")

        self.after(0, update_gui)
        

    def run_inspiration(self):
        if self.model_var.get() in ["Loading...", "No models found", ""]:
             messagebox.showerror("Error", "Please select a valid model first.")
             return
        user_idea = self.user_input_textbox.get("1.0", "end-1c").strip()
        if not user_idea:
            user_idea = "a single leaf" # Default if empty
            self.user_input_textbox.insert("1.0", user_idea)

        self.set_ui_loading(True)
        self.update_output_text("Asking the LLM for inspiration...")

        params = {
            "service": self.service_var.get(),
            "api_url": self.api_url_entry.get(),
            "model": self.model_var.get(),
            "user_idea": user_idea
        }

        threading.Thread(target=self._run_inspiration_thread, args=(params,), daemon=True).start()

    def _run_inspiration_thread(self, params):
        result = backend.get_inspiration(**params)
        def update_gui():
            self.update_output_text(f"Here are a few ideas based on '{params['user_idea']}':\n\n{result}\n\nCopy one of these into the 'Your Idea' box to expand on it!")
            self.set_ui_loading(False)
        self.after(0, update_gui)

    # --- History Panel Methods ---

    def toggle_history_panel(self):
        """Toggle the history panel content visibility (accordion style)"""
        if hasattr(self, 'history_content_frame'):
            if self.history_content_frame.winfo_viewable():
                # Collapse: Hide the content and shrink window
                self.history_content_frame.grid_remove()
                self.history_toggle_btn.configure(text="▶")
                # Hide the title to keep header ultra-compact
                try:
                    self.history_title_label.grid_remove()
                    self.history_header.grid_configure(padx=2, pady=(5,5))
                except Exception:
                    pass
                # Resize history panel to minimal width (just for the button)
                self.history_panel.configure(width=40)
                # Shrink window to just main content + small button area
                new_width = self.base_width + 60  # base + button area
                self.geometry(f"{new_width}x850")
            else:
                # Expand: Show the content and grow window
                self.history_content_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
                self.history_toggle_btn.configure(text="◀")
                # Show the title and restore header padding
                try:
                    self.history_title_label.grid(row=0, column=0, sticky="w")
                    self.history_header.grid_configure(padx=10, pady=(10,5))
                except Exception:
                    pass
                # Restore history panel to normal width
                self.history_panel.configure(width=400)
                # Expand window to accommodate history panel
                new_width = self.base_width + 440  # base + history panel width + padding
                self.geometry(f"{new_width}x850")

    def load_history(self):
        """Load and display history from file"""
        self.history_data = backend.load_history()
        self.filtered_history = self.history_data.copy()
        self.update_history_display()
        self.update_model_filter()

    def update_history_display(self):
        """Update the history list display"""
        # Clear existing history items
        for widget in self.history_listbox.winfo_children():
            widget.destroy()

        if not self.filtered_history:
            no_history_label = ctk.CTkLabel(self.history_listbox, text="No prompts in history", text_color="gray")
            no_history_label.pack(pady=20)
            return

        # Display history items
        for i, entry in enumerate(self.filtered_history):
            self.create_history_item(i, entry)

    def create_history_item(self, index, entry):
        """Create a single history item widget"""
        # Item container - larger height for better readability
        item_frame = ctk.CTkFrame(self.history_listbox)
        item_frame.pack(fill="x", padx=5, pady=8)  # Increased padding

        # Timestamp
        timestamp = datetime.fromisoformat(entry['timestamp'])
        time_str = timestamp.strftime("%m/%d %H:%M")

        # Header with timestamp and delete button
        header_frame = ctk.CTkFrame(item_frame, fg_color="transparent", height=25)
        header_frame.pack(fill="x", padx=10, pady=(10,5))
        header_frame.grid_columnconfigure(0, weight=1)

        timestamp_label = ctk.CTkLabel(header_frame, text=f"🕒 {time_str}", font=ctk.CTkFont(size=11, weight="bold"))
        timestamp_label.grid(row=0, column=0, sticky="w")

        delete_btn = ctk.CTkButton(header_frame, text="❌", width=25, height=25, font=ctk.CTkFont(size=10), command=lambda: self.delete_history_item(index))
        delete_btn.grid(row=0, column=1, sticky="e")

        # Model and creativity info
        info_label = ctk.CTkLabel(item_frame, text=f"{entry['service']} • {entry['model']} • {entry['creativity_level']}",
                                 font=ctk.CTkFont(size=10), text_color="gray")
        info_label.pack(anchor="w", padx=10, pady=(0,5))

        # User idea (truncated)
        user_idea = entry['user_idea'][:80] + "..." if len(entry['user_idea']) > 80 else entry['user_idea']
        user_label = ctk.CTkLabel(item_frame, text=f"💭 {user_idea}", font=ctk.CTkFont(size=11, weight="bold"),
                                 wraplength=280, justify="left")
        user_label.pack(anchor="w", padx=10, pady=(0,5))

        # Generated prompt preview (3-4 lines worth)
        prompt_preview = entry['generated_prompt'][:280] + "..." if len(entry['generated_prompt']) > 280 else entry['generated_prompt']
        
        prompt_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        prompt_frame.pack(fill="x", padx=10, pady=(0,10))
        prompt_frame.grid_columnconfigure(0, weight=1)
        
        prompt_label = ctk.CTkLabel(prompt_frame, text=f"🎬 {prompt_preview}", font=ctk.CTkFont(size=10),
                                   wraplength=280, justify="left", height=60)  # Fixed height for 3-4 lines
        prompt_label.grid(row=0, column=0, sticky="w")
        
        # "..." expand button if text is truncated
        if len(entry['generated_prompt']) > 280:
            expand_btn = ctk.CTkButton(prompt_frame, text="...", width=30, height=20, font=ctk.CTkFont(size=12, weight="bold"),
                                     command=lambda e=entry, btn=None: self.show_full_prompt_at_cursor(e, btn))
            expand_btn.grid(row=0, column=1, sticky="e", padx=(5,0))

        # Button frame for actions
        button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0,10))
        button_frame.grid_columnconfigure(0, weight=1)
        
        use_btn = ctk.CTkButton(button_frame, text="Use This Prompt", font=ctk.CTkFont(size=10), height=30,
                               command=lambda: self.use_history_item(entry))
        use_btn.pack(side="left")

    def delete_history_item(self, index):
        """Delete a specific history item"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this prompt from history?"):
            # Convert filtered index to actual index in history_data
            if index < len(self.filtered_history):
                actual_index = self.history_data.index(self.filtered_history[index])
                self.history_data = backend.delete_from_history(actual_index)
                self.filtered_history = self.history_data.copy()
                self.apply_filters()

    def show_full_prompt_at_cursor(self, entry, button_widget):
        """Show the full prompt in a popup window positioned near the cursor"""
        # Get mouse cursor position
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        
        # Adjust position to avoid going off screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        popup_width = 500
        popup_height = min(700, 300 + ((len(entry['user_idea']) + len(entry['generated_prompt'])) // 50) * 20)
        
        # Keep popup on screen
        if x + popup_width > screen_width:
            x = screen_width - popup_width - 20
        if y + popup_height > screen_height:
            y = screen_height - popup_height - 20
        
        # Minimum positioning
        x = max(20, x - 50)  # Offset a bit from cursor
        y = max(20, y - 50)
        
        self.show_full_prompt(entry, x, y)
    
    def show_full_prompt(self, entry, x=None, y=None):
        """Show the full prompt in a popup window"""
        # Calculate dynamic sizing based on content length
        user_idea_lines = len(entry['user_idea']) // 60 + entry['user_idea'].count('\n') + 1
        prompt_lines = len(entry['generated_prompt']) // 60 + entry['generated_prompt'].count('\n') + 1
        
        # Limit minimum and maximum sizes
        user_idea_lines = max(2, min(user_idea_lines, 8))
        prompt_lines = max(3, min(prompt_lines, 12))
        
        # Calculate window height based on content
        base_height = 200  # For header, buttons, padding
        text_height = (user_idea_lines + prompt_lines) * 20 + 100  # ~20px per line + padding
        total_height = min(base_height + text_height, 700)  # Max 700px
        
        # Create popup window - smaller and smarter sizing
        popup = ctk.CTkToplevel(self)
        popup.title("Full Prompt Details")
        popup.resizable(True, True)
        
        # Position popup at specified coordinates or center
        if x is not None and y is not None:
            popup.geometry(f"500x{total_height}+{x}+{y}")
        else:
            popup.geometry(f"500x{total_height}")
        
        # Make popup modal
        popup.transient(self)
        popup.grab_set()
        
        # Focus the popup
        popup.after(100, lambda: popup.focus())
        
        # Main frame
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)  # User idea gets some space
        main_frame.grid_rowconfigure(2, weight=2)  # Generated prompt gets more space
        
        # Header with metadata
        timestamp = datetime.fromisoformat(entry['timestamp'])
        time_str = timestamp.strftime("%m/%d/%Y %H:%M")
        
        header_label = ctk.CTkLabel(main_frame,
                                   text=f"🕒 {time_str} | {entry['service']} • {entry['model']} • {entry['creativity_level']}",
                                   font=ctk.CTkFont(size=11, weight="bold"))
        header_label.grid(row=0, column=0, pady=(5, 10), sticky="w")
        
        # User idea - proportional sizing
        user_idea_frame = ctk.CTkFrame(main_frame)
        user_idea_frame.grid(row=1, column=0, pady=(0, 5), sticky="nsew")
        user_idea_frame.grid_columnconfigure(0, weight=1)
        user_idea_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(user_idea_frame, text="💭 User Idea:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=8, pady=(8,3), sticky="w")
        
        user_idea_text = ctk.CTkTextbox(user_idea_frame, wrap="word", height=user_idea_lines * 20)
        user_idea_text.grid(row=1, column=0, padx=8, pady=(0,8), sticky="nsew")
        user_idea_text.insert("1.0", entry['user_idea'])
        user_idea_text.configure(state="disabled")
        
        # Generated prompt - proportional sizing
        prompt_frame = ctk.CTkFrame(main_frame)
        prompt_frame.grid(row=2, column=0, pady=(5, 0), sticky="nsew")
        prompt_frame.grid_columnconfigure(0, weight=1)
        prompt_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(prompt_frame, text="🎬 Generated Prompt:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=8, pady=(8,3), sticky="w")
        
        prompt_text = ctk.CTkTextbox(prompt_frame, wrap="word", height=prompt_lines * 20)
        prompt_text.grid(row=1, column=0, padx=8, pady=(0,8), sticky="nsew")
        prompt_text.insert("1.0", entry['generated_prompt'])
        prompt_text.configure(state="disabled")
        
        # Buttons - compact layout
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(10,5), sticky="ew")
        button_frame.grid_columnconfigure([0, 1, 2], weight=1)
        
        use_btn = ctk.CTkButton(button_frame, text="Use This Prompt", height=28,
                               command=lambda: [self.use_history_item(entry), popup.destroy()])
        use_btn.grid(row=0, column=0, padx=3, sticky="ew")
        
        copy_btn = ctk.CTkButton(button_frame, text="Copy Prompt", height=28,
                               command=lambda: self.copy_prompt_to_clipboard(entry['generated_prompt']))
        copy_btn.grid(row=0, column=1, padx=3, sticky="ew")
        
        close_btn = ctk.CTkButton(button_frame, text="Close", height=28, command=popup.destroy)
        close_btn.grid(row=0, column=2, padx=3, sticky="ew")

    def copy_prompt_to_clipboard(self, prompt_text):
        """Copy prompt text to clipboard"""
        try:
            clipboard.copy(prompt_text)
            # Show temporary success message
            temp_window = ctk.CTkToplevel(self)
            temp_window.geometry("200x80")
            temp_window.title("Success")
            temp_window.resizable(False, False)
            
            ctk.CTkLabel(temp_window, text="✅ Copied to clipboard!", font=ctk.CTkFont(size=12)).pack(expand=True)
            
            # Auto close after 1.5 seconds
            temp_window.after(1500, temp_window.destroy)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")

    def use_history_item(self, entry):
        """Use a history item to populate the main interface"""
        # Populate user input
        self.user_input_textbox.delete("1.0", "end")
        self.user_input_textbox.insert("1.0", entry['user_idea'])

        # Populate output
        self.update_output_text(entry['generated_prompt'])

        # Set service and model if they exist
        if entry.get('service'):
            self.service_var.set(entry['service'])
            self.update_ui_for_service()

        if entry.get('model'):
            self.model_var.set(entry['model'])

        if entry.get('creativity_level'):
            self.creativity_var.set(entry['creativity_level'])

    def on_search_change(self, event=None):
        """Handle search input changes"""
        self.apply_filters()

    def on_filter_change(self, value=None):
        """Handle filter changes"""
        self.apply_filters()

    def apply_filters(self):
        """Apply search and filter criteria"""
        query = self.history_search_var.get().strip()
        service_filter = self.history_service_filter.get()
        model_filter = self.history_model_filter.get()
        creativity_filter = self.history_creativity_filter.get()

        # Start with all history
        filtered = self.history_data.copy()

        # Apply search
        if query:
            filtered = backend.search_history(query, filtered)

        # Apply service filter
        if service_filter != "All":
            filtered = [item for item in filtered if item.get('service') == service_filter]

        # Apply model filter
        if model_filter != "All":
            filtered = [item for item in filtered if item.get('model') == model_filter]

        # Apply creativity filter
        if creativity_filter != "All":
            filtered = [item for item in filtered if item.get('creativity_level') == creativity_filter]

        self.filtered_history = filtered
        self.update_history_display()

    def update_model_filter(self):
        """Update the model filter dropdown with available models from history"""
        models = set()
        for entry in self.history_data:
            if entry.get('model'):
                models.add(entry['model'])

        model_list = ["All"] + sorted(list(models))
        self.history_model_filter.configure(values=model_list)
        if self.history_model_filter.get() not in model_list:
            self.history_model_filter.set("All")

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all prompt history? This cannot be undone."):
            self.history_data = backend.clear_history()
            self.filtered_history = []
            self.update_history_display()
            self.update_model_filter()

    def export_history(self):
        """Export history to file"""
        if not self.history_data:
            messagebox.showinfo("No Data", "No history data to export.")
            return

        # Ask user for format
        format_choice = self.ask_export_format()
        if not format_choice:
            return

        try:
            filename = backend.export_history(format_choice)
            messagebox.showinfo("Export Complete", f"History exported to: {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export history: {e}")

    def ask_export_format(self):
        """Ask user for export format"""
        dialog = ctk.CTkInputDialog(text="Choose export format (json/csv):", title="Export Format")
        format_choice = dialog.get_input()
        if format_choice and format_choice.lower() in ['json', 'csv']:
            return format_choice.lower()
        return None


if __name__ == "__main__":
    # Ensure PyInstaller splash screen is closed after the UI is ready
    splash = None
    try:
        import pyi_splash  # Provided by PyInstaller when --splash is used
        splash = pyi_splash
        pyi_splash.update_text("Loading UI...")
    except Exception:
        splash = None

    app = Wan2PromptApp()

    # Draw once so the window exists before closing splash
    try:
        app.update_idletasks()
        app.update()
    except Exception:
        pass

    if splash is not None:
        try:
            splash.close()
        except Exception:
            pass

    app.mainloop()