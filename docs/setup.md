# Setting Up Persona Council in Your Project

## What This Does

Adds a `/council-plan-review` slash command to your Claude Code project. When invoked, it dispatches your plan/spec to 7 specialized reviewer personas (4 AI models via OpenRouter), returning a severity-graded synthesis brief in ~60-90s for $0.04.

## Prerequisites

1. **OpenRouter API key** — sign up at [openrouter.ai](https://openrouter.ai), add credits ($5 minimum)
2. **httpx** — `pip install httpx`
3. **Clone the repo** (or it's already at `/Users/benison/Projects/persona-council/`)

```bash
git clone https://github.com/bennjph/persona-council.git
```

4. **Set your API key:**

```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Add the Slash Command

Create `.claude/commands/council-plan-review.md` in your project root:

```markdown
# /council-plan-review

## Purpose

Dispatch a plan or spec to the Persona Council for multi-persona review. 7 reviewer personas, 4 AI models, $0.04/run.

## Arguments

- `$ARGUMENTS` — path to the plan/spec file to review, optionally followed by scenario name (`dev-plan` or `prd`)

## Workflow

1. Parse `$ARGUMENTS` for the plan file path and scenario.
   - `dev-plan` for engineering plans, implementation plans, technical designs
   - `prd` for PRDs, specs, requirements, feature briefs
   - Default to `dev-plan` if not specified

2. Use the current working directory as the repo path.

3. Run the council:
   ```
   python3 /path/to/persona-council/council_api_budget.py \
     --plan <plan-file> \
     --scenario <scenario> \
     --repo <repo-path>
   ```

4. Read the synthesis file path from the script output. Read that file.

5. Process findings using the 5-step protocol in the synthesis brief:
   - **Validate** — Verify CRITICAL/HIGH findings against the plan
   - **Discredit** — Discard findings where reviewer lacked context
   - **Deduplicate** — Merge overlapping findings
   - **Prioritize** — Rank by implementation impact
   - **Act** — Recommend plan changes or document accepted risk

6. Present processed findings with council metadata (pass rate, wall time, cost).
```

**Important:** Update `/path/to/persona-council/` to the actual path where you cloned the repo.

## Usage

```
/council-plan-review path/to/my-plan.md dev-plan
/council-plan-review specs/feature-brief.md prd
```

## Scenarios

| Scenario | Use When |
|----------|----------|
| `dev-plan` | Engineering/implementation plans, technical designs |
| `prd` | PRDs, specs, requirements documents, feature briefs |

## What You Get

The council produces 3 files in `persona-council/output/`:

1. **Full review** — Raw reviews from all 7 personas with metadata
2. **Synthesis brief** — Findings grouped by severity with processing instructions
3. **Metrics JSON** — Latency, tokens, cost per reviewer

Your agent reads the synthesis brief and processes it — validating findings against your actual plan, discarding false positives, and recommending changes.

## Models & Cost

| Model | Cost/Review |
|-------|-------------|
| DeepSeek V3.2 (×2 personas) | $0.003 |
| Qwen 3.5-27B (×2 personas) | $0.004 |
| Gemini Flash 3.0 (×2 personas) | $0.009 |
| Mistral Large 2512 (×1 persona) | $0.008 |
| **Total per run** | **~$0.04** |

## Verify It Works

```bash
export OPENROUTER_API_KEY="your-key"
python3 /path/to/persona-council/council_api_budget.py \
  --plan /path/to/any-plan.md \
  --scenario dev-plan \
  --repo /path/to/your-project
```

Expected: `Done: 7/7 passed | ~90s wall time | $0.04`
