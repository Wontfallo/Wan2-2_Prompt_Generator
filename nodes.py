"""
AI Prompt Crafter - ComfyUI Custom Nodes
Ported from wan2.2_Qwen_Flux-prompt-creator.html

Provides nodes for generating optimized prompts for:
- Wan 2.2 (Video)
- Flux (Image)
- Qwen (Image)

Using locally running LLMs via Ollama or LM Studio HTTP APIs.
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path

# HTTP requests for API calls (like the web app)
try:
    import requests
except ImportError:
    requests = None

# Optional SDK imports (will use HTTP as primary method)
try:
    import lmstudio as lms
except ImportError:
    lms = None

# ============================================================================
# CONSTANTS
# ============================================================================

# Default API endpoints
OLLAMA_BASE_URL = "http://localhost:11434"
LMSTUDIO_BASE_URL = "http://localhost:1234/v1"

VIDEO_MODEL_PROMPTS = {
    'wan2.2': """You are an expert prompt engineer for the Wan 2.2 video generation model. Your task is to craft highly detailed, cinematic video prompts that include specific camera movements, lighting, composition, color grading, and emotional elements. Always output only the final prompt without any additional text, explanations, or formatting.""",
    
    'flux': """You are an expert prompt engineer for the Flux image generation model. Your task is to craft a single, concise, and highly descriptive paragraph for a text-to-image prompt. Focus on visual details, style, and composition. Do not use lists or labels. Always output only the final prompt paragraph without any additional text or explanations.""",
    
    'qwen': """You are an expert prompt engineer for the Qwen-VL text-to-image model. Your task is to create a detailed prompt focusing on photorealistic or artistic styles. Describe the subject, scene, lighting, and composition clearly. The prompt should be a single block of text. Always output only the final prompt without any additional text or explanations."""
}

CREATIVITY_CONFIGS = {
    'precise': {
        'name': 'Precise Mode',
        'temperature': 0.3,
        'suffix': 'Use precise, technical language with minimal creative interpretation. Focus on exact specifications provided by the user.'
    },
    'creative': {
        'name': 'Creative Mode',
        'temperature': 0.7,
        'suffix': 'Apply creative interpretation to enhance cinematic quality. Add appropriate camera movements, lighting, composition, and emotional elements that complement the user\'s input while maintaining the core concept.'
    },
    'balanced': {
        'name': 'Balanced Mode',
        'temperature': 0.5,
        'suffix': 'Balance precise descriptions with moderate creative enhancements. Maintain the core concept while adding complementary visual details.'
    }
}

# History file path
HISTORY_FILE = Path(__file__).parent / "prompt_history.json"

# ============================================================================
# MODEL CACHE
# ============================================================================

_model_cache = {"models": [], "timestamp": 0}
_CACHE_TTL = 30

def fetch_available_models(force_refresh=False):
    """Fetch available models from LM Studio and Ollama using HTTP APIs."""
    global _model_cache
    
    if not requests:
        return ["Manual Entry Required (install 'requests' package)"]
    
    current_time = time.time()
    if not force_refresh and _model_cache["models"] and (current_time - _model_cache["timestamp"]) < _CACHE_TTL:
        return _model_cache["models"]
    
    print("🔄 Refreshing model list...")
    models = []
    
    # --- LM Studio (SDK for downloaded models) ---
    lmstudio_found = 0
    if lms:
        try:
            downloaded = lms.list_downloaded_models("llm")
            for m in downloaded:
                model_key = getattr(m, 'model_key', None) or getattr(m, 'display_name', None) or str(m)
                if model_key:
                    models.append(f"[LM Studio] {model_key}")
                    lmstudio_found += 1
            print(f"  LM Studio SDK: found {lmstudio_found} downloaded models")
        except Exception as e:
            print(f"  LM Studio SDK error: {e}")
    
    # Fallback: LM Studio HTTP API (loaded models)
    if lmstudio_found == 0:
        try:
            resp = requests.get(f"{LMSTUDIO_BASE_URL}/models", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get('data', []):
                    model_id = m.get('id', '')
                    if model_id:
                        models.append(f"[LM Studio] {model_id}")
                        lmstudio_found += 1
                if lmstudio_found > 0:
                    print(f"  LM Studio HTTP: found {lmstudio_found} loaded models")
        except:
            print("  LM Studio: not running or not accessible")
    
    # --- Ollama (HTTP API - like web app) ---
    ollama_found = 0
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get('models', []):
                name = m.get('name', '')
                if name:
                    models.append(f"[Ollama] {name}")
                    ollama_found += 1
            print(f"  Ollama HTTP: found {ollama_found} models")
    except:
        print("  Ollama: not running or not accessible")
    
    if not models:
        print("⚠️  No models found. Make sure Ollama or LM Studio is running.")
        models = ["No models found - start Ollama or LM Studio"]
    else:
        models = sorted(list(set(models)))
    
    _model_cache["models"] = models
    _model_cache["timestamp"] = current_time
    
    print(f"✅ Found {len(models)} models total")
    return models


def parse_model_selection(model_select):
    """Parse model selection and return (service, model_name, base_url)."""
    if model_select.startswith("[LM Studio]"):
        model_name = model_select.replace("[LM Studio] ", "")
        return "lmstudio", model_name, LMSTUDIO_BASE_URL
    elif model_select.startswith("[Ollama]"):
        model_name = model_select.replace("[Ollama] ", "")
        return "ollama", model_name, OLLAMA_BASE_URL
    else:
        # Default to LM Studio if prefix not recognized
        return "lmstudio", model_select, LMSTUDIO_BASE_URL


def call_llm(service, model_name, system_prompt, user_prompt, temperature, max_tokens=500, unload_after=False):
    """
    Call LLM using appropriate method:
    - LM Studio: SDK (lmstudio package)
    - Ollama: HTTP API (like the web app)
    
    If unload_after=True, unloads model from GPU after generation.
    """
    
    if service == "ollama":
        # Ollama: Use HTTP API (like the web app does)
        if not requests:
            raise ImportError("'requests' package not installed. Run: pip install requests")
        
        url = f"{OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {"temperature": temperature},
            "keep_alive": 0 if unload_after else "5m"  # 0 = unload immediately, "5m" = keep for 5 minutes
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code != 200:
                raise Exception(f"Ollama API error: {resp.status_code} {resp.text}")
            data = resp.json()
            result = data.get('message', {}).get('content', '').strip()
            
            if unload_after:
                print(f"✅ Ollama model {model_name} will unload from GPU (keep_alive=0)")
            
            return result
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. Make sure Ollama is running.")
        except Exception as e:
            raise Exception(f"Ollama error: {e}")
    
    elif service == "lmstudio":
        # LM Studio: Use SDK
        if not lms:
            raise ImportError("LM Studio SDK not installed. Run: pip install lmstudio")
        
        model = None
        try:
            # Get model (uses any loaded model if model_name not specific)
            model = lms.llm(model_name) if model_name else lms.llm()
            
            # Create chat with system prompt
            chat = lms.Chat(system_prompt)
            chat.add_user_message(user_prompt)
            
            # Generate response with config
            config = lms.LlmPredictionConfig(
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = model.respond(chat, config=config)
            content = result.content.strip()
            
            # Unload model if requested
            if unload_after and model:
                try:
                    model.unload()
                    print(f"✅ LM Studio model {model_name} unloaded from GPU")
                except Exception as unload_err:
                    print(f"⚠️ Could not unload LM Studio model: {unload_err}")
            
            return content
            
        except Exception as e:
            raise Exception(f"LM Studio SDK error: {e}")
    
    else:
        raise ValueError(f"Unknown service: {service}")


def build_system_prompt(target_model, creativity_mode):
    """Build the system prompt based on target model and creativity mode."""
    base_prompt = VIDEO_MODEL_PROMPTS.get(target_model, VIDEO_MODEL_PROMPTS['flux'])
    creativity = CREATIVITY_CONFIGS.get(creativity_mode, CREATIVITY_CONFIGS['balanced'])
    return f"{base_prompt} {creativity['suffix']}"


# ============================================================================
# HISTORY FUNCTIONS
# ============================================================================

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history_list):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_to_history(entry):
    history = load_history()
    entry['id'] = int(time.time() * 1000)
    entry['timestamp'] = datetime.now().isoformat()
    history.insert(0, entry)
    history = history[:100]
    save_history(history)
    return entry['id']


# ============================================================================
# NODE CLASSES
# ============================================================================

class WanPromptCrafterNode:
    """
    Main prompt generation node for Wan 2.2, Flux, and Qwen models.
    Auto-detects service (Ollama/LM Studio) from model selection.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        model_list = fetch_available_models()
        
        return {
            "required": {
                "model_select": (model_list, {"default": model_list[0] if model_list else ""}),
                "target_model": (["wan2.2", "flux", "qwen"], {"default": "flux"}),
                "creativity_mode": (["precise", "balanced", "creative"], {"default": "balanced"}),
                "input_text": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "placeholder": "Describe your scene..."
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Elements to avoid (passed through)"
                }),
                "max_tokens": ("INT", {"default": 500, "min": 100, "max": 2000, "step": 50}),
                "unload_model": ("BOOLEAN", {"default": False, "label_on": "Unload After", "label_off": "Keep Loaded"}),
                "save_to_history": ("BOOLEAN", {"default": True, "label_on": "Save", "label_off": "Don't Save"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "full_context")
    FUNCTION = "generate_prompt"
    CATEGORY = "AI Prompt Crafter"
    
    def generate_prompt(self, model_select, target_model, creativity_mode, input_text, seed,
                        negative_prompt="", max_tokens=500, unload_model=False, save_to_history=True):
        
        if not input_text.strip():
            return ("", negative_prompt, "")
        
        # Auto-detect service from model selection
        service, model_name, base_url = parse_model_selection(model_select)
        
        if not model_name or model_name.startswith("No models"):
            raise ValueError("No valid model selected. Make sure Ollama or LM Studio is running.")
        
        # Build prompt and call LLM
        system_prompt = build_system_prompt(target_model, creativity_mode)
        temperature = CREATIVITY_CONFIGS[creativity_mode]['temperature']
        
        generated_text = call_llm(
            service=service,
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=input_text,
            temperature=temperature,
            max_tokens=max_tokens,
            unload_after=unload_model
        )
        
        # Context for debugging
        full_context = json.dumps({
            "input": input_text,
            "output": generated_text,
            "negative": negative_prompt,
            "target_model": target_model,
            "creativity_mode": creativity_mode,
            "llm_service": service,
            "llm_model": model_name
        }, indent=2)
        
        if save_to_history:
            add_to_history({
                "input": input_text,
                "output": generated_text,
                "negative_prompt": negative_prompt,
                "service": service,
                "model": model_name,
                "target_model": target_model,
                "creativity": creativity_mode
            })
        
        return (generated_text, negative_prompt, full_context)


class InspireMeNode:
    """
    Generates short prompt ideas from keywords.
    Auto-detects service from model selection.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        model_list = fetch_available_models()
        
        return {
            "required": {
                "model_select": (model_list, {"default": model_list[0] if model_list else ""}),
                "keywords": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Enter keywords (e.g., 'sunset beach romantic')"
                }),
                "target_model": (["wan2.2", "flux", "qwen"], {"default": "flux"}),
                "num_ideas": ("INT", {"default": 3, "min": 1, "max": 6}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "style_hint": (["any", "cinematic", "artistic", "photorealistic", "anime", "abstract"], {"default": "any"}),
                "unload_model": ("BOOLEAN", {"default": False, "label_on": "Unload After", "label_off": "Keep Loaded"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("all_ideas", "idea_1", "idea_2", "idea_3", "idea_4", "idea_5")
    FUNCTION = "inspire"
    CATEGORY = "AI Prompt Crafter"
    
    def inspire(self, model_select, keywords, target_model, num_ideas, seed, style_hint="any", unload_model=False):
        
        if not keywords.strip():
            return ("Enter some keywords.", "", "", "", "", "")
        
        service, model_name, base_url = parse_model_selection(model_select)
        
        if not model_name or model_name.startswith("No models"):
            raise ValueError("No valid model selected.")
        
        target_desc = {'wan2.2': 'video', 'flux': 'image', 'qwen': 'image'}.get(target_model, 'image')
        style_instruction = f" Each idea should have a {style_hint} feel." if style_hint != "any" else ""
        
        system_prompt = "You are a creative brainstorming assistant. Generate short, distinct scene concepts from keywords. Keep each idea brief (1-2 sentences max)."
        
        user_prompt = f"""Keywords: "{keywords}"

Generate {num_ideas} SHORT {target_desc} scene ideas.{style_instruction}

Rules:
- 1-2 sentences MAX per idea
- Make each distinctly different
- Number them 1., 2., 3.

Example:
1. A lone figure on a rainy neon street.
2. Abstract colors morphing into a face.
3. Timelapse of flowers blooming."""

        generated_text = call_llm(
            service=service,
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.85,
            max_tokens=500,
            unload_after=unload_model
        )
        
        # Parse ideas
        ideas = ["", "", "", "", ""]
        lines = [l.strip() for l in generated_text.split('\n') if l.strip()]
        for line in lines:
            for i in range(1, 6):
                if line.startswith(f'{i}.') or line.startswith(f'{i})'):
                    ideas[i-1] = line[2:].strip()
                    break
        
        return (generated_text, ideas[0], ideas[1], ideas[2], ideas[3], ideas[4])


class VideoSequenceNode:
    """
    Generate sequential prompts for multi-clip video workflows.
    Auto-detects service from model selection.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        model_list = fetch_available_models()
        
        return {
            "required": {
                "model_select": (model_list, {"default": model_list[0] if model_list else ""}),
                "concept": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Describe your video concept..."
                }),
                "num_segments": (["2", "3", "4", "5", "6"], {"default": "4"}),
                "segment_duration": (["3sec", "5sec", "8sec", "10sec"], {"default": "5sec"}),
                "transition_style": (["smooth_continuous", "scene_progression", "time_lapse", "emotional_arc", "action_sequence"], {"default": "smooth_continuous"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "creativity_mode": (["precise", "balanced", "creative"], {"default": "balanced"}),
                "camera_style": (["static", "slow_pan", "tracking", "dynamic", "mixed"], {"default": "mixed"}),
                "unload_model": ("BOOLEAN", {"default": False, "label_on": "Unload After", "label_off": "Keep Loaded"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("all_segments", "segment_1", "segment_2", "segment_3", "segment_4", "segment_5", "segment_6")
    FUNCTION = "generate_sequence"
    CATEGORY = "AI Prompt Crafter"
    
    def generate_sequence(self, model_select, concept, num_segments, segment_duration,
                          transition_style, seed, creativity_mode="balanced", camera_style="mixed", unload_model=False):
        
        if not concept.strip():
            return ("Enter a video concept.", "", "", "", "", "", "")
        
        service, model_name, base_url = parse_model_selection(model_select)
        
        if not model_name or model_name.startswith("No models"):
            raise ValueError("No valid model selected.")
        
        num_segs = int(num_segments)
        duration = segment_duration.replace("sec", " seconds")
        
        transition_instructions = {
            "smooth_continuous": "Flow seamlessly between segments. Ending of one = beginning of next.",
            "scene_progression": "Progress through different but related scenes.",
            "time_lapse": "Show passage of time (morning→night, seasons, etc.).",
            "emotional_arc": "Build emotional narrative across segments.",
            "action_sequence": "Escalating action with dynamic energy."
        }
        
        camera_instructions = {
            "static": "Static camera.",
            "slow_pan": "Slow pans and tilts.",
            "tracking": "Tracking shots following subject.",
            "dynamic": "Dynamic, energetic movements.",
            "mixed": "Vary movements per segment."
        }
        
        temperature = CREATIVITY_CONFIGS.get(creativity_mode, CREATIVITY_CONFIGS['balanced'])['temperature']
        
        system_prompt = """Expert cinematographer for Wan 2.2 video generation. Break concepts into sequential segments where LAST FRAME of each matches FIRST FRAME of next. Output only numbered prompts."""
        
        user_prompt = f"""Concept: "{concept}"
Segments: {num_segs} x {duration}
Transition: {transition_instructions[transition_style]}
Camera: {camera_instructions[camera_style]}

For each segment include: subject, action, camera, lighting, key visuals.
Format: SEGMENT 1: [prompt]"""

        generated_text = call_llm(
            service=service,
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=1500,
            unload_after=unload_model
        )
        
        # Parse segments
        segments = ["", "", "", "", "", ""]
        for i in range(1, 7):
            patterns = [
                rf'SEGMENT\s*{i}\s*[:\-]\s*(.*?)(?=SEGMENT\s*{i+1}|$)',
                rf'{i}\.\s*(.*?)(?={i+1}\.|$)',
            ]
            for pattern in patterns:
                match = re.search(pattern, generated_text, re.IGNORECASE | re.DOTALL)
                if match:
                    segments[i-1] = match.group(1).strip()
                    break
        
        return (generated_text, segments[0], segments[1], segments[2], segments[3], segments[4], segments[5])


class PromptHistoryLoadNode:
    """Load a prompt from history."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "load_by": (["latest", "index", "search"], {"default": "latest"}),
            },
            "optional": {
                "index": ("INT", {"default": 0, "min": 0, "max": 99}),
                "search_term": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "original_input", "metadata")
    FUNCTION = "load"
    CATEGORY = "AI Prompt Crafter"
    
    def load(self, load_by, index=0, search_term=""):
        history = load_history()
        if not history:
            return ("", "", "", "No history found")
        
        entry = None
        if load_by == "latest":
            entry = history[0]
        elif load_by == "index" and index < len(history):
            entry = history[index]
        elif load_by == "search":
            for h in history:
                if search_term.lower() in f"{h.get('input', '')} {h.get('output', '')}".lower():
                    entry = h
                    break
        
        if entry:
            return (
                entry.get("output", ""),
                entry.get("negative_prompt", ""),
                entry.get("input", ""),
                json.dumps({k: entry.get(k, "") for k in ["timestamp", "service", "model", "target_model"]}, indent=2)
            )
        return ("", "", "", "Entry not found")


class PromptCombinerNode:
    """Combine multiple text strings."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_1": ("STRING", {"default": "", "forceInput": True}),
                "separator": (["comma", "newline", "space", "period"], {"default": "comma"}),
            },
            "optional": {
                "text_2": ("STRING", {"default": "", "forceInput": True}),
                "text_3": ("STRING", {"default": "", "forceInput": True}),
                "text_4": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined_text",)
    FUNCTION = "combine"
    CATEGORY = "AI Prompt Crafter"
    
    def combine(self, text_1, separator, text_2="", text_3="", text_4=""):
        sep_map = {"comma": ", ", "newline": "\n", "space": " ", "period": ". "}
        texts = [t.strip() for t in [text_1, text_2, text_3, text_4] if t.strip()]
        return (sep_map.get(separator, ", ").join(texts),)


class PromptStylerNode:
    """Apply style modifiers to a prompt."""
    
    STYLE_PRESETS = {
        "none": {"prefix": "", "suffix": ""},
        "cinematic": {"prefix": "Cinematic shot, ", "suffix": ", dramatic lighting, film grain"},
        "anime": {"prefix": "Anime style, ", "suffix": ", vibrant colors, cel shading"},
        "photorealistic": {"prefix": "Photorealistic, ", "suffix": ", 8K UHD, highly detailed"},
        "cyberpunk": {"prefix": "Cyberpunk aesthetic, ", "suffix": ", neon lights, rain, holographic"},
        "fantasy": {"prefix": "Fantasy art, ", "suffix": ", magical atmosphere, ethereal lighting"},
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "forceInput": True}),
                "style": (list(cls.STYLE_PRESETS.keys()), {"default": "none"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("styled_prompt",)
    FUNCTION = "style"
    CATEGORY = "AI Prompt Crafter"
    
    def style(self, prompt, style):
        if not prompt.strip():
            return (prompt,)
        preset = self.STYLE_PRESETS.get(style, self.STYLE_PRESETS["none"])
        return (f"{preset['prefix']}{prompt}{preset['suffix']}".strip(),)


class NegativePromptGeneratorNode:
    """Generate negative prompts from presets."""
    
    NEGATIVE_PRESETS = {
        "general": "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark",
        "photorealistic": "cartoon, anime, illustration, painting, CGI, 3D render",
        "anime": "photorealistic, photograph, 3D, hyperrealistic, western style",
        "video": "static, still image, frozen, no motion, choppy, low fps, artifacts",
        "none": "",
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(cls.NEGATIVE_PRESETS.keys()), {"default": "general"}),
            },
            "optional": {
                "additional": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("negative_prompt",)
    FUNCTION = "generate"
    CATEGORY = "AI Prompt Crafter"
    
    def generate(self, preset, additional=""):
        parts = [p for p in [self.NEGATIVE_PRESETS.get(preset, ""), additional.strip()] if p]
        return (", ".join(parts),)


# ============================================================================
# NODE MAPPINGS
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "WanPromptCrafterNode": WanPromptCrafterNode,
    "InspireMeNode": InspireMeNode,
    "VideoSequenceNode": VideoSequenceNode,
    "PromptHistoryLoadNode": PromptHistoryLoadNode,
    "PromptCombinerNode": PromptCombinerNode,
    "PromptStylerNode": PromptStylerNode,
    "NegativePromptGeneratorNode": NegativePromptGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanPromptCrafterNode": "🎬 Prompt Crafter",
    "InspireMeNode": "✨ Inspire Me",
    "VideoSequenceNode": "🎞️ Video Sequence",
    "PromptHistoryLoadNode": "📂 Load History",
    "PromptCombinerNode": "🔗 Combine Prompts",
    "PromptStylerNode": "🎨 Style Prompt",
    "NegativePromptGeneratorNode": "⛔ Negative Prompt",
}
