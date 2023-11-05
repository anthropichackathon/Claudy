import os

import app.src.utils.claude as claude
import app.src.utils.prompts as prompts
import app.src.utils.update as update


def run(user_input: str):
    bio_path = "data/bio/bio/BIO.xml"
    if os.path.exists(bio_path):
        return

    llm_setup = claude.get_anthropic()
    response = claude.claude_call(
        llm_setup,
        prompts.bio_prompt(user_input),
        max_tokens=10_000
    )
    # Update the bio
    update.bio_update(response)

    # Update the STM
    update.stm_update(response)
