# Setting Up Persona Council in Your Project

You're about to add a 7-persona review council to your Claude Code workflow. One slash command sends your plan or spec to 4 AI models running as specialized reviewers. You'll get a severity-graded synthesis brief back in ~60-90 seconds for about $0.04.

This guide gets you from zero to a working `/council-plan-review` command.

## Prerequisites

1. **OpenRouter API key** -- sign up at [openrouter.ai](https://openrouter.ai) and add credits ($5 minimum)
2. **httpx** -- `pip install httpx`
3. **Clone the repo:**

```bash
git clone https://github.com/bennjph/persona-council.git
```

4. **Set your API key:**

```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Add the Slash Command

Create `.claude/commands/council-plan-review.md` in your target project root (not in the persona-council repo itself). Copy-paste the entire block below:

````markdown
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
   python3 /absolute/path/to/persona-council/council_api_budget.py \
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
````

**Important:** Replace `/absolute/path/to/persona-council/` with the actual path where you cloned the repo.

## Usage

```
# Review a plan before implementation
/council-plan-review path/to/my-plan.md dev-plan
/council-plan-review specs/feature-brief.md prd

# Review code after implementation (against the original plan)
/council-execution-review path/to/original-plan.md
```

For execution review, create a second file at `.claude/commands/council-execution-review.md` -- same template but with `--scenario execution`. The 5-step protocol then focuses on code changes rather than plan changes.

## Scenarios

| Scenario | Use When | Command |
|----------|----------|---------|
| `dev-plan` | Engineering/implementation plans, technical designs | `/council-plan-review` |
| `prd` | PRDs, specs, requirements documents, feature briefs | `/council-plan-review` |
| `execution` | Post-implementation code review against the original plan | `/council-execution-review` |

## What You Get Back

The council produces 3 files in `persona-council/output/`:

1. **Full review** -- raw reviews from all 7 personas with metadata
2. **Synthesis brief** -- findings grouped by severity with processing instructions
3. **Metrics JSON** -- latency, tokens, cost per reviewer

Your agent reads the synthesis brief and processes it -- validating findings against your actual plan, discarding false positives, and recommending changes.

## Models and Cost

| Model | Cost/Review |
|-------|-------------|
| DeepSeek V3.2 (x2 personas) | $0.003 |
| Qwen 3.5-27B (x2 personas) | $0.004 |
| Gemini Flash 3.0 (x2 personas) | $0.009 |
| Mistral Large 2512 (x1 persona) | $0.008 |
| **Total per run** | **~$0.04** |

## Verify It Works

Run the council directly from your terminal to confirm everything's wired up:

```bash
export OPENROUTER_API_KEY="your-key"
python3 /absolute/path/to/persona-council/council_api_budget.py \
  --plan /path/to/any-plan.md \
  --scenario dev-plan \
  --repo /path/to/your-project
```

You should see output ending with something like:

```
Done: 7/7 passed | ~90s wall time | $0.04
```

If any personas fail, check your API key and that you have OpenRouter credits. The most common issue is an expired or unfunded key.
