from dataclasses import dataclass, field
from typing import Dict

@dataclass
class LiteLLMConfig:
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    MODEL_MAP: Dict[str, str] = field(default_factory=lambda: {
        "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "gemini": ["gemini-2.0-flash", "gemini-1.5-pro"],
        "anthropic": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
    })