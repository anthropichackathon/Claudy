from anthropic import Anthropic
import os
from typing import Union, Optional

def setup_anthropic() -> None:
    """Setup anthropic client"""
    api_key = os.getenv("CLAUDE_API_KEY")
    anthropic = Anthropic(api_key=api_key)

def claude_call()