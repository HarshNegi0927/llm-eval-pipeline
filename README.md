# LLM Eval Pipeline — Model Regression Detection System

A CI/CD-style pipeline that tests an LLM-powered feature against a golden
dataset on every prompt change, catches quality regressions before they ship,
and alerts the team — the same discipline unit tests bring to regular code,
applied to prompts.

## Results (latest recorded run)

| Metric | Value |
|---|---|
| Pass rate | **90.6%** (77/85 cases) |
| Avg summary quality (LLM-as-judge) | 4.06 / 5 |
| Avg latency | 473 ms |
| Errors | 0 |

Category breakdown: account 100% · general 93.3% · technical 91.7% · billing 84%

Run `0823aecf`, prompt `v2`, `llama-3.1-8b-instant` via Groq — flat vs. the
previous `v2` run, no regressions. Three prompt versions (`v1` → `v3`) have
been iterated on so far, with 4 recorded eval runs in `eval_runs/` and a full
HTML report in `reports/`.

## Status
- [x] **Phase 1** — LLM feature under test, versioned prompts, typed interface contract
- [x] **Phase 2** — Golden dataset (85 cases — drafted, pending human review, see below)
- [x] **Phase 3** — Evaluation engine (async batching, multi-dimensional scoring, regression diff, statistical thresholds)
- [x] **Phase 4** — Alerting + HTML diff reports (Slack, drift detection)
- [x] **Phase 5** — CI/CD wiring (GitHub Actions, Docker)

## The feature under test
A customer support email classifier: reads one email, returns a category
(`billing` / `technical` / `account` / `general`) plus a one-sentence summary.
This is deliberately simple — the point of this project isn't the feature,
it's the eval infrastructure wrapped around it.

## Project structure
```
llm-eval-pipeline/
├── .github/workflows/
│   └── eval.yml               # CI: runs eval on every prompt-changing PR
├── prompts/                   # versioned prompt YAML — the "code" under CI
│   ├── v1.yaml
│   ├── v2.yaml
│   └── v3.yaml
├── golden_dataset/
│   └── v1.json                 # 85 test cases across 4 categories
├── eval_runs/                  # committed run history — CI diffs against this
├── reports/                    # self-contained HTML report per run
├── src/
│   ├── models.py                # Pydantic interface contract (input/output types)
│   ├── prompt_loader.py         # loads a PromptConfig from /prompts
│   ├── llm_client.py            # Groq API wrapper — only file that touches the SDK
│   ├── classifier.py            # the feature under test
│   ├── golden_dataset.py        # loads/validates the golden dataset
│   ├── judge.py                  # LLM-as-judge summary scoring
│   ├── eval_engine.py            # async batch runner, scoring orchestration
│   ├── comparison.py              # regression diff + statistical thresholds
│   ├── rate_limiter.py            # dual rolling-window limiter (req/min + tokens/min)
│   ├── report.py                   # HTML report generation
│   ├── slack_alert.py              # Slack webhook alerting
│   ├── run_store.py                # reads/writes eval_runs/*.json
│   └── git_utils.py                # diffs changed prompt files against a base branch
├── scripts/
│   ├── run_single_example.py     # manual smoke test with a real API key
│   ├── review_dataset.py          # interactive golden-dataset review
│   ├── run_eval.py                 # full local eval run
│   ├── ci_run_eval.py              # eval entrypoint used by GitHub Actions
│   ├── detect_changed_prompts.py   # diffs prompts/ against a base branch
│   └── show_failures.py             # prints failing cases from a saved run
├── tests/                      # 8 files, mocked-LLM unit tests
├── Dockerfile
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

## Golden dataset — human review checklist
`golden_dataset/v1.json` has 85 draft test cases (25 billing, 24 technical,
21 account, 15 general; 14 of them tagged `"difficulty": "edge"` — sarcasm,
typos, mixed-language, near-empty input, deliberately ambiguous twins, and
a few multi-symptom "hard" cases where two things are broken at once). These
were drafted, not hand-verified — **do this before treating it as ground
truth**:

```bash
python scripts/review_dataset.py
```

Read every case. For any you disagree with, edit `expected_category` /
`expected_summary` / `difficulty` directly in the JSON. Once you've
confirmed a case, set `"human_verified": true` on it. Add your own cases
too — the point of the golden set is that *you* trust every entry in it,
because the regression detection is only as honest as this file.

## Run a real eval (needs a real API key — makes ~170 live API calls)
```bash
python scripts/run_eval.py v1
```
First run has nothing to diff against and becomes your baseline. Edit
`prompts/v1.yaml` (or add a new version), run again, and you'll see a
pass-rate delta and any regressions/improvements vs. the last run.

**This takes several minutes on Groq's free tier — that's expected.**
Free tier caps at 30 requests/min AND 6,000 tokens/min, and this run makes
~170 calls. `src/rate_limiter.py` tracks both limits in a rolling window
and paces calls to stay under them; progress prints as each case finishes,
so gaps between lines mean the limiter is waiting, not that anything hung.
On a paid Developer tier, raise `MAX_REQUESTS_PER_MINUTE` /
`MAX_TOKENS_PER_MINUTE` in `.env` to go faster.

## How a case is scored
Every case is checked on two dimensions, not just category:
1. **Category match** — exact, binary.
2. **Summary quality** — an LLM-as-judge scores the candidate summary
   against the golden reference summary, 1-5.

A case only **passes** if the category matches AND the judge score is ≥4.
This is deliberate — a case that gets the category right but produces a
garbage summary should still count as a failure.

## Regression thresholds
Comparing a new run to the previous one: pass-rate drop ≥3% is a
`warning`, ≥8% is `critical` (both configurable in `src/comparison.py`).

## HTML reports + Slack alerts + drift detection
Every `scripts/run_eval.py` run also:
- Writes a self-contained HTML report to `reports/<run_id>.html` — scorecard,
  regression/improvement tables, and a pass-rate trend chart across all
  saved runs. Opens by double-clicking, no server needed.
- Checks for **slow drift**: compares the trailing 7-run average pass rate
  against the previous 7-run average, independent of any single run's diff.
  Needs 14+ saved runs before it can fire — with only a handful of runs so
  far it'll stay silent, and that's expected, not broken.
- Sends a Slack alert if `SLACK_WEBHOOK_URL` is set in `.env` (get one at
  https://api.slack.com/messaging/webhooks). Leave it blank to skip
  Slack — the pipeline works fully without it.

## CI/CD — GitHub Actions
`.github/workflows/eval.yml` triggers on every PR that touches `prompts/**`:
1. Detects which prompt version file(s) changed (`src/git_utils.py`, diffed
   against the PR's base branch).
2. Runs the full eval for each changed version (`scripts/ci_run_eval.py`),
   comparing each against the latest saved run.
3. Posts a comment on the PR with pass rate, category accuracy, and any
   regressions/improvements.
4. **Fails the check (blocking merge, if set as a required check) if any
   run comes back CRITICAL.**
5. Uploads the run JSON + HTML report as workflow artifacts.

**Required setup** — add these as repository secrets (Settings → Secrets
and variables → Actions → New repository secret):
- `GROQ_API_KEY`
- `SLACK_WEBHOOK_URL` (optional — leave unset to skip Slack from CI too)

**Why `eval_runs/` and `reports/` are committed to git, not ignored:**
CI runs in a fresh checkout every time — it has no memory of past runs
except what's actually in the repo. `get_latest_run()` reads from
`eval_runs/*.json`, so if that folder isn't committed, every CI run would
have nothing to diff against and "baseline" would never advance. Commit
your local eval runs (especially after a meaningful one) so CI compares
against real history, not nothing.

**To test the workflow:** push a new prompt version on a branch, open a PR
against `main`, and check the Actions tab + the PR's comments.

## Docker
```bash
docker build -t eval-pipeline .
docker run --rm -e GROQ_API_KEY=your_key_here eval-pipeline v2
```
The container's default command runs `v1`; pass a different version as the
final argument, as shown above.

## Design decisions
- **Prompt as a file, not a string in code.** Every prompt version lives in
  `/prompts/<version_id>.yaml` with its own timestamp and few-shot examples.
  This is what lets the CI trigger watch "did `/prompts` change?" the
  same way it'd watch any source file.
- **Groq over OpenAI.** Free tier, fast inference, OpenAI-compatible-style
  JSON mode. Swappable later — `llm_client.py` is the only file that would
  need to change.
- **Pydantic contract, not a dataclass.** The classifier's output is
  validated the instant it comes back from the LLM. A malformed response
  fails loudly here instead of silently corrupting downstream eval scores.
