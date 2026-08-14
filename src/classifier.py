"""The LLM feature under test: classify a customer support email and
summarize it in one sentence.

classify_email() is the single function the entire eval pipeline (Phase 2
onward) will call in a loop. The prompt is never hardcoded here — it's
always passed in as a PromptConfig, which is what makes this testable
across prompt versions.
"""
from .llm_client import call_llm_json
from .models import EmailClassificationOutput, PromptConfig


def build_user_prompt(email_text: str, prompt_config: PromptConfig) -> str:
    few_shot_block = ""
    for ex in prompt_config.few_shot_examples:
        few_shot_block += f"\nEmail: {ex.input}\nOutput: {ex.output.model_dump_json()}\n"

    instructions = (
        "Classify the email below into exactly one category: "
        "billing, technical, account, or general. "
        "Also write a one-sentence summary. "
        'Respond ONLY as JSON: {"category": "...", "summary": "..."}'
    )
    return f"{instructions}\n{few_shot_block}\nEmail: {email_text}\nOutput:"


def classify_email(
    email_text: str, prompt_config: PromptConfig
) -> EmailClassificationOutput:
    """Runs one email through the classifier feature and returns a validated,
    structured output. Raises a pydantic ValidationError if the LLM's JSON
    doesn't match the contract — that's a feature, not a bug, for Phase 3."""
    user_prompt = build_user_prompt(email_text, prompt_config)
    raw_output = call_llm_json(prompt_config.system_prompt, user_prompt)
    return EmailClassificationOutput(**raw_output)
