# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/7 completed | 200.8s | $0.0403

**Failed reviewers:** Architecture Stress Tester (invalid)

**Total findings:** 37 (CRITICAL: 6 | HIGH: 12 | MEDIUM: 12 | LOW: 7)

### CRITICAL

- **No rollback path for embedding cache corruption** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Missing Saturation Metric for Local Embedding Provider** — _Observability Advocate_ (gemini-3-flash)
- **`backup_before_write` function exists in lib but is not used anywhere** — _Coupling Detector_ (qwen-3.5-27b)
- **No Automated Tests for Semantic Search Implementation** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No CI Pipeline to Enforce Quality Gates** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Ollama API Contract Not Validated Against Documentation** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Semantic search deployment lacks a feature flag** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Blast radius of failed embedding call is uncontained** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Broken Trace Correlation in Hybrid Search** — _Observability Advocate_ (gemini-3-flash)
- **Silent Failure Mode in Cache Integrity** — _Observability Advocate_ (gemini-3-flash)
- **Global ROOT path creates hidden coupling across modules** — _Coupling Detector_ (qwen-3.5-27b)
- **Import statement split creates maintenance coupling** — _Coupling Detector_ (qwen-3.5-27b)
- **`search_semantic` interface is not versioned and couples callers to implementation** — _Coupling Detector_ (qwen-3.5-27b)
- **Single-number estimates without decomposition** — _Estimate Calibrator_ (deepseek-v3.2)
- **Test Environment Requires Manual Ollama Setup** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **QA Effort Not Estimated or Budgeted** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No Circuit Breaker or Timeout for Ollama API Calls** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache Corruption Risk Due to Non-Atomic Writes** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **No validation for embedding model output format** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Deployment sequence risks service interruption** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Missing Alert Thresholds for Similarity Scores** — _Observability Advocate_ (gemini-3-flash)
- **Cache file is shared mutable state with no concurrency protection** — _Coupling Detector_ (qwen-3.5-27b)
- **Ollama availability check creates temporal coupling on every search** — _Coupling Detector_ (qwen-3.5-27b)
- **Cache refresh logic assumes sequential file processing without error recovery** — _Coupling Detector_ (qwen-3.5-27b)
- **Plan lacks contingency for integration and discovery work** — _Estimate Calibrator_ (deepseek-v3.2)
- **Plan underestimates complexity of modifying `cto_context_lib.py`** — _Estimate Calibrator_ (deepseek-v3.2)
- **No Test Data Strategy for Cache Validation** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Regression Risk on Keyword Search Path** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No Fallback for Embedding Failures on Individual Files** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Integration Tests for Semantic Search Boundary** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Cache TTL configuration is not implemented** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Log Level Verbosity Risk** — _Observability Advocate_ (gemini-3-flash)
- **`SOURCE_WEIGHTS` global couples search ranking to hardcoded paths** — _Coupling Detector_ (qwen-3.5-27b)
- **Parallelism assumption is invalid** — _Estimate Calibrator_ (deepseek-v3.2)
- **External dependency risk is under-analyzed** — _Estimate Calibrator_ (deepseek-v3.2)
- **Cache File Format Not Versioned** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Hardcoded Model Name and Embedding Dimensions** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Deployment Risk Assessor** (deepseek-v3.2):
  1. **Implement atomic cache updates and a rollback mechanism** before deploying the cache system. This addresses the CRITICAL finding of no rollback and the HIGH finding of partial failure state. Use the existing `backup_before_write` pattern for the cache file.
  2. **Add a runtime feature flag for semantic search** to allow disabling the new functionality without a code rollback, addressing the HIGH risk of a flawed semantic implementation affecting all users.
  3. **Deploy library and CLI changes atomically** in a single operation to prevent broken intermediate states, as per the MEDIUM deployment sequence finding.

**Observability Advocate** (gemini-3-flash):
  1. **Implement Resource Guardrails**: Add a timeout and a "circuit breaker" to the Ollama API client in `cto_context_lib.py`. If the local model takes >2s to respond, the system must automatically trip to keyword-only mode for 5 minutes to prevent cascading latency.
  2. **Standardize Structured Logging**: Replace `print` statements in `cto_context_search.py` with structured JSON logging that includes a `correlation_id`, `duration_ms`, and `provider: ollama`. This is essential for identifying if search lag is caused by the model or the similarity math.
  3. **Define Confidence Floor**: Set a hard floor for semantic scores (e.g., 0.5). Any result below this should be filtered out before reaching the agent to prevent "semantic drift" where unrelated context is injected into the prompt.

**Coupling Detector** (qwen-3.5-27b):
  1. **Wire up `backup_before_write()` to cache refresh and learning modifications** — This directly addresses the "Shadow Restore Points" pattern from the Context+ learning that motivated this plan. Call it before `save_embedding_cache()` and any vault write operations.
  2. **Consolidate all imports to top of `cto_context_search.py`** — Move the conditional imports inside the `--refresh-cache` block to the top of the file. This makes dependencies explicit and prevents future import-related bugs.
  3. **Add file locking to cache read/write operations** — Protect `logs/cache/vault_embeddings.json` from concurrent access corruption. Use `fcntl.flock()` on Unix or `msvcrt.locking()` on Windows, or implement atomic rename pattern.

**Estimate Calibrator** (deepseek-v3.2):
  1. Decompose the "Effort X/10" estimates into specific sub-tasks with time allocations for each, referencing the [HIGH] finding on single-number estimates.
  2. Add a "Phase 0: Setup & Integration Discovery" to investigate Ollama integration and codebase modifications before committing to the main implementation timeline, addressing the [MEDIUM] finding on lack of contingency.
  3. Open `scripts/cto_context_lib.py` and explicitly map where new functions will be added and how they will interact with existing code to ground the Phase 1 estimate, as noted in the [MEDIUM] finding on underestimated complexity.

**Test & QA Strategy Auditor** (qwen-3.5-27b):
  1. **Add automated unit tests for all new functions** — Reference: [CRITICAL] No Automated Tests for Semantic Search Implementation. Create `tests/test_cto_context_lib.py` with tests for `embed_text()`, `_cosine_similarity()`, `search_semantic()`, `ollama_available()`, and cache management functions.
  2. **Create CI pipeline with test enforcement** — Reference: [CRITICAL] No CI Pipeline to Enforce Quality Gates. Add `.github/workflows/test.yml` that runs `pytest` on PR and blocks merge if tests fail or coverage drops on changed files.
  3. **Add mock Ollama for CI compatibility** — Reference: [HIGH] Test Environment Requires Manual Ollama Setup. Use `pytest-mock` to stub Ollama API calls in CI, and provide a local setup script for developers who need to test with real Ollama.

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Add runtime validation for Ollama API contract** (CRITICAL finding): Ensure the model's output dimensions and response structure match expectations before caching embeddings. This prevents silent failures or incorrect results due to model changes.
  2. **Implement timeouts and circuit breakers for Ollama API calls** (HIGH finding): Prevent hangs and improve resilience by adding timeouts, retries, and circuit breakers to all HTTP calls to Ollama.
  3. **Make cache writes atomic** (HIGH finding): Use temporary files and `os.replace()` to ensure the cache file is never corrupted, even if the process is interrupted.
  ---

---

## Instructions for Primary Agent

You are receiving this synthesis from a 7-persona review council (budget API stack, 5 models).
Process these findings as follows:

1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan.
2. **Discredit**: If a finding is wrong (reviewer lacked context), note why and discard it.
3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge.
4. **Prioritize**: Rank validated findings by implementation impact.
5. **Act**: Fix the plan or document why the risk is accepted.

Do NOT blindly accept all findings. These are cheap models with focused prompts —
they catch real issues but also produce false positives. Your job is to be the judge.