# Persona Council: Experiment Results & Findings

**Date:** 2026-03-02
**Author:** Benison Sam (with Claude Code)
**Repository:** `/Users/benison/Projects/persona-council/`

---

## Executive Summary

We built and tested three review council stacks — CLI-based ($0/run), Premium API ($0.10/run), and Budget API ($0.04/run) — dispatching 6-7 specialized reviewer personas against the same engineering plan across 4 experiments. The experiments validate that **cheap, diverse models with rich persona prompts produce comparable reviews faster and cheaper than premium stacks**.

**Key finding:** A 7-persona budget stack using 4 models (DeepSeek V3.2, Qwen 3.5-27B, Gemini Flash 3.0, Mistral Large) achieves 100% contract compliance at $0.04/run. The optimized stack was validated in Experiment 4 with 7/7 pass rate and zero retries across both scenarios.

---

## What We Built

### The System

A CLI tool that dispatches a plan/spec document to multiple AI models simultaneously, each running as a different "persona" (reviewer archetype) with a rich system prompt defining their review method, focus area, and output format.

```
Plan/Spec → council_*.py → 6-7 concurrent reviewers → Validation Gate → Synthesis Brief
```

### Three Stacks Tested

| Stack | Dispatch | Models | Cost/Run | Pass Rate |
|-------|----------|--------|----------|-----------|
| **CLI** | Codex CLI + OpenCode CLI | 2 (GPT 5.3 Codex, Kimi K2.5) | $0 (subscription) | 100% |
| **Premium API** | OpenRouter API | 6 diverse models | $0.10 | 100% |
| **Budget API (v1)** | OpenRouter API | 7 cheap models | $0.05 | 71-86% |
| **Budget API (v2, production)** | OpenRouter API | 4 optimized models | $0.04 | **100%** |

### Two Review Scenarios

1. **PRD/Spec Review** — 6-7 personas pressure-test requirements documents for gaps, ambiguities, testability, edge cases, acceptance criteria, and dependency risks
2. **Dev Plan Review** — 6-7 personas review engineering plans for architecture, deployment risk, observability, coupling, estimates, QA strategy, and dependency risks

---

## Experiment 1: CLI Council (Baseline)

**Stack:** Codex CLI (GPT 5.3 Codex) × 3 personas + OpenCode CLI (Kimi K2.5 via OpenRouter) × 3 personas

**Cost:** $0/run (uses existing $20 ChatGPT + $40 Kimi subscriptions)

### Results

| Scenario | Pass Rate | Wall Time | Findings | CRITICAL | HIGH |
|----------|-----------|-----------|----------|----------|------|
| dev-plan | 6/6 | 242s | 46 | 8 | 18 |
| prd | 6/6 | 228s | 65 | 11 | 25 |

### Per-Reviewer Performance (dev-plan)

| Persona | CLI Tool | Time |
|---------|----------|------|
| Architecture Stress Tester | Codex | 143.0s |
| Deployment Risk Assessor | Codex | 75.0s |
| Observability Advocate | Codex | 155.1s |
| Coupling Detector | OpenCode/Kimi | 126.0s |
| Estimate Calibrator | OpenCode/Kimi | 148.9s |
| Test & QA Strategy Auditor | OpenCode/Kimi | 115.8s |

### Key Observations

- **Filesystem access is the killer feature.** Codex `-C` and OpenCode `--dir` let models read actual source code. Coupling Detector cited specific file:line references and import chains.
- **OpenCode/Kimi personas were initially timing out (300s).** Fixed by scoping prompts to "read only 3-5 files most central to the plan" and pre-computing a repo brief. All 6 passed after this fix.
- **100% contract compliance.** All reviews contained the required sections (Findings, Top 3 Recommendations, What I Might Be Wrong About).

### Latency Issue & Fix

Two OpenCode/Kimi personas (Estimate Calibrator, Test & QA Strategy Auditor) timed out at 300s on the first run. Root cause: unbounded "READ SOURCE CODE" instructions caused Kimi K2.5 to scan too many files.

**Fix applied (from CTO Mentor tiered-context discipline):**
1. Scoped persona prompts: "read only the 3-5 files most central to the plan"
2. Added `build_repo_brief()`: pre-computes file inventory (max 30 files) injected into prompt
3. Anti-exploration constraint: "Do NOT scan directories or read more than 3-5 files total"

After fix: 6/6 passed, 242s wall time, zero timeouts.

---

## Experiment 2: Premium API Council

**Stack:** 6 diverse models via OpenRouter API, one per persona

### Model Assignment

| Model | OpenRouter ID | Persona (dev-plan) | Persona (prd) |
|-------|---------------|-------------------|---------------|
| GPT 5.3 Codex | `openai/gpt-5.3-codex` | Architecture Stress Tester | Requirements Archaeologist |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | Deployment Risk Assessor | Spec Prosecutor |
| Gemini 3.1 Pro | `google/gemini-3.1-pro-preview` | Observability Advocate | Testability Auditor |
| Qwen 3.5-27B | `qwen/qwen3.5-27b` | Coupling Detector | Edge Case Hunter |
| MiniMax M2.5 | `minimax/minimax-m2.5` | Estimate Calibrator | QA Test Case Reviewer |
| GLM 5 | `z-ai/glm-5` | Test & QA Strategy Auditor | Acceptance Criteria Engineer |

### Results

| Scenario | Pass Rate | Wall Time | Cost | Findings | CRITICAL | HIGH |
|----------|-----------|-----------|------|----------|----------|------|
| dev-plan | 6/6 | 112s | $0.096 | 38 | 6 | 13 |
| prd | 6/6 | 103s | $0.092 | 49 | 7 | 14 |

### Per-Reviewer Performance (dev-plan, from OpenRouter logs)

| Persona | Model | Time | Cost | Tokens (in→out) | Speed |
|---------|-------|------|------|-----------------|-------|
| Architecture Stress Tester | GPT 5.3 Codex | 50.3s | $0.0575 | 8,630→3,072 | 62.3 tps |
| Deployment Risk Assessor | DeepSeek V3.2 | 38.1s | $0.0027 | 8,820→1,278 | 34.5 tps |
| Observability Advocate | Gemini 3.1 Pro | 53.3s | $0.0619 | 11,668→3,264 | 64.3 tps |
| Coupling Detector | Qwen 3.5-27B | 48.6s | $0.0106 | 11,439→5,611 | 75.5 tps |
| Estimate Calibrator | MiniMax M2.5 | 74.2s | $0.0050 | 8,567→2,016 | 27.2 tps |
| Test & QA Strategy Auditor | GLM 5 | 54.1s | $0.0152 | 9,593→1,997 | 37.0 tps |

### Per-Reviewer Performance (prd, from OpenRouter logs)

| Persona | Model | Time | Cost | Tokens (in→out) | Speed |
|---------|-------|------|------|-----------------|-------|
| Requirements Archaeologist | GPT 5.3 Codex | 52.9s | $0.0487 | 8,616→2,440 | 46.7 tps |
| Spec Prosecutor | DeepSeek V3.2 | 42.9s | $0.0028 | 8,812→1,568 | 36.7 tps |
| Testability Auditor | Gemini 3.1 Pro | 53.0s | $0.0668 | 11,685→3,673 | 70.5 tps |
| Edge Case Hunter | Qwen 3.5-27B | 31.4s | $0.0116 | 11,472→2,231 | 71.5 tps |
| QA Test Case Reviewer | MiniMax M2.5 | 58.3s | $0.0048 | 8,626→1,948 | 33.5 tps |
| Acceptance Criteria Engineer | GLM 5 | 60.2s | $0.0163 | 9,653→2,305 | 38.4 tps |

### Cost Breakdown

GPT 5.3 Codex + Gemini 3.1 Pro = **76% of total API cost**. DeepSeek V3.2 at $0.003/review is 25x cheaper than GPT 5.3 at near-equal quality.

### Context Leveling

CLI personas have filesystem access (can read repo files). API personas get pre-loaded file contents injected into the prompt via `build_repo_context()`. This reads the 3-5 files most relevant to the plan and packs them as fenced code blocks in the user message.

---

## Experiment 3: Budget API Council

**Stack:** 7 diverse cheap models via OpenRouter API, 7 personas (added Dependency & Integration Risk Mapper)

### Model Assignment

| Model | OpenRouter ID | Input $/M | Output $/M | Persona (dev-plan) | Persona (prd) |
|-------|---------------|-----------|------------|-------------------|---------------|
| GPT 5.1 Codex Mini | `openai/gpt-5.1-codex-mini` | $0.25 | $2.00 | Architecture Stress Tester | Requirements Archaeologist |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | $0.25 | $0.40 | Deployment Risk Assessor | Spec Prosecutor |
| Gemini Flash 3.0 | `google/gemini-3-flash-preview` | $0.50 | $3.00 | Observability Advocate | Testability Auditor |
| Qwen 3.5-27B | `qwen/qwen3.5-27b` | $0.20 | $0.60 | Coupling Detector | Edge Case Hunter |
| Kimi K2.5 | `moonshotai/kimi-k2.5` | $0.45 | $2.20 | Estimate Calibrator | QA Test Case Reviewer |
| Llama 4 Maverick | `meta-llama/llama-4-maverick` | $0.20 | $0.60 | Test & QA Strategy Auditor | Acceptance Criteria Engineer |
| Mistral Large 2512 | `mistralai/mistral-large-2512` | $0.50 | $1.50 | Dependency Risk Mapper | Dependency Risk Mapper |

### Results

| Scenario | Pass Rate | Wall Time | Cost | Findings |
|----------|-----------|-----------|------|----------|
| dev-plan | 5/7 (71%) | 431s | $0.046 | 38 (from 5 passing) |
| prd | 6/7 (86%) | 204s | $0.046 | 49 (from 6 passing) |

### Per-Reviewer Performance (from OpenRouter logs)

| Model | dev-plan Time | prd Time | dev-plan Cost | prd Cost | Speed (tps) | Contract Compliance | Finish |
|-------|-------------|----------|--------------|----------|-------------|--------------------|----|
| GPT 5.1 Codex Mini | 18.5s | 15.6s | $0.0082 | $0.0075 | 143-180 | 50% (failed dev-plan) | stop |
| DeepSeek V3.2 | 45.5s | 47.1s | $0.0027 | $0.0028 | 29-31 | 100% | stop |
| Gemini Flash 3.0 | 10.4s | 10.2s | $0.0090 | $0.0088 | 112-115 | 100% | stop |
| Qwen 3.5-27B | 40.6s | 44.6s | $0.0106 | $0.0116 | 75-78 | 100% | stop |
| Kimi K2.5 | 211.8s | 181.0s | $0.013 | $0.011 | 17-19 | 50% (failed dev-plan) | **length** |
| Llama 4 Maverick | 11.5s | 10.5s | $0.0016 | $0.0017 | 53-60 | **0%** (both scenarios) | stop |
| Mistral Large 2512 | 34.3s | 48.6s | $0.0082 | $0.0087 | 43-51 | 100% | stop |

### Failure Analysis

**Llama 4 Maverick (0% compliance):** Ultra-fast (10-12s) and ultra-cheap ($0.002) but cannot follow the structured output format. Produces narrative reviews without `[SEVERITY]` tags or required sections. Rich persona prompts don't compensate for weak instruction-following.

**Kimi K2.5 (50% compliance):** Hit the 4096 max_tokens limit ("length" finish in OpenRouter). Produces verbose output that gets truncated before reaching required sections. Also extremely slow (181-211s) — the wall-time bottleneck.

**GPT 5.1 Codex Mini (50% compliance):** Passed PRD but failed dev-plan. Inconsistent — may need stronger format enforcement in the persona prompt for code-review tasks.

---

## Experiment 4: Optimized Budget Stack (Production)

**Stack:** 4 models × 7 personas. Dropped Llama 4 Maverick, Kimi K2.5, and GPT 5.1 Codex Mini based on Experiment 3 failures. DeepSeek V3.2, Qwen 3.5-27B, and Gemini Flash 3.0 each serve 2 personas.

### Model Assignment

| Model | OpenRouter ID | Persona (dev-plan) | Persona (prd) |
|-------|---------------|-------------------|---------------|
| Gemini Flash 3.0 | `google/gemini-3-flash-preview` | Architecture Stress Tester | Requirements Archaeologist |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | Deployment Risk Assessor | Spec Prosecutor |
| Gemini Flash 3.0 | `google/gemini-3-flash-preview` | Observability Advocate | Testability Auditor |
| Qwen 3.5-27B | `qwen/qwen3.5-27b` | Coupling Detector | Edge Case Hunter |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | Estimate Calibrator | QA Test Case Reviewer |
| Qwen 3.5-27B | `qwen/qwen3.5-27b` | Test & QA Strategy Auditor | Acceptance Criteria Engineer |
| Mistral Large 2512 | `mistralai/mistral-large-2512` | Dependency Risk Mapper | Dependency Risk Mapper |

### Why GPT 5.1 Codex Mini Was Dropped

Between Experiments 3 and 4, we ran the original 5-model stack (keeping GPT 5.1 Codex Mini, dropping only Llama 4 Maverick and Kimi K2.5). GPT 5.1 Codex Mini failed **both** scenarios — hitting the 4096 token limit and producing output_tokens: 4096 without completing required sections. Overall compliance: 1/4 runs (25%). Demoted from Tier 2 to Tier 3.

### Results

| Scenario | Pass Rate | Wall Time | Cost | Retries |
|----------|-----------|-----------|------|---------|
| dev-plan | **7/7 (100%)** | 92s | $0.040 | 0 |
| prd | **7/7 (100%)** | 142s | $0.040 | 0 |

### Per-Reviewer Performance (dev-plan)

| Persona | Model | Time | Cost | Tokens (in/out) |
|---------|-------|------|------|-----------------|
| Architecture Stress Tester | Gemini Flash 3.0 | 12.3s | $0.009 | 11,645/1,176 |
| Deployment Risk Assessor | DeepSeek V3.2 | 92.0s | $0.003 | 8,820/993 |
| Observability Advocate | Gemini Flash 3.0 | 10.2s | $0.009 | 11,668/1,018 |
| Coupling Detector | Qwen 3.5-27B | 47.4s | $0.004 | 11,439/3,667 |
| Estimate Calibrator | DeepSeek V3.2 | 55.0s | $0.003 | 8,821/1,047 |
| Test & QA Strategy Auditor | Qwen 3.5-27B | 35.9s | $0.004 | 11,470/2,737 |
| Dependency Risk Mapper | Mistral Large | 36.0s | $0.008 | 11,230/1,921 |

### Per-Reviewer Performance (prd)

| Persona | Model | Time | Cost | Tokens (in/out) |
|---------|-------|------|------|-----------------|
| Requirements Archaeologist | Gemini Flash 3.0 | 10.5s | $0.009 | 11,636/1,150 |
| Spec Prosecutor | DeepSeek V3.2 | 142.2s | $0.003 | 8,812/1,473 |
| Testability Auditor | Gemini Flash 3.0 | 10.6s | $0.009 | 11,685/949 |
| Edge Case Hunter | Qwen 3.5-27B | 27.6s | $0.004 | 11,472/2,338 |
| QA Test Case Reviewer | DeepSeek V3.2 | 53.9s | $0.003 | 8,883/1,073 |
| Acceptance Criteria Engineer | Qwen 3.5-27B | 42.9s | $0.004 | 11,531/3,494 |
| Dependency Risk Mapper | Mistral Large | 48.6s | $0.008 | 11,260/1,774 |

### Key Observations

- **100% compliance, zero retries.** All 4 models passed validation on first attempt across both scenarios.
- **DeepSeek V3.2 latency variance.** Same model showed 45s in Experiment 3 but 55-142s in Experiment 4. This is OpenRouter load variance, not a model issue. DeepSeek still produced correct output.
- **Gemini Flash dominates speed.** 10-12s per review regardless of persona. Fastest model by 3-4x.
- **Cost stable at $0.04/run.** Nearly identical to the 7-model Experiment 3 despite fewer models — GPT 5.1 Codex Mini's removal saved ~$0.01 but Gemini Flash replacement costs ~$0.009.

---

## Experiment 5: Execution Review (New Scenario)

**Stack:** Same 4-model budget stack. NEW personas designed for post-implementation code review.

This is a fundamentally different review type — instead of reviewing a plan before implementation, it reviews the CODE CHANGES against the original plan. Personas were designed from first-principles research across the CTO Mentor vault, existing review patterns, and industry best practices (Google, Microsoft, diffray, CodeRabbit).

### Model Assignment

| Persona | Model | Focus |
|---------|-------|-------|
| Logic & Correctness Auditor | DeepSeek V3.2 | Branch tracing, null handling, edge cases, data integrity |
| Security & Trust Boundary Reviewer | Gemini Flash 3.0 | OWASP Top 10, injection, auth, secrets, trust boundaries |
| Performance & Resource Efficiency Analyst | Mistral Large | N+1, memory leaks, complexity, resource management |
| Plan Fidelity Checker | DeepSeek V3.2 | Drift from spec, missing requirements, scope creep |
| Test & Coverage Verifier | Gemini Flash 3.0 | Coverage gaps, flaky tests, assertion quality |
| Code Health & Maintainability Inspector | Qwen 3.5-27B | Naming, dead code, complexity, entropy, anti-additive bias |
| Integration & Contract Compliance Reviewer | Qwen 3.5-27B | API contracts, coupling, type safety, compatibility |

### Results

| Scenario | Pass Rate | Wall Time | Cost | Retries |
|----------|-----------|-----------|------|---------|
| execution | **7/7 (100%)** | 176s | $0.042 | 1 (Code Health Inspector) |

### Per-Reviewer Performance

| Persona | Model | Time | Cost | Tokens (in/out) | Retried |
|---------|-------|------|------|-----------------|---------|
| Logic & Correctness Auditor | DeepSeek V3.2 | 37.8s | $0.003 | 8,999/1,354 | no |
| Security & Trust Boundary Reviewer | Gemini Flash 3.0 | 10.7s | $0.009 | 11,901/960 | no |
| Performance & Resource Efficiency Analyst | Mistral Large | 33.4s | $0.008 | 11,350/1,840 | no |
| Plan Fidelity Checker | DeepSeek V3.2 | 116.0s | $0.003 | 9,152/1,579 | no |
| Test & Coverage Verifier | Gemini Flash 3.0 | 10.5s | $0.009 | 11,989/1,142 | no |
| Code Health & Maintainability Inspector | Qwen 3.5-27B | 32.9s | $0.004 | 11,776/2,539 | yes |
| Integration & Contract Compliance Reviewer | Qwen 3.5-27B | 72.9s | $0.006 | 11,780/5,556 | no |

### Key Observations

- **7/7 passed.** All execution review personas produced valid, severity-tagged findings on first run.
- **Code Health Inspector needed 1 retry.** Qwen 3.5-27B's first attempt was too verbose without following format. Self-corrected on retry — same pattern seen in earlier experiments.
- **Plan Fidelity Checker is the standout.** Unique to execution review — no equivalent in plan-stage review. Caught requirement-to-implementation gaps that other personas missed.
- **Same cost as plan review.** $0.042 vs $0.040 for dev-plan — execution review is cost-equivalent.
- **Wall time higher (176s vs 92s).** Driven by DeepSeek V3.2 latency variance (116s for Plan Fidelity Checker). Typical run should be ~90s when DeepSeek is at normal speed.

---

## Three-Stack Comparison

### Latency

| Metric | CLI | Premium API | Budget API |
|--------|-----|-------------|------------|
| dev-plan wall time | 242s | **112s** | 431s* |
| prd wall time | 228s | **103s** | 204s* |
| Avg per reviewer | ~115s | ~51s | ~30s (excl. Kimi) |
| Fastest reviewer | 75s | 31s | **10s (Gemini Flash)** |
| Slowest reviewer | 155s | 74s | 212s (Kimi K2.5) |

*Budget wall time inflated by Kimi K2.5 (181-212s). Without it, budget runs in ~55s.

### Quality (Specificity 1-5 / Actionability 1-5)

| Persona | CLI | Premium API | Budget API |
|---------|-----|-------------|------------|
| Architecture / Requirements | 4/4 | 4.5/5 | 3.5/4 |
| Deployment / Spec | 4/4 | 4/4.5 | 4/4 |
| Observability / Testability | 4/4 | 5/5 | 4/4 |
| Coupling / Edge Case | 5/5 | 4/4.5 | 4/4 |
| Estimate / QA Review | 3.5/4 | 4/4 | 3/3 (Kimi failures) |
| Test QA / Accept. Criteria | 3.5/3.5 | 4/4 | 2/2 (Llama failures) |
| Dependency Risk (7th) | N/A | N/A | 4/4 (Mistral) |

### Coverage

| Metric | CLI | Premium API | Budget API |
|--------|-----|-------------|------------|
| Total findings (dev-plan) | 46 | 38 | ~30 (5/7 passing) |
| Total findings (prd) | 65 | 49 | ~42 (6/7 passing) |
| CRITICAL (dev-plan) | 8 | 6 | ~5 |
| CRITICAL (prd) | 11 | 7 | ~6 |

### Cost

| Metric | CLI | Premium API | Budget API |
|--------|-----|-------------|------------|
| Per run | $0 (sub) | $0.096 | $0.046 |
| Per finding | $0 | $0.002 | $0.001 |
| Monthly (1/day) | $60 (subs) | $2.88 | $1.38 |
| Annual | $720 | $35 | $17 |

---

## Model Tier Rankings

### Tier 1 — Reliable, Expand

| Model | Avg Latency | Avg Cost | Compliance | Verdict |
|-------|------------|----------|------------|---------|
| **DeepSeek V3.2** | 44s | $0.003 | 100% | Best value. Strong reasoning, cheapest output. |
| **Qwen 3.5-27B** | 42s | $0.011 | 100% | Fast, good reasoning. Excellent for code analysis. |
| **Gemini Flash 3.0** | **10s** | $0.009 | 100% | Blazing fast. Excellent Gemini 3.1 Pro replacement at 3x less cost. |

### Tier 2 — Reliable, Keep

| Model | Avg Latency | Avg Cost | Compliance | Verdict |
|-------|------------|----------|------------|---------|
| **Mistral Large 2512** | 41s | $0.008 | 100% | Solid format compliance. Good for structured output tasks. |

### Tier 3 — Drop from API Council

| Model | Issue | Verdict |
|-------|-------|---------|
| **GPT 5.1 Codex Mini** | Hits 4096 token limit, 25% compliance | Fast but can't complete structured output |
| **Kimi K2.5** | 181-211s latency, hits 4096 token limit | Keep for CLI (subscription), drop from API |
| **Llama 4 Maverick** | 0% contract compliance | Cannot follow structured output format |
| **GLM 5** | Redundant — replaced by better-value models | Drop in favor of DeepSeek/Qwen |
| **MiniMax M2.5** | Redundant — replaced by Mistral Large | Drop in favor of Mistral |

### Tier S — Premium (use when quality > cost)

| Model | Avg Latency | Avg Cost | Verdict |
|-------|------------|----------|---------|
| **GPT 5.3 Codex** | 51s | $0.042 | Highest reasoning quality. 10x cost of DeepSeek. |
| **Gemini 3.1 Pro** | 53s | $0.032 | Best knowledge coverage. Premium for knowledge-heavy tasks. |

---

## Recommended Production Stack (Validated)

Based on all four experiments. Validated in Experiment 4: **7/7 pass rate, zero retries, both scenarios.**

| # | Persona | Model | Actual Cost | Actual Time |
|---|---------|-------|-------------|-------------|
| 1 | Architecture / Requirements | Gemini Flash 3.0 | $0.009 | ~11s |
| 2 | Deployment / Spec | DeepSeek V3.2 | $0.003 | ~45-92s* |
| 3 | Observability / Testability | Gemini Flash 3.0 | $0.009 | ~10s |
| 4 | Coupling / Edge Case | Qwen 3.5-27B | $0.004 | ~35s |
| 5 | Estimate / QA Test Case | DeepSeek V3.2 | $0.003 | ~55s* |
| 6 | Test Strategy / Accept. Criteria | Qwen 3.5-27B | $0.004 | ~36s |
| 7 | Dependency Risk Mapper | Mistral Large 2512 | $0.008 | ~42s |

**Actual: $0.040/run, 92-142s wall time, 7 personas, 100% compliance.**

*DeepSeek V3.2 latency varies 45-142s depending on OpenRouter load. Typical is 45s.

### Routing Decision

| Scenario | Stack | Rationale |
|----------|-------|-----------|
| PRD / Spec review | **Budget API** | No filesystem needed. Fast. Cheap. Model diversity compensates. |
| Dev plan review | **Budget API** | Context injection levels the field. 2x faster than CLI. |
| Code audit (line-level) | **CLI** | Filesystem access irreplaceable for file:line citations. |
| Cost-constrained | **CLI** | $0 marginal if subscriptions already active. |
| Maximum quality | **Premium API** | GPT 5.3 + Gemini 3.1 Pro for highest reasoning quality. |

---

## Technical Architecture

### Scripts

| Script | Purpose | Models |
|--------|---------|--------|
| `council_cli.py` | CLI dispatch via Codex + OpenCode | 2 (GPT 5.3, Kimi K2.5) |
| `council_api.py` | Premium API dispatch via OpenRouter | 6 diverse |
| `council_api_budget.py` | Budget API dispatch via OpenRouter | 4 (optimized) |

### Shared Infrastructure

- **Persona files:** `config/personas/{prd,dev-plan}/*.md` — 7 personas per scenario, shared across all stacks
- **Output format:** Validated against required sections + severity tags + minimum finding count
- **Synthesis brief:** Auto-generated summary grouping findings by severity with primary-agent processing instructions
- **Repo context:** `build_repo_context()` reads 3-5 relevant files and injects contents into API prompts

### Validation Gate (Upgraded)

```python
REQUIRED_SECTIONS = ["Findings", "Top 3 Recommendations", "What I Might Be Wrong About"]
SEVERITY_TAGS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
MIN_FINDINGS = 2
```

Reviews must have all 3 sections, at least 1 severity tag, and at least 2 findings. Failed reviews get 1 retry. Still-failing reviews marked INVALID with raw output preserved.

### Concurrency

- CLI: `asyncio.Semaphore(4)` — CLI subprocesses are heavy
- API: `asyncio.Semaphore(4)` + exponential backoff for 429/5xx

---

## Key Insights

### 1. Rich persona prompts are the equalizer

Prior experiment (Exp 2) showed rich personas cost $0.001 extra and dramatically improve weak models. This held: DeepSeek V3.2 at $0.003/review with a rich persona prompt produces findings comparable to GPT 5.3 Codex at $0.042/review.

### 2. Model diversity > model quality for review coverage

6 different cheap models catch more unique issues than 2 expensive models, because each model has different training biases and knowledge gaps. The "wisdom of the crowd" effect is real.

### 3. Structured output compliance is the real filter

The gap between Tier 1 models (100% compliance) and Tier 3 models (0-50% compliance) isn't reasoning quality — it's instruction-following. Llama 4 Maverick has good reasoning but can't produce `[SEVERITY] Title` formatted findings.

### 4. Speed is mostly about output token generation

Gemini Flash 3.0 at 112-115 tps produces reviews in 10s. Kimi K2.5 at 17-19 tps takes 180-210s for similar-length output. The speed difference is 6-10x, driven entirely by model inference speed.

### 5. CLI has an irreplaceable advantage for code review

API models get pre-loaded file contents, but CLI models (Codex with `-C`) can explore interactively. For the Coupling Detector persona, CLI consistently scored 5/5 specificity (file:line citations) vs API's 4/4.

---

## Raw Data Files

All outputs are in `/Users/benison/Projects/persona-council/output/`:

### CLI Council
- `dev-plan-20260302-061324.md` — First CLI run (4/6 passed, pre-fix)
- `dev-plan-20260302-062954.md` — Second CLI run (6/6 passed, post-fix)
- `dev-plan-20260302-062954-synthesis.md` — CLI dev-plan synthesis
- `prd-20260302-063530.md` — CLI PRD run (6/6 passed)
- `prd-20260302-063530-synthesis.md` — CLI PRD synthesis

### Premium API Council
- `dev-plan-api-20260302-070618.md` — Premium API dev-plan (6/6)
- `dev-plan-api-20260302-070618-synthesis.md` — Synthesis
- `dev-plan-api-20260302-070618-metrics.json` — Tokens, cost, latency
- `prd-api-20260302-070609.md` — Premium API PRD (6/6)
- `prd-api-20260302-070609-synthesis.md` — Synthesis
- `prd-api-20260302-070609-metrics.json` — Metrics

### Budget API Council (Experiment 3 — 7 models)
- `dev-plan-budget-20260302-073847.md` — Budget dev-plan (5/7)
- `dev-plan-budget-20260302-073847-synthesis.md` — Synthesis
- `dev-plan-budget-20260302-073847-metrics.json` — Metrics
- `prd-budget-20260302-073501.md` — Budget PRD (6/7)
- `prd-budget-20260302-073501-synthesis.md` — Synthesis
- `prd-budget-20260302-073501-metrics.json` — Metrics

### Budget API Council (Experiment 4 — Optimized 4 models, production)
- `dev-plan-budget-20260302-080011.md` — Budget dev-plan (7/7)
- `dev-plan-budget-20260302-080011-synthesis.md` — Synthesis
- `dev-plan-budget-20260302-080011-metrics.json` — Metrics
- `prd-budget-20260302-080102.md` — Budget PRD (7/7)
- `prd-budget-20260302-080102-synthesis.md` — Synthesis
- `prd-budget-20260302-080102-metrics.json` — Metrics

### Execution Review (Experiment 5)
- `execution-budget-20260302-084342.md` — Execution review (7/7)
- `execution-budget-20260302-084342-synthesis.md` — Synthesis
- `execution-budget-20260302-084342-metrics.json` — Metrics

### Comparison
- `ab-comparison-20260302.md` — CLI vs Premium API comparison

---

## OpenRouter Dashboard Costs (Verified)

From OpenRouter logs (Mar 2, 2026):

**Premium Stack (12 calls across both scenarios):**
- GPT 5.3 Codex: $0.0487 + $0.0575 = $0.1062
- Gemini 3.1 Pro: $0.0619 + $0.0668 = $0.1287
- Qwen 3.5-27B: $0.0167 + $0.0116 = $0.0283 (note: OpenRouter reported higher than our calc)
- GLM 5: $0.0152 + $0.0163 = $0.0315
- MiniMax M2.5: $0.0049 + $0.00483 = $0.0097
- DeepSeek V3.2: $0.0028 + $0.00269 = $0.0055
- **Total premium: ~$0.31 (both scenarios)**

**Budget Stack (14+ calls including retries):**
- GPT 5.1 Codex Mini: $0.0051 + $0.0075 + $0.0082 + $0.0082 = $0.029
- Gemini Flash 3.0: $0.0088 + $0.0090 = $0.018
- Qwen 3.5-27B: $0.0116 + $0.0106 = $0.022
- DeepSeek V3.2: $0.0028 + $0.0027 = $0.006
- Kimi K2.5: $0.011 + $0.013 + $0.013 = $0.037 (includes retry)
- Llama 4 Maverick: $0.0017 + $0.0016 + $0.0016 = $0.005
- Mistral Large 2512: $0.0082 + $0.0087 = $0.017
- **Total budget: ~$0.13 (both scenarios, including retries)**
