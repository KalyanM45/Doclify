from dataclasses import dataclass

@dataclass
class CliConfig:
    MODEL_NAME: str = "gemini-2.5-flash"