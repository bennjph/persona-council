# Council Synthesis Brief (API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/6 completed | 103.2s | $0.0916

**Total findings:** 49 (CRITICAL: 7 | HIGH: 14 | MEDIUM: 16 | LOW: 12)

### CRITICAL

- **Retrieval Quality Is Not Measurable or Reproducible** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **External Dependency Contract Is Assumed but Not Bounded** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Undefined "semantic search" behavior when Ollama is partially available** — _Spec Prosecutor_ (deepseek-v3.2)
- **Non-Deterministic Performance Metrics** — _Testability Auditor_ (gemini-3.1-pro)
- **Path Traversal in Backup Function** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Input Length Limits on Query Parameter** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Test Case Structure — Evaluation Criteria Are Not Formalized Tests** — _QA Test Case Reviewer_ (minimax-m2.5)

### HIGH

- **Cache Concurrency and Integrity Requirements Are Missing** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Stakeholder Coverage Is Narrow (Single Local Operator Bias)** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **CLI/Output Compatibility Is Changed Without a Contract** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Contradiction between "incremental refresh" definition and cache staleness logic** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Embedding Target" leads to inconsistent vector generation** — _Spec Prosecutor_ (deepseek-v3.2)
- **Subjective and Undefined Search Quality Metrics** — _Testability Auditor_ (gemini-3.1-pro)
- **Missing Fallback Logic for Malformed Markdown** — _Testability Auditor_ (gemini-3.1-pro)
- **Ollama API Calls Lack Timeout Configuration** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Cache File Has No Atomic Write Guarantee** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Validation on Embedding Cache Integrity** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Missing Test Data for Primary Success Criterion** — _QA Test Case Reviewer_ (minimax-m2.5)
- **No Edge Case Coverage for Embedding Pipeline** — _QA Test Case Reviewer_ (minimax-m2.5)
- **Vague Relevance Criterion** — _Acceptance Criteria Engineer_ (glm-5)
- **Undefined "Typical Delta" Threshold** — _Acceptance Criteria Engineer_ (glm-5)

### MEDIUM

- **Search Scope Is Underspecified and Inconsistent Across Modes** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Performance Targets Lack Environmental Constraints** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Error Handling Is Policy-Level Only (No Operational Bounds)** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Unclear state transition for `--refresh-cache` flag** — _Spec Prosecutor_ (deepseek-v3.2)
- **Boundary condition for "score" calculation and ranking is undefined** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined Configuration Mechanism for Cache TTL** — _Testability Auditor_ (gemini-3.1-pro)
- **Concurrency and Race Conditions in Cache Writes** — _Testability Auditor_ (gemini-3.1-pro)
- **Concurrent Cache Access Not Protected** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Maximum Limit on Search Results** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Empty Query Not Handled in Semantic Search** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Backup Directory Not Validated** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Boundary Testing for Cache Behavior** — _QA Test Case Reviewer_ (minimax-m2.5)
- **Regression Coverage Absent for Keyword Search** — _QA Test Case Reviewer_ (minimax-m2.5)
- **Subjective "Graceful Degradation" Criterion** — _Acceptance Criteria Engineer_ (glm-5)
- **Unmeasurable Token Reduction Criterion** — _Acceptance Criteria Engineer_ (glm-5)
- **Vague "Seamlessly" Toggle Criterion** — _Acceptance Criteria Engineer_ (glm-5)

### LOW

- **Data Retention and Privacy Handling for Embeddings Is Absent** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **“Completed” Status Lacks Automated Verification Artifacts** — _Requirements Archaeologist_ (gpt-5.3-codex)
- **Undefined behavior for empty or malformed cache file on startup** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Verification" success criteria** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined "Seamless" Toggle Requirement** — _Testability Auditor_ (gemini-3.1-pro)
- **No Cache Size Limit or Pruning Strategy** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Model Name Not Validated** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Test Data Lacks Real-World Adversarial Examples** — _QA Test Case Reviewer_ (minimax-m2.5)
- **No Performance Regression Tests** — _QA Test Case Reviewer_ (minimax-m2.5)
- **Single-Case Coverage Test** — _Acceptance Criteria Engineer_ (glm-5)
- **Missing Rollback Plan for Deployment Gate** — _Acceptance Criteria Engineer_ (glm-5)
- **Orphaned Cache Size Metric** — _Acceptance Criteria Engineer_ (glm-5)

### Reviewer Top Recommendations

**Requirements Archaeologist** (gpt-5.3-codex):
  1. Define a rigorous, reproducible relevance evaluation protocol with objective ranking metrics and pass/fail gates (**Retrieval Quality Is Not Measurable or Reproducible**).
  2. Formalize and enforce the Ollama/model dependency contract (version pinning, dimension validation, and failure behavior) (**External Dependency Contract Is Assumed but Not Bounded**).
  3. Add cache integrity controls (locking, atomicity, corruption handling) to prevent race-condition failures during refresh/search overlap (**Cache Concurrency and Integrity Requirements Are Missing**).

**Spec Prosecutor** (deepseek-v3.2):
  1. **Define failure mode contracts for Ollama API calls** (relates to CRITICAL finding). Specify HTTP timeout (e.g., 5s), retry logic (e.g., 0 retries), and exact conditions that trigger fallback to keyword search, ensuring deterministic behavior.
  2. **Clarify and implement cache staleness logic** (relates to HIGH finding). Remove the contradictory TTL claim or implement it. Update `get_stale_files` specification to reflect the chosen strategy (mtime-only or mtime+TTL).
  3. **Normalize the embedding input text** (relates to HIGH finding). Provide a pseudo-code function that extracts title, thesis, and tags robustly, handling edge cases to guarantee consistent embeddings across all vault files.

**Testability Auditor** (gemini-3.1-pro):
  1. Define a static benchmark suite of 10 exact queries and expected file matches to replace subjective relevance metrics (Addresses High: Subjective and Undefined Search Quality Metrics).
  2. Specify fallback extraction rules for markdown files that lack a thesis or tags to prevent concatenation errors or poor embeddings (Addresses High: Missing Fallback Logic for Malformed Markdown).
  3. Replace hardware-dependent time metrics with deterministic operational metrics, such as asserting the exact number of API calls made during an incremental refresh (Addresses Critical: Non-Deterministic Performance Metrics).

**Edge Case Hunter** (qwen-3.5-27b):
  1. **Add path traversal protection to `backup_before_write`** (relates to CRITICAL finding #1) - Implement `src.resolve().is_relative_to(ROOT)` check to prevent arbitrary file backup/overwrite attacks
  2. **Add timeout and retry logic to Ollama API calls** (relates to HIGH finding #3) - Configure 30-second timeout with 3 retries to prevent indefinite hangs on Ollama failures
  3. **Implement atomic cache writes with integrity validation** (relates to HIGH findings #4 and #5) - Use write-to-temp-then-rename pattern and add SHA-256 content hashes to prevent cache corruption

**QA Test Case Reviewer** (minimax-m2.5):
  1. **Formalize test cases from evaluation criteria** (CRITICAL finding): Convert the 4 evaluation criteria into executable test cases with specific input queries, expected outputs, and pass/fail thresholds. Without this, there's no way to verify the implementation actually meets its success metrics.
  2. **Add edge case and failure mode tests** (HIGH finding): The plan tests happy path but embedding pipelines have numerous failure modes (service unavailable, corrupt cache, encoding issues). Add explicit test cases for each error condition in the error handling table.
  3. **Verify keyword search regression** (MEDIUM finding): Before declaring semantic upgrade complete, prove keyword search still returns identical results. This is the most likely area for unintended regression when modifying shared library code.
  ---

**Acceptance Criteria Engineer** (glm-5):
  1. Define "relevant" with a similarity score threshold and a benchmark query set — this is the core success metric and currently cannot be verified deterministically (relates to HIGH: Vague Relevance Criterion).
  2. Replace "typical delta" with specific file count scenarios (e.g., "3 files modified" vs "99 files modified") — enables reproducible cache performance testing (relates to HIGH: Undefined "Typical Delta" Threshold).
  3. Add explicit rollback gates to each phase in the execution sequence — currently there is no documented recovery path if a phase fails (relates to LOW: Missing Rollback Plan for Deployment Gate).

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