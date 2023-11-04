from anthropic import Anthropic
import os

def get_anthropic():
    """Setup anthropic client"""
    api_key = os.getenv("CLAUDE_API_KEY")
    anthropic = Anthropic(api_key=api_key)

    return anthropic


def claude_call(llm_setup, prompt, model="claude-2", max_tokens = 300, **kwargs):
    """Call Claude API"""
    response = llm_setup.completions.create(
        model=model,
        max_tokens_to_sample=max_tokens,
        prompt=prompt,
    )
    return response.completion