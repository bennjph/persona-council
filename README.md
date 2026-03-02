# Persona Council

Multi-persona AI review system. Dispatches plans/specs/code to 7 specialized reviewer personas, each powered by a different AI model, producing a structured synthesis brief.

Three scenarios: plan review (`dev-plan`), spec review (`prd`), execution review (`execution`).

## Quick Start

```bash
export OPENROUTER_API_KEY="your-key"

# Review a plan before implementation
python3 council_api_budget.py --plan path/to/plan.md --scenario dev-plan --repo /path/to/project

# Review a PRD/spec
python3 council_api_budget.py --plan path/to/spec.md --scenario prd --repo /path/to/project

# Review code after implementation (against the original plan)
python3 council_api_budget.py --plan path/to/plan.md --scenario execution --repo /path/to/project
```

## Stacks

### Budget API (`council_api_budget.py`) — Recommended

4 models via OpenRouter, 7 personas. Optimized after Experiments 3-4 — dropped Llama 4 Maverick (0% compliance), Kimi K2.5 (too slow), GPT 5.1 Codex Mini (hits token limit). Tier 1 models each serve 2 personas.

| Model | OpenRouter ID | Cost/Review | Speed | Personas |
|-------|---------------|-------------|-------|----------|
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | $0.003 | 45s | 2 |
| Qwen 3.5-27B | `qwen/qwen3.5-27b` | $0.004 | 42s | 2 |
| Gemini Flash 3.0 | `google/gemini-3-flash-preview` | $0.009 | 10s | 2 |
| Mistral Large 2512 | `mistralai/mistral-large-2512` | $0.008 | 41s | 1 |

### Premium API (`council_api.py`)

6 premium models. Highest quality, 100% contract compliance.

| Model | Cost/Review | Speed |
|-------|-------------|-------|
| GPT 5.3 Codex | $0.042 | 51s |
| Gemini 3.1 Pro | $0.032 | 53s |
| DeepSeek V3.2 | $0.003 | 40s |
| Qwen 3.5-27B | $0.005 | 40s |
| MiniMax M2.5 | $0.005 | 66s |
| GLM 5 | $0.009 | 57s |

### CLI (`council_cli.py`)

2 models via CLI subscriptions. $0/run. Filesystem access for code-grounded reviews.

| Model | CLI Tool | Cost |
|-------|----------|------|
| GPT 5.3 Codex | `codex exec -C` | $0 (ChatGPT $20/mo) |
| Kimi K2.5 | `opencode run --dir` | $0 (Kimi $40/mo) |

## Scenarios

### `prd` — PRD & Spec Review (6-7 personas)

| Persona | Focus |
|---------|-------|
| Requirements Archaeologist | Missing requirements, implicit assumptions |
| Spec Prosecutor | Ambiguity, contradictions, boundary gaps |
| Testability Auditor | Requirement-to-test mapping, coverage |
| Edge Case Hunter | Failure modes, adversarial inputs |
| QA Test Case Reviewer | Test sufficiency, edge case coverage |
| Acceptance Criteria Engineer | Vague criteria → Given-When-Then |
| Dependency Risk Mapper* | External service assumptions, API contracts |

### `dev-plan` — Engineering Dev Plan Review (6-7 personas)

| Persona | Focus |
|---------|-------|
| Architecture Stress Tester | 10x scaling, SPOFs, anti-patterns |
| Deployment Risk Assessor | Rollback, blast radius, feature flags |
| Observability Advocate | Golden signals, logging, alerting |
| Coupling Detector | Import graphs, shared state, interfaces |
| Estimate Calibrator | Complexity vs estimates, unknowns budget |
| Test & QA Strategy Auditor | Test pyramid, CI, QA effort |
| Dependency Risk Mapper* | Third-party APIs, integration contracts |

*7th persona in budget stack only

### `execution` — Post-Implementation Execution Review (7 personas)

| Persona | Focus |
|---------|-------|
| Logic & Correctness Auditor | Branch tracing, null handling, edge cases, data integrity |
| Security & Trust Boundary Reviewer | OWASP Top 10, injection, auth, secrets, trust boundaries |
| Performance & Resource Efficiency Analyst | N+1 queries, memory leaks, complexity, resource management |
| Plan Fidelity Checker | Drift from spec, missing requirements, scope creep, unplanned additions |
| Test & Coverage Verifier | Coverage gaps, flaky tests, assertion quality, preservation properties |
| Code Health & Maintainability Inspector | Naming, dead code, complexity, entropy, anti-additive bias |
| Integration & Contract Compliance Reviewer | API contracts, coupling, type safety, backwards compatibility |

## Output

Each run produces 2-3 files in `output/`:

1. **Full review** (`{scenario}-{stack}-{timestamp}.md`) — Raw reviews from all personas with metadata
2. **Synthesis brief** (`{scenario}-{stack}-{timestamp}-synthesis.md`) — Findings grouped by severity, reviewer recommendations, processing instructions for primary agent
3. **Metrics** (`{scenario}-{stack}-{timestamp}-metrics.json`) — API stacks only. Latency, tokens, cost per reviewer.

### Synthesis Brief → Primary Agent

The synthesis brief is designed to be fed to a primary agent (Claude, etc.) with instructions:

1. **Validate** — Verify each CRITICAL/HIGH finding against the plan
2. **Discredit** — Discard findings where reviewer lacked context
3. **Deduplicate** — Merge overlapping findings from different reviewers
4. **Prioritize** — Rank by implementation impact
5. **Act** — Fix the plan or document accepted risk

## Architecture

- **Concurrency:** `asyncio.Semaphore(4)` for all stacks
- **Validation gate:** Required sections + severity tags + minimum 2 findings
- **Retry budget:** 1 retry for contract failures, 2 retries for transport errors (API)
- **Context injection:** API models get repo file contents pre-loaded in prompt. CLI models read files via filesystem tools.

## Experiment Results

Full experiment documentation: [`docs/experiment-results.md`](docs/experiment-results.md)

**Three-stack comparison (same plan, same personas):**

| Metric | CLI | Premium API | Budget API |
|--------|-----|-------------|------------|
| Wall time | 235s | 108s | 55s* |
| Cost/run | $0 | $0.10 | $0.04 |
| Pass rate | 100% | 100% | 71-86% |
| Findings | 46-65 | 38-49 | 30-42 |

*Budget wall time excluding Kimi K2.5 bottleneck

**Key finding:** Rich persona prompts are the equalizer. DeepSeek V3.2 at $0.003/review with a rich prompt produces findings comparable to GPT 5.3 Codex at $0.042/review.

## File Structure

```
persona-council/
  council_cli.py                    # CLI dispatcher
  council_api.py                    # Premium API dispatcher
  council_api_budget.py             # Budget API dispatcher
  config/
    personas/
      prd/                          # 7 PRD scenario personas
      dev-plan/                     # 7 dev-plan scenario personas
      execution/                    # 7 execution review personas
  output/                           # Generated reviews + synthesis + metrics
  docs/
    experiment-results.md           # Full experiment documentation
    setup.md                        # Setup guide for other projects
```
