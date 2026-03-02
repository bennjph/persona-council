# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 7/7 completed | 92.1s | $0.0404

**Total findings:** 40 (CRITICAL: 6 | HIGH: 10 | MEDIUM: 14 | LOW: 10)

### CRITICAL

- **Memory-Bound Linear Scan in Search Path** — _Architecture Stress Tester_ (gemini-3-flash)
- **Missing Saturation Monitoring for Local Inference** — _Observability Advocate_ (gemini-3-flash)
- **Single-number effort estimates without decomposition** — _Estimate Calibrator_ (deepseek-v3.2)
- **No automated test strategy exists** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No CI pipeline to enforce test execution** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Ollama API contract assumptions not validated** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Atomic Write Failure Risk in Cache Management** — _Architecture Stress Tester_ (gemini-3-flash)
- **Synchronous API Bottleneck in Embedding Generation** — _Architecture Stress Tester_ (gemini-3-flash)
- **Silent Failure in Cache Integrity** — _Observability Advocate_ (gemini-3-flash)
- **Missing Correlation IDs in Search Logs** — _Observability Advocate_ (gemini-3-flash)
- **Missing function implementations in library** — _Coupling Detector_ (qwen-3.5-27b)
- **Plan underestimates complexity of modifying core library functions** — _Estimate Calibrator_ (deepseek-v3.2)
- **Ollama dependency creates untestable code paths without mocks** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Cache file committed to repository creates CI bloat and merge conflicts** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No circuit breaker or retry logic for Ollama API calls** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache corruption risk due to non-atomic writes** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **Implicit Coupling via Localhost Port Dependency** — _Architecture Stress Tester_ (gemini-3-flash)
- **N+1 File System Metadata Access** — _Architecture Stress Tester_ (gemini-3-flash)
- **Rollback path for Ollama dependency is missing** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Blast radius of embedding cache corruption is uncontained** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Lack of Latency Thresholds for Semantic Path** — _Observability Advocate_ (gemini-3-flash)
- **Unstructured Error Logging** — _Observability Advocate_ (gemini-3-flash)
- **Shared mutable cache without concurrency protection** — _Coupling Detector_ (qwen-3.5-27b)
- **Temporal coupling between cache refresh and search operations** — _Coupling Detector_ (qwen-3.5-27b)
- **Zero contingency for discovery work and integration surprises** — _Estimate Calibrator_ (deepseek-v3.2)
- **No test data strategy for semantic search quality verification** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Error handling tested manually only** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **QA effort not included in estimates** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **No fallback for embedding failures on individual files** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No integration tests for Ollama API boundary** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Brittle Text Extraction for Embeddings** — _Architecture Stress Tester_ (gemini-3-flash)
- **Data migration risk during cache refresh lacks atomicity** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Feature flag coverage is implicit but not explicit** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Deployment sequence creates a brief period of broken state** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Global ROOT path creates implicit coupling** — _Coupling Detector_ (qwen-3.5-27b)
- **Wide parameter list in search_context function** — _Coupling Detector_ (qwen-3.5-27b)
- **Parallelism risk between cache and search modifications** — _Estimate Calibrator_ (deepseek-v3.2)
- **parallelism risk** — _Estimate Calibrator_ (deepseek-v3.2)
- **Implementation claims cannot be verified from truncated source** — _Test & QA Strategy Auditor_ (qwen-3.5-27b)
- **Cache TTL is hardcoded and not configurable** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Architecture Stress Tester** (gemini-3-flash):
  1. **Implement Atomic File Writes**: Modify `save_embedding_cache` to write to a temporary file and use `os.replace()`. This prevents the "Corrupt Cache" failure mode which would block all semantic searches. (Relates to HIGH: Atomic Write Failure Risk)
  2. **Decouple Retrieval from Brute Force**: Even at 10x scale (1,000 docs), the overhead of deserializing a 20MB JSON and iterating in Python will be felt. Move toward a binary format or a dedicated vector index. (Relates to CRITICAL: Memory-Bound Linear Scan)
  3. **Add Batching to Embedding Logic**: Update `embed_text` to support a list of strings. This reduces the HTTP overhead and allows Ollama to optimize GPU/CPU utilization during the `--refresh-cache` process. (Relates to HIGH: Synchronous API Bottleneck)

**Deployment Risk Assessor** (deepseek-v3.2):
  1. Document a complete rollback procedure to remove the Ollama dependency and semantic search feature, as per the first finding.
  2. Implement atomic writes and defensive loading for the embedding cache to prevent corruption from breaking the feature, as per the second and third findings.
  3. Define explicit evaluation criteria and a timeline for the `--semantic` feature flag to decide on its future, as per the fourth finding.

**Observability Advocate** (gemini-3-flash):
  1. **Implement Model Version Pinning in Cache**: (Relates to CRITICAL/HIGH findings) Ensure the embedding cache includes the model name. Searching with a 768-dim vector against a cache generated by a different model will return garbage results without throwing an error.
  2. **Add Resource Saturation Guards**: (Relates to CRITICAL finding) Before triggering a `--refresh-cache`, check if the local machine has the headroom to run 99+ embedding generations without crashing the agent's environment.
  3. **Define Search Latency Budgets**: (Relates to MEDIUM finding) Set a 2-second timeout on the semantic path. A "smart" search that takes 30 seconds is operationally broken compared to a "dumb" keyword search that takes 50ms.

**Coupling Detector** (qwen-3.5-27b):
  1. **Verify missing function implementations** — Check if `search_semantic`, `ollama_available`, `_extract_learning_text`, and `embed_text` actually exist in `cto_context_lib.py` before marking plan as complete (relates to HIGH finding)
  2. **Add file locking to cache writes** — Implement atomic write pattern or file locking in `save_embedding_cache` to prevent corruption if multiple processes access cache simultaneously (relates to MEDIUM finding)
  3. **Integrate cache freshness into normal search flow** — Remove special `--refresh-cache` execution path and check cache freshness automatically during semantic search (relates to MEDIUM finding)

**Estimate Calibrator** (deepseek-v3.2):
  1. Decompose the abstract effort scores (2/10, 3/10) into concrete sub-tasks with time estimates for each, including testing and integration. **[CRITICAL]**
  2. Examine the `_extract_learning_text` function in `cto_context_lib.py` to verify the embedding target logic and update the plan/estimate accordingly. **[HIGH]**
  3. Add an explicit contingency buffer (+2 days) to the Week 1 schedule for integration surprises and discovery work. **[MEDIUM]**

**Test & QA Strategy Auditor** (qwen-3.5-27b):
  1. **Create automated pytest test suite** — Reference: CRITICAL finding #1. Write unit tests for all new functions in `cto_context_lib.py` (embed_text, cosine_similarity, cache functions) and integration tests for `--semantic` flag behavior. Minimum 80% coverage on changed code.
  2. **Add CI pipeline with test enforcement** — Reference: CRITICAL finding #2. Create `.github/workflows/test.yml` that runs pytest on every PR, fails build on test failure, and excludes `logs/cache/` from version control.
  3. **Implement mock strategy for Ollama dependency** — Reference: HIGH finding #3. Add `unittest.mock` patches for HTTP calls to Ollama API; create test fixtures with simulated embedding responses; ensure all Ollama-dependent paths have mock-based tests that run without external service.

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Add runtime validation for Ollama API responses** (relates to [CRITICAL] Ollama API contract assumptions not validated). Without this, the integration could silently break if Ollama changes its API shape.
  2. **Implement circuit breakers and retries for Ollama API calls** (relates to [HIGH] No circuit breaker or retry logic for Ollama API calls). This prevents transient failures from cascading into search outages.
  3. **Use atomic file writes for the embedding cache** (relates to [HIGH] Cache corruption risk due to non-atomic writes). This ensures the cache remains consistent even if the process is interrupted.
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