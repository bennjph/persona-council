# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/7 completed | 146.0s | $0.0403

**Failed reviewers:** Requirements Archaeologist (invalid)

**Total findings:** 48 (CRITICAL: 7 | HIGH: 13 | MEDIUM: 17 | LOW: 11)

### CRITICAL

- **Undefined "semantic search" behavior when Ollama is partially available** — _Spec Prosecutor_ (deepseek-v3.2)
- **Missing Dependency for Cosine Similarity** — _Testability Auditor_ (gemini-3-flash)
- **Unbounded Query Input Allows Resource Exhaustion** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Path Traversal in Backup Function** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Vague "Relevance" Metric in Success Criteria** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Undefined Ollama API Contract** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Fallback for Embedding Failures** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Contradiction between "Embedding Target" and actual implementation** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous cache staleness definition leads to inconsistent updates** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined Cache TTL Logic** — _Testability Auditor_ (gemini-3-flash)
- **Integration Gap: Ollama API Timeout/Latency** — _Testability Auditor_ (gemini-3-flash)
- **Cache Corruption Has No Recovery Path** — _Edge Case Hunter_ (qwen-3.5-27b)
- **TOCTOU Race Condition in Backup** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No File Locking on Cache Writes** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Inadequate test coverage for Ollama integration failure modes** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Undefined "Typical Delta" for Cache Performance** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **No Acceptance Criteria for Cache Corruption Recovery** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Cache Corruption Risk Without Atomic Writes** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Rate Limiting or Retry Logic for Ollama API** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Embedding Target Omits Critical Context** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **Boundary condition missing for empty or malformed learning files** — _Spec Prosecutor_ (deepseek-v3.2)
- **Contradiction in search result ranking and display** — _Spec Prosecutor_ (deepseek-v3.2)
- **Subjective Success Metric for Search Quality** — _Testability Auditor_ (gemini-3-flash)
- **Non-Deterministic "Top 5" Selection on Score Ties** — _Testability Auditor_ (gemini-3-flash)
- **No Timeout on Ollama HTTP Requests** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Validation on Embedding Response Format** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Cache Size Limit** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Markdown Encoding Errors Not Handled** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Missing edge cases for embedding and cache operations** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Unrealistic test data limits validation** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Insufficient regression test coverage for existing keyword search** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **"Graceful Fallback" Lacks Measurable Definition** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **No Negative Test Scenarios for Semantic Search** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Missing Traceability to Parent Requirements** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Cache TTL Not Configurable** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Validation of Embedding Quality** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Protection Against Cache Poisoning** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Undefined behavior for cache file corruption during read** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Coverage" evaluation test** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Thesis Line" Extraction** — _Testability Auditor_ (gemini-3-flash)
- **No Backup Cleanup Policy** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Model Name Not Validated** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Rate Limiting on Ollama Calls** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Test maintainability risk from tight coupling to file system** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **No Performance Threshold for Semantic Search Latency** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Cache Size Threshold Not Defined** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Hardcoded Model Name** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Logging for Debugging** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Spec Prosecutor** (deepseek-v3.2):
  1. **Define partial failure modes for Ollama** (CRITICAL finding). Update the Error Handling table to specify timeout, HTTP error, and malformed response behaviors, ensuring the fallback is robust.
  2. **Clarify the embedding text source** (HIGH finding). Align the plan's "Embedding Target" with the implemented `_extract_learning_text` function by documenting the exact concatenation logic in `cto_context_lib.py`.
  3. **Specify cache staleness algorithm** (HIGH finding). Replace "modified since last cache" with a precise rule comparing file mtime to a stored mtime within the cache entry.

**Testability Auditor** (gemini-3-flash):
  1. **Establish a Deterministic Benchmark**: Replace the subjective "relevant learnings" metric with a fixed JSON file of Query-to-Document mappings to allow for automated regression testing of search quality (Relates to Finding 1).
  2. **Hard-code API Timeouts**: Implement a strict timeout on the Ollama HTTP call in `cto_context_lib.py`. Without this, the "graceful fallback" is untestable as it depends on the OS-level socket timeout which is often too long (Relates to Finding 6).
  3. **Formalize the Staleness Contract**: Clarify the conflict between `mtime` checking and the 24-hour TTL. A deterministic test cannot verify "incremental refresh" if the rules for what constitutes "stale" are contradictory (Relates to Finding 2).

**Edge Case Hunter** (qwen-3.5-27b):
  1. **Implement path validation in `backup_before_write`** (relates to CRITICAL Path Traversal finding) - Add `assert src.is_relative_to(ROOT)` to prevent backup of arbitrary system files
  2. **Add file locking to cache operations** (relates to HIGH Cache Corruption finding) - Use `fcntl.flock()` or atomic write pattern to prevent concurrent cache corruption
  3. **Add query length limits and timeouts** (relates to CRITICAL Resource Exhaustion finding) - Limit `--query` to 1000 chars and add 30s timeout to all Ollama HTTP requests

**QA Test Case Reviewer** (deepseek-v3.2):
  1. **Add failure mode tests for Ollama integration** — Critical for ensuring the system's advertised graceful degradation works under all expected failure conditions (see HIGH finding).
  2. **Expand test queries to be adversarial and realistic** — To validate semantic search finds conceptually related content beyond simple keyword matching, using queries with synonyms, misspellings, and natural language (see MEDIUM finding on test data).
  3. **Create a regression test suite for existing keyword search** — Protect the core functionality from breaking during the semantic search upgrade (see MEDIUM finding on regression).

**Acceptance Criteria Engineer** (qwen-3.5-27b):
  1. **Replace "relevant" with measurable similarity thresholds** — The success metric for semantic search cannot be verified without defining what "relevant" means. Use cosine similarity scores (≥0.65) and explicit test queries with known target documents. This relates to the CRITICAL finding on vague relevance metrics.
  2. **Add negative test scenarios for all error conditions** — The plan only defines positive scenarios. Add acceptance criteria for corrupted cache, empty vault, Ollama unavailable, and no semantic matches. This relates to the MEDIUM finding on missing negative tests.
  3. **Define cache performance baselines with concrete numbers** — "Typical delta" and "too high latency" are untestable. Specify exact file counts, time thresholds, and cache size limits. This relates to the HIGH finding on undefined cache performance.

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Define the Ollama API contract explicitly** (CRITICAL: Undefined Ollama API Contract) — Without this, the integration cannot be tested or validated, and failures will surface in production.
  2. **Implement atomic cache writes and corruption detection** (HIGH: Cache Corruption Risk Without Atomic Writes) — Cache corruption could silently degrade search results or cause crashes.
  3. **Add fallback thresholds and retry logic** (CRITICAL: No Fallback for Embedding Failures, HIGH: No Rate Limiting or Retry Logic) — Partial failures (e.g., 50% of files fail to embed) should not silently degrade to keyword search without warning.
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