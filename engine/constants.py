import os
from typing import Literal
from pathlib import Path

PROJ_DIR: str = str(Path(__file__).parent.parent.absolute())
IGNORE_INDEX = -100  # The default setting in CrossEntropyLoss

try:
    from .key import OPENAI_API_KEY, ANTHROPIC_API_KEY
except:
    print("Warning: No OpenAI or Anthropic keys found.")
    OPENAI_API_KEY = ''
    ANTHROPIC_API_KEY = ''


if 'DRY_RUN' in os.environ:
    DRY_RUN = bool(os.environ['DRY_RUN'])
else:
    DRY_RUN = False
print(f'DRY_RUN={DRY_RUN}')

# LLM configs
LLM_PROVIDER: Literal['gpt', 'claude', 'llama', 'ollama'] = 'ollama'
TEMPERATURE: float = 0.0
NUM_COMPLETIONS: int = 1
MAX_TOKENS: int = 4000

assert 0 <= TEMPERATURE <= 1, TEMPERATURE
if NUM_COMPLETIONS > 1:
    assert TEMPERATURE > 0, TEMPERATURE
