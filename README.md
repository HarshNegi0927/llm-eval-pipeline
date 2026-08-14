# LLM Eval Pipeline — Model Regression Detection System

A CI/CD-style pipeline that tests an LLM-powered feature against a golden
dataset on every prompt change, catches quality regressions before they ship,
and alerts the team — the same discipline unit tests bring to regular code,
applied to prompts.

## Status
- [x] **Phase 1** — LLM feature under test, versioned prompts, typed interface contract
- [ ] Phase 2 — Golden dataset (50-100 hand-labeled test cases)
- [ ] Phase 3 — Evaluation engine (multi-dimensional scoring, regression diff)
- [ ] Phase 4 — Alerting + HTML diff reports (Slack)
- [ ] Phase 5 — CI/CD wiring (GitHub Actions)
- [ ] Phase 6 — Docker + demo polish

## The feature under test
A customer support email classifier: reads one email, returns a category
(`billing` / `technical` / `account` / `general`) plus a one-sentence summary.
This is deliberately simple — the point of this project isn't the feature,
it's the eval infrastructure wrapped around it.

## Project structure
```
llm-eval-pipeline/
├── prompts/            # versioned prompt YAML files — the "code" under CI
│   └── v1.yaml
├── src/
│   ├── models.py        # Pydantic interface contract (input/output types)
│   ├── prompt_loader.py # loads a PromptConfig from /prompts
│   ├── llm_client.py     # Groq API wrapper — only file that touches the SDK
│   └── classifier.py     # the feature under test
├── tests/
│   └── test_classifier.py  # mocked-LLM unit tests
├── scripts/
│   └── run_single_example.py  # manual smoke test with a real API key
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your Groq API key (console.groq.com — free tier)
```

## Run the tests (no API key needed — LLM call is mocked)
```bash
pytest -v
```

## Run a real end-to-end smoke test (needs a real API key in .env)
```bash
python scripts/run_single_example.py
```

## Design decisions
- **Prompt as a file, not a string in code.** Every prompt version lives in
  `/prompts/<version_id>.yaml` with its own timestamp and few-shot examples.
  This is what lets Phase 5's CI trigger watch "did `/prompts` change?" the
  same way it'd watch any source file.
- **Groq over OpenAI.** Free tier, fast inference, OpenAI-compatible-style
  JSON mode. Swappable later — `llm_client.py` is the only file that would
  need to change.
- **Pydantic contract, not a dataclass.** The classifier's output is
  validated the instant it comes back from the LLM. A malformed response
  fails loudly here instead of silently corrupting downstream eval scores.
