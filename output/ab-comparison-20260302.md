# Best-Stack Comparison: CLI Council vs API Council

**Date:** 2026-03-02
**Plan reviewed:** Plan 18 — Semantic Search with Ollama
**Repo:** CTO Mentor vault

---

## Latency

| Metric | CLI (Codex+Kimi) | API (6 models) | Delta |
|--------|-----------------|-----------------|-------|
| **dev-plan wall time** | 242.0s | 112.4s | **-54% (2.2x faster)** |
| **prd wall time** | 228.3s | 103.2s | **-55% (2.2x faster)** |
| **dev-plan avg/reviewer** | 127.3s | 53.1s | -58% |
| **prd avg/reviewer** | 104.5s | 49.8s | -52% |
| **dev-plan slowest** | 155.1s (Observability) | 74.2s (Estimate Cal.) | -52% |
| **dev-plan fastest** | 75.0s (Deployment) | 38.1s (Deployment) | -49% |
| **prd slowest** | 228.0s (Edge Case) | 60.2s (Accept. Criteria) | -74% |
| **prd fastest** | 64.8s (Req. Arch.) | 31.4s (Edge Case) | -52% |

**Verdict: API is consistently 2x+ faster.** CLI's slowest reviewer (228s) would be API's total wall time.

### Per-Reviewer Latency (dev-plan)

| Persona | CLI (s) | API (s) | API Model |
|---------|---------|---------|-----------|
| Architecture Stress Tester | 143.0 | 50.3 | gpt-5.3-codex |
| Deployment Risk Assessor | 75.0 | 38.1 | deepseek-v3.2 |
| Observability Advocate | 155.1 | 53.3 | gemini-3.1-pro |
| Coupling Detector | 126.0 | 48.6 | qwen-3.5-27b |
| Estimate Calibrator | 148.9 | 74.2 | minimax-m2.5 |
| Test & QA Strategy Auditor | 115.8 | 54.1 | glm-5 |

### Per-Reviewer Latency (prd)

| Persona | CLI (s) | API (s) | API Model |
|---------|---------|---------|-----------|
| Requirements Archaeologist | 64.8 | 52.9 | gpt-5.3-codex |
| Spec Prosecutor | 69.0 | 42.9 | deepseek-v3.2 |
| Testability Auditor | 82.6 | 53.0 | gemini-3.1-pro |
| Edge Case Hunter | 228.0 | 31.4 | qwen-3.5-27b |
| QA Test Case Reviewer | 77.9 | 58.3 | minimax-m2.5 |
| Acceptance Criteria Engineer | 118.0 | 60.2 | glm-5 |

---

## Coverage

| Metric | CLI dev-plan | API dev-plan | CLI prd | API prd |
|--------|-------------|-------------|---------|---------|
| **Total findings** | 46 | 38 | 65 | 49 |
| **CRITICAL** | 8 | 6 | 11 | 7 |
| **HIGH** | 18 | 13 | 25 | 14 |
| **MEDIUM** | 15 | 14 | 20 | 16 |
| **LOW** | 5 | 5 | 9 | 12 |

**CLI produces ~20-30% more findings.** This is partly explained by:
1. CLI uses 2 models (Codex + Kimi K2.5) with 3 personas each — both models generate findings for all personas, leading to more duplication
2. CLI has filesystem access, enabling code-level findings that API can't reach
3. Some CLI "extra" findings may be duplicates across personas (e.g. Deployment Risk Assessor flagging same cache issue twice in CLI)

---

## Cost

| Metric | CLI | API dev-plan | API prd |
|--------|-----|-------------|---------|
| **Per run** | $0 (subscription) | $0.0958 | $0.0916 |
| **Tokens in** | N/A | 58,717 | 58,864 |
| **Tokens out** | N/A | 17,238 | 14,165 |
| **Cost/finding** | $0 | $0.0025 | $0.0019 |
| **Subscription cost** | $60/mo (Codex $20 + Kimi $40) | Pay-per-use | Pay-per-use |

### API Cost Breakdown by Model (dev-plan)

| Model | Input Tokens | Output Tokens | Cost | % of Total |
|-------|-------------|---------------|------|-----------|
| gpt-5.3-codex | 8,630 | 3,072 | $0.0418 | 43.6% |
| gemini-3.1-pro | 11,668 | 3,264 | $0.0309 | 32.3% |
| glm-5 | 9,593 | 1,997 | $0.0088 | 9.2% |
| qwen-3.5-27b | 11,439 | 5,611 | $0.0057 | 5.9% |
| minimax-m2.5 | 8,567 | 2,016 | $0.0050 | 5.2% |
| deepseek-v3.2 | 8,820 | 1,278 | $0.0037 | 3.8% |

**GPT 5.3 Codex + Gemini 3.1 Pro = 76% of API cost.** DeepSeek V3.2 is 25x cheaper than GPT 5.3 Codex per run.

At ~$0.10/run, the API council costs ~$3/month at 1 run/day. CLI costs $60/month in subscriptions regardless of usage.

**Break-even: ~600 runs/month.** Below that, API is cheaper. Above that, CLI (if you'd use both subscriptions that heavily anyway).

---

## Quality (all 6 reviewers scored, both stacks)

### dev-plan Scenario

| Persona | CLI Specificity | API Specificity | CLI Actionability | API Actionability | Notes |
|---------|---------------|-----------------|-------------------|-------------------|----|
| Architecture Stress Tester | 4 | 4 | 5 | 5 | Both strong. CLI (Codex CLI) and API (Codex API) use same model family. |
| Deployment Risk Assessor | 4 | 4 | 4 | 4 | API (DeepSeek) matches CLI (Codex) quality. Tighter, less verbose. |
| Observability Advocate | 4 | 5 | 4 | 5 | API (Gemini 3.1 Pro) excels — structured golden signals, incident sim. |
| Coupling Detector | 5 | 4 | 5 | 4 | CLI wins — filesystem access gives file:line citations from actual code. |
| Estimate Calibrator | 3 | 4 | 4 | 4 | API (MiniMax) better structured. CLI (Kimi) timed out on first attempt. |
| Test & QA Strategy Auditor | 4 | 4 | 4 | 4 | Both solid. API (GLM 5) good contract compliance. |

**dev-plan avg:** CLI 4.0/4.3 | API 4.2/4.3

### prd Scenario

| Persona | CLI Specificity | API Specificity | CLI Actionability | API Actionability | Notes |
|---------|---------------|-----------------|-------------------|-------------------|----|
| Requirements Archaeologist | 4 | 5 | 4 | 5 | API (Codex) stronger — cites missing contract elements precisely. |
| Spec Prosecutor | 4 | 4 | 4 | 5 | API (DeepSeek) more actionable — specific fix patterns. |
| Testability Auditor | 4 | 5 | 4 | 5 | API (Gemini 3.1 Pro) standout — benchmark suite proposals. |
| Edge Case Hunter | 5 | 4 | 5 | 5 | CLI wins specificity (Kimi reads code), API wins actionability. |
| QA Test Case Reviewer | 3 | 4 | 4 | 4 | API (MiniMax) more structured. CLI (Kimi) less focused. |
| Acceptance Criteria Engineer | 3 | 4 | 3 | 4 | API (GLM 5) produces proper Given-When-Then. CLI (Kimi) vague. |

**prd avg:** CLI 3.8/4.0 | API 4.3/4.7

---

## Contract Compliance

| Metric | CLI dev-plan | API dev-plan | CLI prd | API prd |
|--------|-------------|-------------|---------|---------|
| Pass rate (first attempt) | 6/6 | 6/6 | 6/6 | 6/6 |
| Retries needed | 0 | 0 | 0 | 0 |
| Severity tags present | 6/6 | 6/6 | 6/6 | 6/6 |
| Min 2 findings | 6/6 | 6/6 | 6/6 | 6/6 |

Both stacks achieve 100% contract compliance with the upgraded validation gate.

---

## Model Performance Rankings (API only)

| Model | Avg Latency | Avg Cost | Quality Score | Best For |
|-------|------------|----------|--------------|----------|
| deepseek-v3.2 | 40.5s | $0.0038 | 4.0/4.5 | Best value. Strong reasoning, lowest cost. |
| qwen-3.5-27b | 40.0s | $0.0046 | 4.0/4.5 | Fast, good reasoning. Edge cases + coupling. |
| gpt-5.3-codex | 51.6s | $0.0393 | 4.5/5.0 | Highest quality. 10x cost vs DeepSeek. |
| gemini-3.1-pro | 53.2s | $0.0319 | 5.0/5.0 | Best overall quality. Knowledge-heavy tasks. |
| glm-5 | 57.2s | $0.0091 | 4.0/4.0 | Good value. Structured output. |
| minimax-m2.5 | 66.3s | $0.0050 | 4.0/4.0 | Reliable, mid-speed. Estimate/QA tasks. |

**Standouts:**
- **Gemini 3.1 Pro**: Best quality scores. Worth the premium for knowledge-intensive personas.
- **DeepSeek V3.2**: Best value. Near-top quality at 10x lower cost than GPT 5.3.
- **Qwen 3.5-27B**: Fastest average response. Good all-rounder.

---

## Summary

| Dimension | CLI | API | Winner |
|-----------|-----|-----|--------|
| **Latency** | 235s avg | 108s avg | **API (2.2x faster)** |
| **Finding Quality** | 3.9/4.2 avg | 4.3/4.5 avg | **API (model diversity)** |
| **Coverage (raw count)** | 56 avg | 44 avg | CLI (+27% more findings) |
| **Coverage (unique)** | ~35 est. | ~38 est. | **Roughly equal** |
| **Cost per run** | $0 marginal | ~$0.10 | CLI (if subscriptions used) |
| **Contract compliance** | 100% | 100% | Tie |
| **Code-level specificity** | 5/5 for code personas | 4/5 (no filesystem) | CLI (for code review) |

---

## Verdict

**API wins on speed and quality. CLI wins on code-grounded specificity and zero marginal cost.**

### Recommended Routing

| Scenario | Recommended Stack | Rationale |
|----------|------------------|-----------|
| **PRD / Spec review** | **API** | No filesystem needed. 2x faster. Higher quality from model diversity. $0.09/run is negligible. |
| **Dev plan review** | **API** | Context injection levels the field. 2x faster. Gemini 3.1 Pro + DeepSeek V3.2 standouts. |
| **Code audit (line-level)** | **CLI** | Filesystem access is irreplaceable for file:line citations. Keep Codex -C for code review. |
| **Cost-constrained** | **CLI** | $0 marginal if subscriptions active anyway. |

### Optimal Mixed Council (future)

Best of both: API for plan/spec personas + CLI for code-grounded personas.
- Positions 1-3 (reasoning-heavy): API (GPT 5.3, DeepSeek V3.2, Gemini 3.1 Pro)
- Positions 4-6 (code-grounded): CLI (Codex -C for filesystem access)
- Expected: ~90s wall time, ~$0.07/run, best quality from both stacks
