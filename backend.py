import requests
import json
import os
from datetime import datetime
from pathlib import Path

# --- Default API Endpoints ---
DEFAULT_LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_OLLAMA_URL = "http://localhost:11434"

# --- History Management ---
HISTORY_FILE = "wan2_prompt_history.json"
MAX_HISTORY_ENTRIES = 100

def get_history_file_path():
    """Get the path to the history file in %APPDATA%"""
    appdata = os.environ.get('APPDATA')
    if not appdata:
        # Fallback to user's home directory if APPDATA is not available
        appdata = str(Path.home())

    history_dir = Path(appdata) / "Wan2PromptGenerator"
    history_dir.mkdir(exist_ok=True)
    return history_dir / HISTORY_FILE

def load_history():
    """Load prompt history from file"""
    history_file = get_history_file_path()
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading history: {e}")
            return []
    return []

def save_history(history):
    """Save prompt history to file"""
    history_file = get_history_file_path()
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving history: {e}")

def add_to_history(user_idea, generated_prompt, service, model, creativity_level, api_url=""):
    """Add a new entry to the prompt history"""
    history = load_history()

    # Create new history entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_idea": user_idea,
        "generated_prompt": generated_prompt,
        "service": service,
        "model": model,
        "creativity_level": creativity_level,
        "api_url": api_url
    }

    # Add to beginning of list (most recent first)
    history.insert(0, entry)

    # Keep only the most recent entries
    if len(history) > MAX_HISTORY_ENTRIES:
        history = history[:MAX_HISTORY_ENTRIES]

    save_history(history)
    return history

def delete_from_history(index):
    """Delete an entry from history by index"""
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)
    return history

def clear_history():
    """Clear all history"""
    save_history([])
    return []

def search_history(query, history=None):
    """Search history by keywords in user_idea or generated_prompt"""
    if history is None:
        history = load_history()

    if not query.strip():
        return history

    query_lower = query.lower()
    filtered = []

    for entry in history:
        user_idea = entry.get('user_idea', '').lower()
        generated_prompt = entry.get('generated_prompt', '').lower()

        if query_lower in user_idea or query_lower in generated_prompt:
            filtered.append(entry)

    return filtered

def filter_history_by_date(start_date=None, end_date=None, history=None):
    """Filter history by date range"""
    if history is None:
        history = load_history()

    if not start_date and not end_date:
        return history

    filtered = []

    for entry in history:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()

        if start_date and end_date:
            if start_date <= entry_date <= end_date:
                filtered.append(entry)
        elif start_date:
            if entry_date >= start_date:
                filtered.append(entry)
        elif end_date:
            if entry_date <= end_date:
                filtered.append(entry)

    return filtered

def filter_history_by_metadata(service=None, model=None, creativity_level=None, history=None):
    """Filter history by metadata (service, model, creativity_level)"""
    if history is None:
        history = load_history()

    filtered = []

    for entry in history:
        match = True

        if service and entry.get('service') != service:
            match = False
        if model and entry.get('model') != model:
            match = False
        if creativity_level and entry.get('creativity_level') != creativity_level:
            match = False

        if match:
            filtered.append(entry)

    return filtered

def export_history(format_type="json"):
    """Export history to JSON or CSV format"""
    history = load_history()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format_type.lower() == "json":
        filename = f"wan2_history_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    elif format_type.lower() == "csv":
        import csv
        filename = f"wan2_history_{timestamp}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if history:
                writer = csv.DictWriter(f, fieldnames=history[0].keys())
                writer.writeheader()
                writer.writerows(history)

    return filename

# --- System Prompts ---

# This is the core instruction set for the LLM. It's designed to be flawless.
# It internalizes the Wan 2.2 rules and the user's creativity choice.

def get_system_prompt(creativity_level, user_idea):
    """
    Dynamically generates the system prompt based on the chosen creativity level.
    """
    
    # Common framework rules for both creativity levels
    framework_rules = """
    You are an expert prompt engineer for Wan 2.2, a text-to-video AI model. Your task is to take a user's idea and expand it into a detailed, visually stunning, and technically precise prompt.

    Adhere strictly to the Wan 2.2 Prompting Framework:
    1.  **Structure:** The final prompt must be a single paragraph, ideally between 80-120 words.
    2.  **Shot Order:** Always lead with what the camera sees first, then describe the camera's movement and what it reveals. Follow the structure: Opening shot -> Camera motion -> Reveal / pay-off.
    3.  **Camera Language:** Use specific, professional camera terms. Choose from: pan left/right, tilt up/down, dolly in/out, orbital arc, crane up.
    4.  **Motion Modifiers:** Enhance camera movements with speed adjectives (e.g., slow-motion, rapid whip-pan, time-lapse) and parallax cues (e.g., "foreground elements blur past, background remains sharp").
    5.  **Aesthetic Tags:** Inject rich visual detail using tags for lighting (e.g., volumetric dusk, harsh noon sun, neon rim light), color-grade (e.g., "teal-and-orange", "bleach-bypass", "kodak portra"), and lens/style (e.g., anamorphic bokeh, 16mm grain, CGI stylized).
    6.  **Clarity & Concision:** Do not use bullet points, numbering, or explicit parameter settings like 'frame count' in your output. The output should be a single, descriptive paragraph ready to be used as a prompt.
    """

    if creativity_level == "Moderate Freedom":
        specific_instructions = f"""
        **Creativity Mode: Moderate Freedom**
        Your task is to take the user's core idea and build upon it directly. Adhere closely to the subject provided by the user, but enrich it with essential cinematic details. Your goal is to enhance, not replace, the user's original concept.

        User's Idea: "{user_idea}"
        """
    else: # High Freedom
        specific_instructions = f"""
        **Creativity Mode: High Freedom**
        Your task is to use the user's idea as a seed for a completely new, highly creative scene. Invent a compelling narrative and a strong visual mood. You have full creative license to interpret the user's concept into a unique and breathtaking cinematic moment.

        User's Idea Seed: "{user_idea}"
        """
        
    return framework_rules + specific_instructions

def get_inspiration_prompt(user_idea):
    """
    Generates a system prompt for the 'Inspire Me' feature.
    """
    return f"""
    You are a creative assistant for a film director. The director has a basic idea and needs inspiration.
    Based on the user's idea of '{user_idea}', generate three distinct and visually compelling one-sentence scene concepts.
    These concepts should be creative, diverse, and serve as starting points for a full video prompt.
    Format your response as a numbered list (1., 2., 3.). Be concise and inspiring.
    """

# --- API Communication Functions ---

def get_lm_studio_models(api_url):
    """
    Fetches the list of loaded models from the LM Studio server.
    Note: The base URL for model listing is slightly different from chat completions.
    """
    try:
        # The model list endpoint is typically at /v1/models
        base_url = api_url.split('/v1/')[0]
        response = requests.get(f"{base_url}/v1/models")
        response.raise_for_status()
        models = response.json().get('data', [])
        return [model['id'] for model in models]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching LM Studio models: {e}")
        return []

def get_ollama_models(api_url):
    """
    Fetches the list of available models from the Ollama server.
    """
    try:
        response = requests.get(f"{api_url}/api/tags")
        response.raise_for_status()
        models = response.json().get('models', [])
        return [model['name'] for model in models]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Ollama models: {e}")
        return []

def pull_ollama_model(model_name, api_url, progress_callback=None):
    """
    Pulls a model from Ollama, with optional progress streaming.
    """
    try:
        payload = {"name": model_name, "stream": True}
        response = requests.post(f"{api_url}/api/pull", json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if progress_callback:
                    progress_callback(data)
        return True, "Model pulled successfully!"
    except requests.exceptions.RequestException as e:
        return False, f"Error pulling model: {e}"

def generate_prompt(service, api_url, model, creativity_level, user_idea):
    """
    The main function to generate the Wan 2.2 prompt by querying the LLM.
    """
    system_prompt = get_system_prompt(creativity_level, user_idea)
    
    headers = {"Content-Type": "application/json"}
    
    if service == "LM Studio":
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}],
            "temperature": 0.7,
        }
        chat_url = api_url
    elif service == "Ollama":
        payload = {
            "model": model,
            "prompt": "", # Will be overridden by messages
            "system": system_prompt,
             "stream": False,
             "options": {
                 "temperature": 0.7
             }
        }
        # Ollama can use different endpoints for chat vs generation
        chat_url = f"{api_url}/api/generate" if "generate" not in api_url else api_url
        # For consistency with OpenAI standard, let's try the chat endpoint first
        chat_url = f"{api_url}/api/chat"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}],
            "stream": False,
        }

    else:
        return "Invalid service selected."

    try:
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if service == "LM Studio":
            return data['choices'][0]['message']['content'].strip()
        elif service == "Ollama":
            # The structure for Ollama chat response is similar
            return data['message']['content'].strip()

    except requests.exceptions.RequestException as e:
        return f"API Error: Could not connect to the server at {api_url}. Please ensure it is running and the URL is correct.\n\nDetails: {e}"
    except (KeyError, IndexError) as e:
        return f"API Error: Received an unexpected response from the server. The model may not be compatible with the chat/completion API.\n\nDetails: {e}\nResponse: {response.text}"


def get_inspiration(service, api_url, model, user_idea):
    """
    Generates inspirational ideas by querying the LLM.
    """
    system_prompt = get_inspiration_prompt(user_idea)
    
    headers = {"Content-Type": "application/json"}
    
    if service == "LM Studio":
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}],
            "temperature": 0.9,
        }
        chat_url = api_url
    elif service == "Ollama":
        chat_url = f"{api_url}/api/chat"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}],
            "stream": False,
        }
    else:
        return "Invalid service selected."
        
    try:
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if service == "LM Studio":
            return data['choices'][0]['message']['content'].strip()
        elif service == "Ollama":
            return data['message']['content'].strip()
            
    except requests.exceptions.RequestException as e:
        return f"API Error: Could not connect to the server at {api_url}.\n\nDetails: {e}"
    except (KeyError, IndexError) as e:
        return f"API Error: Unexpected response from the server.\n\nDetails: {e}\nResponse: {response.text}"