"""Manual smoke test — run this after setting a real GROQ_API_KEY in .env to
confirm the classifier actually talks to the LLM correctly end to end.

Usage:
    python scripts/run_single_example.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import classify_email
from src.prompt_loader import load_prompt_config

if __name__ == "__main__":
    config = load_prompt_config("v1")
    sample_email = (
        "My account got locked after I tried logging in from a new phone. "
        "Please help me get back in, I have an urgent client call in an hour."
    )
    result = classify_email(sample_email, config)
    print(f"Category: {result.category}")
    print(f"Summary:  {result.summary}")
