# Persona Council

**7 AI reviewers. 4 models. $0.04 per run.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)

I built this because my plans kept shipping with blind spots. One model catches architecture issues, another finds missing edge cases, a third spots deployment risks. No single reviewer covers everything. So I made a council — 7 specialized personas dispatched in parallel across 4 cheap models via OpenRouter. The whole thing runs in 60-90 seconds and costs less than a nickel.

The secret isn't the model. It's the prompt. DeepSeek V3.2 at $0.003/review with a rich persona prompt produces findings comparable to GPT 5.3 Codex at $0.042/review. That's 14x cheaper for the same quality. Rich prompts are the equalizer.

## Quick Start

```bash
pip install httpx
export OPENROUTER_API_KEY="your-key"

# Review an engineering plan
python3 council_api_budget.py --plan path/to/plan.md --scenario dev-plan --repo /path/to/project

# Review a PRD or spec
python3 council_api_budget.py --plan path/to/spec.md --scenario prd --repo /path/to/project

# Review code after implementation
python3 council_api_budget.py --plan path/to/plan.md --scenario execution --repo /path/to/project
```

Expected output: `Done: 7/7 passed | ~90s wall time | $0.04`

## How It Works

Your plan goes in. Seven structured reviews come out.

```
Plan/Spec → council_api_budget.py → 7 concurrent reviewers → Validation Gate → Synthesis Brief
```

Each persona gets a rich system prompt defining their review method, focus area, and required output format. Every review passes through a validation gate — required sections, severity tags, minimum 2 findings. No hand-waving allowed.

The synthesis brief feeds back to your primary agent (Claude, Codex, whatever) with a 5-step processing protocol:

1. **Validate** — Verify each CRITICAL/HIGH finding against the plan
2. **Discredit** — Discard findings where the reviewer lacked context
3. **Deduplicate** — Merge overlapping findings from different reviewers
4. **Prioritize** — Rank by implementation impact
5. **Act** — Fix the plan or document accepted risk

## Three Scenarios

| Scenario | Use When | Personas |
|----------|----------|----------|
| `dev-plan` | Engineering plans, technical designs | Architecture Stress Tester, Deployment Risk Assessor, Observability Advocate, Coupling Detector, Estimate Calibrator, Test & QA Strategy Auditor, Dependency Risk Mapper |
| `prd` | PRDs, specs, requirements documents | Requirements Archaeologist, Spec Prosecutor, Testability Auditor, Edge Case Hunter, QA Test Case Reviewer, Acceptance Criteria Engineer, Dependency Risk Mapper |
| `execution` | Post-implementation code review | Logic & Correctness Auditor, Security & Trust Boundary Reviewer, Performance Analyst, Plan Fidelity Checker, Test & Coverage Verifier, Code Health Inspector, Integration & Contract Reviewer |

## The Model Stack

Four models, seven personas. Tier 1 models each serve two personas.

| Model | Cost/Review | Speed | Personas |
|-------|-------------|-------|----------|
| DeepSeek V3.2 | $0.003 | ~45s | 2 |
| Qwen 3.5-27B | $0.004 | ~42s | 2 |
| Gemini Flash 3.0 | $0.009 | ~10s | 2 |
| Mistral Large 2512 | $0.008 | ~41s | 1 |
| **Total per run** | **~$0.04** | **~60-90s** | **7** |

All models accessed via [OpenRouter](https://openrouter.ai). Sign up, add $5 in credits, and you're running.

## What You Get

Each run produces three files in `output/`:

| File | Contents |
|------|----------|
| `{scenario}-budget-{timestamp}.md` | Raw reviews from all 7 personas with metadata |
| `{scenario}-budget-{timestamp}-synthesis.md` | Findings grouped by severity, processing instructions for your agent |
| `{scenario}-budget-{timestamp}-metrics.json` | Latency, tokens, and cost per reviewer |

The synthesis brief is the one that matters. Hand it to your primary agent and let the 5-step protocol do the filtering.

## Validated Across 5 Experiments

Built and stress-tested across 4 experiments comparing CLI, Premium API, and Budget API stacks against the same plans.

| Metric | CLI (2 models) | Premium API (6 models) | Budget API (4 models) |
|--------|----------------|------------------------|----------------------|
| Wall time | 235s | 108s | 55s |
| Cost/run | $0 (subscription) | $0.10 | $0.04 |
| Pass rate | 100% | 100% | 100% |
| Findings | 46-65 | 38-49 | 30-42 |

The production budget stack hit 100% contract compliance with zero retries. Full experiment documentation: [`docs/experiment-results.md`](docs/experiment-results.md)

## Setup in Your Project

Want to add `/council-plan-review` as a slash command in your Claude Code project? See [`docs/setup.md`](docs/setup.md) for the full walkthrough.

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).

Built by [Ben Joseph](https://benal.co).
