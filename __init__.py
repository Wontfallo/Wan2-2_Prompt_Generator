"""
AI Prompt Crafter - ComfyUI Custom Nodes Package

A comprehensive set of nodes for generating AI prompts for:
- Wan 2.2 (Video generation)
- Flux (Image generation)
- Qwen (Image generation)

Using locally running LLMs via Ollama or LM Studio.
"""

from .nodes import (
    WanPromptCrafterNode,
    InspireMeNode,
    VideoSequenceNode,
    PromptHistoryLoadNode,
    PromptCombinerNode,
    PromptStylerNode,
    NegativePromptGeneratorNode,
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Version info
__version__ = "1.1.0"
__author__ = "AI Prompt Crafter"
