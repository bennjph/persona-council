# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 5/7 completed | 430.9s | $0.0462

**Failed reviewers:** Architecture Stress Tester (invalid), Estimate Calibrator (invalid)

**Total findings:** 30 (CRITICAL: 4 | HIGH: 8 | MEDIUM: 11 | LOW: 7)

### CRITICAL

- **No Rollback Path for Cache Corruption or Schema Changes** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Missing Saturation Monitoring for Local Inference** — _Observability Advocate_ (gemini-3-flash)
- **Missing Test Automation for Semantic Search** — _Test & QA Strategy Auditor_ (llama-4-maverick)
- **Ollama API Contract Not Validated** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Blast Radius of Cache Staleness Affects All Semantic Search Users** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Silent Failure in Cache Corruption Handling** — _Observability Advocate_ (gemini-3-flash)
- **Missing Correlation ID for Cross-Process Requests** — _Observability Advocate_ (gemini-3-flash)
- **Dynamic Import Creates Hidden Dependency** — _Coupling Detector_ (qwen-3.5-27b)
- **Shared Cache File Creates Implicit Contract** — _Coupling Detector_ (qwen-3.5-27b)
- **CI Pipeline Not Configured for Test Automation** — _Test & QA Strategy Auditor_ (llama-4-maverick)
- **No Circuit Breaker for Ollama API Calls** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache Corruption Not Handled** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **No Feature Flag for Semantic Search Integration** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Deployment Sequence Lacks Validation of External Dependency Health** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Lack of Latency Histograms for Semantic vs. Keyword** — _Observability Advocate_ (gemini-3-flash)
- **Ollama Availability Check Creates Temporal Coupling** — _Coupling Detector_ (qwen-3.5-27b)
- **ROOT Path Coupling to Filesystem Layout** — _Coupling Detector_ (qwen-3.5-27b)
- **SOURCE_WEIGHTS Shared Configuration Affects Both Search Paths** — _Coupling Detector_ (qwen-3.5-27b)
- **Test Environment Dependencies Not Automated** — _Test & QA Strategy Auditor_ (llama-4-maverick)
- **Cache Management Not Tested in CI** — _Test & QA Strategy Auditor_ (llama-4-maverick)
- **No Fallback for Embedding Failures** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache TTL Not Configurable** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Integration Tests for Semantic Search** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Data Migration Risk from Embedding Model Changes** — _Deployment Risk Assessor_ (deepseek-v3.2)
- **Ambiguous Alert Threshold for Cache Stale-ness** — _Observability Advocate_ (gemini-3-flash)
- **Backup Directory Not Integrated with Semantic Search** — _Coupling Detector_ (qwen-3.5-27b)
- **Cache Size Not Monitored** — _Coupling Detector_ (qwen-3.5-27b)
- **Documentation Lacks Testing Guidance** — _Test & QA Strategy Auditor_ (llama-4-maverick)
- **Embedding Target Concatenation May Dilute Semantic Signal** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Monitoring for Ollama Model Drift** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Deployment Risk Assessor** (deepseek-v3.2):
  1. **Implement versioned backups for the embedding cache** to enable instant rollback from corruption or bad embeddings. This addresses the CRITICAL finding of no rollback path.
  2. **Add a runtime feature flag to control semantic search availability**, not just a CLI flag, to allow disabling the new functionality without code changes. This addresses the MEDIUM finding on lack of operational control.
  3. **Introduce a stability pre-check and circuit breaker for Ollama calls** during cache population to prevent a partial, corrupted cache state from being saved. This addresses the HIGH finding on blast radius from cache staleness.

**Observability Advocate** (gemini-3-flash):
  1. **Implement Resource Guardrails**: Add a hard timeout to the Ollama API client and monitor system load during `--refresh-cache` to prevent the SRE's worst nightmare: a background "maintenance" script locking up the production-adjacent dev environment. (Relates to CRITICAL finding).
  2. **Inject Trace Context**: Add a unique `trace_id` to the search flow that propagates from the CLI to the library and into the Ollama HTTP headers. Without this, debugging a "slow search" in a distributed (even if local) system is guesswork. (Relates to HIGH finding).
  3. **Automate Latency Benchmarking**: Add a `--bench` flag to the search script that runs both engines and outputs the delta. If semantic search adds >500ms to the user experience, the "2x faster" agentic coding claim is invalidated. (Relates to MEDIUM finding).

**Coupling Detector** (qwen-3.5-27b):
  1. **Move dynamic imports to module level** (relates to HIGH: Dynamic Import Creates Hidden Dependency) — This exposes the full dependency surface and enables static analysis. The 5-line change prevents future debugging nightmares when functions are renamed or removed.
  2. **Add schema validation to cache file** (relates to HIGH: Shared Cache File Creates Implicit Contract) — Define a TypedDict for cache entries and validate on load. This prevents silent corruption when the format changes and makes the contract explicit.
  3. **Wrap semantic search in try/except** (relates to MEDIUM: Ollama Availability Check Creates Temporal Coupling) — The availability check is a race condition. Wrap the actual embedding calls to handle connection failures gracefully and log specific error types.

**Test & QA Strategy Auditor** (llama-4-maverick):
  1. **Implement automated testing for semantic search** — Create test cases that validate semantic search results against expected outcomes for critical queries.
  2. **Configure CI pipeline to run semantic search tests** — Add a test stage to the CI configuration that executes automated tests for semantic search functionality.
  3. **Automate test environment setup** — Create a script or container configuration that sets up Ollama and required Python dependencies for testing.

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Add runtime validation for Ollama API responses** (CRITICAL finding). Ensure the embedding dimensionality matches expectations (768) and fail gracefully if not. This prevents silent failures due to model changes.
  2. **Implement timeouts, retries, and circuit breakers for Ollama API calls** (HIGH finding). Use a 5-second timeout and 2 retries for transient failures, and halt calls if Ollama fails repeatedly.
  3. **Handle cache corruption and add integration tests** (HIGH and MEDIUM findings). Wrap cache operations in try-catch blocks, rebuild the cache on corruption, and add automated tests for semantic search and fallback behavior.
  ---

---

## Instructions for Primary Agent

You are receiving this synthesis from a 7-persona review council (budget API stack).
Process these findings as follows:

1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan.
2. **Discredit**: If a finding is wrong (reviewer lacked context), note why and discard it.
3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge.
4. **Prioritize**: Rank validated findings by implementation impact.
5. **Act**: Fix the plan or document why the risk is accepted.

Do NOT blindly accept all findings. These are cheap models with focused prompts —
they catch real issues but also produce false positives. Your job is to be the judge.