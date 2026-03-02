# Council Synthesis Brief (API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/6 completed | 112.4s | $0.0958

**Total findings:** 38 (CRITICAL: 6 | HIGH: 13 | MEDIUM: 14 | LOW: 5)

### CRITICAL

- **Single mutable JSON cache is a write-time SPOF with no concurrency control** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **No Rollback Path for Cache Corruption or Schema Changes** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Silent Degradation on Embedding Failures** — _Observability Advocate_ (gemini-3.1-pro)
- **Missing backup_before_write usage in cache operations** — _Coupling Detector_ (qwen-3.5-27b)
- **No automated tests exist for completed feature** — _Test & QA Strategy Auditor_ (glm-5)
- **CI pipeline has no test stage for this module** — _Test & QA Strategy Auditor_ (glm-5)

### HIGH

- **Embedding refresh pipeline is strictly sequential and will not hold at 10x/100x corpus growth** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Semantic and keyword corpora are implicitly divergent (distributed-monolith behavior at retrieval layer)** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Stale/deleted content lifecycle is under-specified, risking ghost results and broken references** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Blast Radius of Cache Staleness Affects All Semantic Search Users** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Unbounded JSON Cache Loading Latency** — _Observability Advocate_ (gemini-3.1-pro)
- **Missing Timeout Controls for Ollama API** — _Observability Advocate_ (gemini-3.1-pro)
- **Import statement inside conditional block breaks module-level dependency tracking** — _Coupling Detector_ (qwen-3.5-27b)
- **Cache file has no existence check before load** — _Coupling Detector_ (qwen-3.5-27b)
- **Undefined Estimation Scale** — _Estimate Calibrator_ (minimax-m2.5)
- **External Dependency Not Accounted in Timeline** — _Estimate Calibrator_ (minimax-m2.5)
- **Missing Verification That Effort Estimates Match Code Complexity** — _Estimate Calibrator_ (minimax-m2.5)
- **Keyword search regression risk untested** — _Test & QA Strategy Auditor_ (glm-5)
- **Fallback behavior is unverified by automation** — _Test & QA Strategy Auditor_ (glm-5)

### MEDIUM

- **Model-version drift creates hidden coupling and non-reproducible retrieval quality** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Query path is full-scan vector ranking over JSON; this is under-engineered for 100x** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Output path is a dual list (semantic + keyword) with no rank fusion, creating operator bottlenecks** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **No Backward Compatibility for Search Clients** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Deployment Sequence Lacks Verification and Staging Step** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Lack of Trace Context to Local LLM** — _Observability Advocate_ (gemini-3.1-pro)
- **Ambiguous Cache Corruption Detection** — _Observability Advocate_ (gemini-3.1-pro)
- **search_semantic function signature not visible in truncated code** — _Coupling Detector_ (qwen-3.5-27b)
- **Large cache file (89,012 lines) may cause I/O bottlenecks** — _Coupling Detector_ (qwen-3.5-27b)
- **Temporal coupling: Ollama availability check happens after cache refresh starts** — _Coupling Detector_ (qwen-3.5-27b)
- **No Explicit Contingency Buffer** — _Estimate Calibrator_ (minimax-m2.5)
- **Test Coverage Not Specified** — _Estimate Calibrator_ (minimax-m2.5)
- **QA effort not estimated in plan** — _Test & QA Strategy Auditor_ (glm-5)
- **Cache corruption handling is untested** — _Test & QA Strategy Auditor_ (glm-5)

### LOW

- **Failure handling degrades silently, masking service health issues** — _Architecture Stress Tester_ (gpt-5.3-codex)
- **Point of No Return for Ollama Model Not Documented** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **SOURCE_WEIGHTS global couples search behavior to hardcoded paths** — _Coupling Detector_ (qwen-3.5-27b)
- **Parallelism Claim Mismatch** — _Estimate Calibrator_ (minimax-m2.5)
- **Test environment setup not documented** — _Test & QA Strategy Auditor_ (glm-5)

### Reviewer Top Recommendations

**Architecture Stress Tester** (gpt-5.3-codex):
  1. Replace `vault_embeddings.json` with a transactional, lock-safe index store and generation-based reads/writes (Finding: **Single mutable JSON cache is a write-time SPOF**).
  2. Decouple indexing from query serving with asynchronous/batched embedding jobs and bounded parallelism (Finding: **Embedding refresh pipeline is strictly sequential**).
  3. Unify corpus scope and lifecycle rules (coverage + deletion handling) across semantic and keyword paths (Findings: **Semantic/keyword corpus divergence** and **stale/deleted lifecycle gap**).

**Deployment Risk Assessor** (deepseek-v3.2):
  1. **[CRITICAL Fix]** Before deploying, implement a rollback and recovery mechanism for the `vault_embeddings.json` cache, including versioned backups and a restore command. (Relates to: CRITICAL - No Rollback Path for Cache Corruption)
  2. **[HIGH Fix]** Add robustness to the cache freshness logic: implement warnings for stale entries and a health check to proactively identify degradation. (Relates to: HIGH - Blast Radius of Cache Staleness)
  3. **[MEDIUM Fix]** Run a shadow evaluation phase where semantic search results are collected and compared to keyword baselines before enabling the `--semantic` flag for general use. (Relates to: MEDIUM - Deployment Sequence Lacks Verification)

**Observability Advocate** (gemini-3.1-pro):
  1. Add strict HTTP timeouts and explicit `TimeoutError` handling for all Ollama API requests to prevent silent hangs and ensure the keyword fallback actually executes when the model stalls.
  2. Implement explicit error logging and a final failure summary during `--refresh-cache` so users know exactly which files are missing from the semantic index.
  3. Replace the monolithic JSON cache with a scalable local store (e.g., SQLite) before the JSON parsing overhead degrades CLI latency beyond acceptable interactive limits.

**Coupling Detector** (qwen-3.5-27b):
  1. **Add backup_before_write to cache operations** (relates to CRITICAL finding) — Wrap all `save_embedding_cache` calls with backup logic to enable safe cache recovery
  2. **Move imports to module level** (relates to HIGH finding) — Refactor `scripts/cto_context_search.py` to use standard import patterns for better static analysis and dependency tracking
  3. **Add cache existence check** (relates to HIGH finding) — Implement try/except around `load_embedding_cache()` to handle first-run scenarios gracefully

**Estimate Calibrator** (minimax-m2.5):
  1. **Replace "Effort X/10" with explicit time estimates** — The current scale is meaningless without defining the denominator. Use hours or days with breakdown per sub-task (implementation, testing, integration).
  2. **Add pre-flight Ollama check to schedule** — The plan acknowledges "if Ollama ready" but doesn't schedule the verification or the defer decision. Add "Day 0: Verify Ollama, decide proceed/defer" before Week 1.
  3. **Include test time explicitly** — The evaluation criteria describe ad-hoc testing but don't account for test writing. Add 1-2 hours for unit tests on embedding functions and integration tests for the hybrid search behavior.

**Test & QA Strategy Auditor** (glm-5):
  1. Create `tests/test_cto_context_semantic.py` with unit tests for all new functions (`embed_text`, `_cosine_similarity`, `search_semantic`, `ollama_available`) before considering this plan truly complete. (Relates to CRITICAL: No automated tests exist)
  2. Add a CI workflow that runs the test suite on every push, including a test configuration that verifies graceful fallback when Ollama is unavailable. (Relates to CRITICAL: CI pipeline has no test stage)
  3. Add regression tests for existing keyword search functionality to ensure the "major refactor" doesn't break current users. (Relates to HIGH: Keyword search regression risk)

---

## Instructions for Primary Agent

You are receiving this synthesis from a 6-persona review council (API dispatch).
Process these findings as follows:

1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan.
2. **Discredit**: If a finding is wrong (reviewer lacked context), note why and discard it.
3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge.
4. **Prioritize**: Rank validated findings by implementation impact.
5. **Act**: Fix the plan or document why the risk is accepted.

Do NOT blindly accept all findings. These are diverse cheap models with focused prompts —
they catch real issues but also produce false positives. Your job is to be the judge.