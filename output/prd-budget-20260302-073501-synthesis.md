# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/7 completed | 203.7s | $0.0455

**Failed reviewers:** Acceptance Criteria Engineer (invalid)

**Total findings:** 44 (CRITICAL: 8 | HIGH: 13 | MEDIUM: 16 | LOW: 7)

### CRITICAL

- **Ambiguous "Embedding Target" Definition** — _Spec Prosecutor_ (deepseek-v3.2)
- **Untestable Performance Target** — _Testability Auditor_ (gemini-3-flash)
- **Non-Atomic Cache Write Risk** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Automated Test Suite Defined** — _QA Test Case Reviewer_ (kimi-k2.5)
- **Missing Regression Coverage for Keyword Search** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No Cache Corruption Recovery Tests** — _QA Test Case Reviewer_ (kimi-k2.5)
- **Undefined Embedding Model Version and Stability Requirements** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Fallback Behavior for Embedding Cache Corruption** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Missing operations monitoring for Ollama availability** — _Requirements Archaeologist_ (gpt-5.1-codex-mini)
- **Security stakeholder needs for sensitive content embedding are missing** — _Requirements Archaeologist_ (gpt-5.1-codex-mini)
- **Contradiction on Cache Refresh Trigger** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined Behavior for Missing "Thesis line" or "Tags"** — _Spec Prosecutor_ (deepseek-v3.2)
- **Non-Deterministic Embedding Target** — _Testability Auditor_ (gemini-3-flash)
- **Cache File Race Condition** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Ollama Network Timeout Missing** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Network Failure/Timeout Testing** — _QA Test Case Reviewer_ (kimi-k2.5)
- **Missing Concurrency/Race Condition Tests** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No Input Validation Edge Cases** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No SLA or Latency Requirements for Ollama Embedding Service** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Contract for Ollama API Response Shape** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Data Contract for Embedding Cache Format** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **Cache TTL is mentioned but not implemented** — _Requirements Archaeologist_ (gpt-5.1-codex-mini)
- **Assumes embedding dimension is fixed without verification** — _Requirements Archaeologist_ (gpt-5.1-codex-mini)
- **Contradictory Search Output Formats** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Ollama available" Health Check** — _Spec Prosecutor_ (deepseek-v3.2)
- **Subjective Success Metric: "Relevancy"** — _Testability Auditor_ (gemini-3-flash)
- **Undefined Cache TTL Behavior** — _Testability Auditor_ (gemini-3-flash)
- **Query Input Length Unbounded** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Mtime-Based Staleness Fragility** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Path Traversal in File Iteration** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Adversarial Test Data** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No Stress Testing for Vault Scale** — _QA Test Case Reviewer_ (kimi-k2.5)
- **Backup Functionality Untested** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No Rate Limiting or Throttling for Ollama API Calls** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Validation of Embedding Input Text** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Observability for Semantic Search Failures** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Protection Against Cache Poisoning** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Cache cleanup for deleted or renamed files is undefined** — _Requirements Archaeologist_ (gpt-5.1-codex-mini)
- **Undefined Boundary for "Top-5" Results** — _Spec Prosecutor_ (deepseek-v3.2)
- **Missing State Transition for Cache Corruption** — _Spec Prosecutor_ (deepseek-v3.2)
- **Missing Dependency Versioning** — _Testability Auditor_ (gemini-3-flash)
- **Timestamp Edge Cases Ignored** — _QA Test Case Reviewer_ (kimi-k2.5)
- **No Compression for Embedding Cache** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No User Control Over Cache Location** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Requirements Archaeologist** (gpt-5.1-codex-mini):
  1. Implement actionable monitoring/alerting for Ollama availability (Finding: Missing operations monitoring for Ollama availability).
  2. Enforce the declared cache TTL by invalidating/re-embedding entries older than the configured window (Finding: Cache TTL is mentioned but not implemented).
  3. Introduce opt-in filtering/redaction for sensitive transcripts before embedding to satisfy security stakeholders (Finding: Security stakeholder needs for sensitive content embedding are missing).

**Spec Prosecutor** (deepseek-v3.2):
  1. **[CRITICAL Fix]** Precisely define the text extraction algorithm for embeddings, including handling missing fields, to ensure consistent vector generation across runs and implementations.
  2. **[HIGH Fix]** Resolve the contradiction between TTL-based and mtime-based cache refresh by choosing one strategy and updating all spec sections and function names/logic accordingly.
  3. **[HIGH Fix]** Define complete behavior for edge cases in the embedding target (missing thesis, missing tags) to prevent runtime errors or malformed data.

**Testability Auditor** (gemini-3-flash):
  1. **Establish a Deterministic Evaluation Suite (Relates to "Subjective Success Metric")**: Replace the vague "finds relevant learnings" metric with a static JSON mapping of queries to expected document IDs. This allows for automated Precision/Recall testing.
  2. **Hard-code the Embedding Concatenation Logic (Relates to "Non-Deterministic Embedding Target")**: The current logic relies on "first paragraph after title." If a file starts with an image or a table, the embedding will be noise. Use a robust Markdown parser (like `marko` or `mistune`) rather than regex to extract these fields.
  3. **Define "Stale" Deterministically (Relates to "Undefined Cache TTL Behavior")**: Reconcile the conflict between `mtime` logic and the 24-hour TTL requirement in the code to prevent the cache from becoming permanently out of sync with the model version.
  ---

**Edge Case Hunter** (qwen-3.5-27b):
  1. **Implement Atomic Cache Writes** (Relates to CRITICAL finding): Refactor `save_embedding_cache` to write to a temporary file in the same directory and use `os.replace` to swap it into place, ensuring the cache file is never in a partial state.
  2. **Add File Locking to Cache Operations** (Relates to HIGH finding): Wrap all reads and writes to `logs/cache/vault_embeddings.json` with an exclusive lock to prevent race conditions between search and refresh operations.
  3. **Enforce Network Timeouts for Ollama** (Relates to HIGH finding): Configure a strict timeout (e.g., 5s) on all HTTP requests to the Ollama API to prevent the CLI from hanging indefinitely during service degradation.

**QA Test Case Reviewer** (kimi-k2.5):
  1. **Implement automated regression test suite for keyword search** (addresses CRITICAL finding): Before considering this complete, create pytest tests that verify the refactored `main()` function produces identical JSON and text output for all existing keyword-only use cases, ensuring the router refactor didn't break existing behavior.
  2. **Add fault injection tests for Ollama integration** (addresses HIGH finding): Create tests that mock `urllib.request` to simulate network timeouts, connection refused, and malformed JSON responses, verifying the graceful fallback logic works correctly and doesn't crash the CLI.
  3. **Implement cache corruption recovery tests** (addresses CRITICAL finding): Write tests that write intentionally corrupted JSON to `vault_embeddings.json` (truncated data, wrong embedding dimensions, null values) and verify the system detects corruption and rebuilds the cache rather than crashing with a JSONDecodeError.

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Pin the Ollama model version and define a fallback model** (relates to [CRITICAL] Undefined Embedding Model Version and Stability Requirements). Without this, the semantic search feature is at risk of silent degradation or failure if the model is updated or deprecated.
  2. **Implement cache corruption recovery with backup and fallback** (relates to [CRITICAL] No Fallback Behavior for Embedding Cache Corruption). This ensures that the system remains functional even if the cache is corrupted, preventing user-facing failures.
  3. **Add response validation and latency requirements for the Ollama API** (relates to [HIGH] No SLA or Latency Requirements for Ollama Embedding Service and [HIGH] No Contract for Ollama API Response Shape). This protects against API changes and ensures a consistent user experience.
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