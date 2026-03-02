# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 7/7 completed | 142.3s | $0.0398

**Total findings:** 50 (CRITICAL: 9 | HIGH: 14 | MEDIUM: 16 | LOW: 11)

### CRITICAL

- **Silent Cache Invalidation on Model Change** — _Requirements Archaeologist_ (gemini-3-flash)
- **Ambiguous Embedding Target Definition** — _Spec Prosecutor_ (deepseek-v3.2)
- **Untestable "Token Reduction" Criterion** — _Testability Auditor_ (gemini-3-flash)
- **Path Traversal in Backup Function** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Unbounded Query Input Enables DoS** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Zero coverage for graceful fallback and error handling** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Subjective "Relevance" in Success Metrics** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Undefined Embedding Model Version and Stability** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Contract for Ollama API Response Shape** — _Dependency & Integration Risk Mapper_ (mistral-large)

### HIGH

- **Unbounded Memory Consumption during Search** — _Requirements Archaeologist_ (gemini-3-flash)
- **Race Condition in Atomic Cache Writes** — _Requirements Archaeologist_ (gemini-3-flash)
- **Contradiction in Search Output Format** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined Behavior for Cache Corruption** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined Similarity Threshold for "Match"** — _Testability Auditor_ (gemini-3-flash)
- **No Maximum Limit on Search Results** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Cache File Race Condition (TOCTOU)** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Non-Atomic Cache Write** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No test cases defined for core functionality** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Insufficient coverage for cache integrity and incremental refresh** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Undefined "Typical Delta" for Performance Testing** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **No Fallback for Embedding Failures Beyond Keyword Search** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache Invalidation Relies on mtime Only** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Rate Limiting or Throttling for Ollama API** — _Dependency & Integration Risk Mapper_ (mistral-large)

### MEDIUM

- **Missing Character/Token Limit on Embedding Inputs** — _Requirements Archaeologist_ (gemini-3-flash)
- **Implicit Dependency on Localhost Networking** — _Requirements Archaeologist_ (gemini-3-flash)
- **Contradictory Search Result Limit** — _Spec Prosecutor_ (deepseek-v3.2)
- **Missing Boundary Condition for "Ollama available"** — _Spec Prosecutor_ (deepseek-v3.2)
- **Ambiguous "Thesis Line" Extraction Logic** — _Testability Auditor_ (gemini-3-flash)
- **Missing Cache Collision/Stale Data Strategy** — _Testability Auditor_ (gemini-3-flash)
- **No Embedding Dimension Validation** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Unvalidated Model Parameter** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Cache Integrity Verification** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Missing Error Handling for Empty Embeddings** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No adversarial or realistic test data for embeddings** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Missing regression test coverage for existing keyword search** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Orphaned "Token Reduction" Evaluation Criterion** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **Embedding Target Omits Critical Context** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Validation of Embedding Quality** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **Cache File Location Not Version-Controlled** — _Dependency & Integration Risk Mapper_ (mistral-large)

### LOW

- **Brittle Heading Extraction** — _Requirements Archaeologist_ (gemini-3-flash)
- **Ambiguous "Incremental Refresh" Scope** — _Spec Prosecutor_ (deepseek-v3.2)
- **Undefined State for Missing Cache File** — _Spec Prosecutor_ (deepseek-v3.2)
- **Non-Deterministic "Top 5" Tie-Breaking** — _Testability Auditor_ (gemini-3-flash)
- **No Rate Limiting on Ollama API Calls** — _Edge Case Hunter_ (qwen-3.5-27b)
- **JSON Output Exposes Internal Paths** — _Edge Case Hunter_ (qwen-3.5-27b)
- **No Cache Size Limit** — _Edge Case Hunter_ (qwen-3.5-27b)
- **Test execution order dependency and brittleness risk** — _QA Test Case Reviewer_ (deepseek-v3.2)
- **Vague "Seamlessly" UX Definition** — _Acceptance Criteria Engineer_ (qwen-3.5-27b)
- **No Handling for Large Files or Timeouts** — _Dependency & Integration Risk Mapper_ (mistral-large)
- **No Documentation for Cache Schema** — _Dependency & Integration Risk Mapper_ (mistral-large)

### Reviewer Top Recommendations

**Requirements Archaeologist** (gemini-3-flash):
  1. **Implement Model-Versioning in Cache**: (Relates to CRITICAL finding) Prevent mathematical "garbage-in-garbage-out" by ensuring embeddings in the cache were generated by the same model currently active in Ollama.
  2. **Ensure Atomic File Operations**: (Relates to HIGH finding) Use the `write-to-temp-and-move` pattern for `vault_embeddings.json` to prevent the "Corrupt Cache" failure mode identified in the Error Handling table.
  3. **Add Input Sanitization/Truncation**: (Relates to MEDIUM finding) Explicitly bound the string length sent to the `/api/embeddings` endpoint to ensure the "Tags" (which are high-signal for search) aren't dropped by the model's internal token limits.

**Spec Prosecutor** (deepseek-v3.2):
  1. **CRITICAL**: Resolve the ambiguous embedding target definition by specifying a precise, deterministic text extraction algorithm for the title, thesis line, and tags.
  2. **HIGH**: Resolve the contradiction in the search output format by aligning the specification in the "Display format" section with the actual implementation shown in the verification.
  3. **HIGH**: Define the exact conditions and recovery procedure for "Cache corrupt" in the Error Handling table to ensure robust implementation.

**Testability Auditor** (gemini-3-flash):
  1. **Establish a Golden Data Set (Relates to CRITICAL finding)**: Create a static fixture of 10 queries and their expected semantic matches. Without this, "better than keyword" is a subjective opinion, not a verified requirement.
  2. **Hard-code the Similarity Floor (Relates to HIGH finding)**: Implement a `MIN_SEMANTIC_SCORE` constant. Testing "Top 5" without a floor results in "hallucinated" context where the 5th result might have a 0.2 similarity and be completely irrelevant.
  3. **Formalize the Embedding String Template (Relates to MEDIUM finding)**: Replace the "if present" logic with a strict template function. If a field (like Tags) is missing, it must be replaced with a deterministic empty string constant to ensure embedding consistency.

**Edge Case Hunter** (qwen-3.5-27b):
  1. **Fix path traversal vulnerability in `backup_before_write()`** (relates to CRITICAL finding) - Add path canonicalization and ROOT boundary validation before any file operations. This is the highest risk as it could allow reading/writing arbitrary files on the system.
  2. **Add input validation for `--query` and `--limit`** (relates to CRITICAL and HIGH findings) - Implement maximum length (1000 chars) for queries and maximum limit (100) for results. This prevents DoS attacks through resource exhaustion.
  3. **Implement atomic cache writes with integrity verification** (relates to HIGH and MEDIUM findings) - Use temp file + rename pattern for cache writes, add JSON schema validation on load, and implement checksum verification. This prevents cache corruption from causing silent failures.

**QA Test Case Reviewer** (deepseek-v3.2):
  1. **Define explicit test cases for all requirements and success metrics**, starting with the critical graceful fallback scenario. Reference the **CRITICAL** finding on error handling.
  2. **Create a test plan section** that maps test cases to each "Evaluation Criterion" and "Error Handling" scenario. Reference the **HIGH** finding on no test cases.
  3. **Implement a regression test suite for the existing keyword search** to protect against breakage during the upgrade. Reference the **MEDIUM** finding on regression coverage.

**Acceptance Criteria Engineer** (qwen-3.5-27b):
  1. **Replace subjective relevance metrics with ground-truth test cases** (Relates to Finding 1): Define a fixed set of 5 queries with expected file matches and minimum similarity scores to ensure deterministic verification of semantic search quality.
  2. **Quantify "typical delta" for performance gates** (Relates to Finding 2): Specify exact file counts (e.g., "5 modified files") and hardware assumptions (e.g., "SSD, 8GB RAM") to make the <5 second cache refresh target testable.
  3. **Align evaluation criteria with the stated objective** (Relates to Finding 3): Remove the "Token reduction" criterion from this plan's acceptance gates as it measures a downstream effect (prompt engineering) rather than the current deliverable (search retrieval).

**Dependency & Integration Risk Mapper** (mistral-large):
  1. **Pin the Ollama model version and validate the API contract** (CRITICAL findings). Without this, the integration is unverifiable and may break silently.
  2. **Add hybrid fallback for partial embedding failures** (HIGH finding). Skipping files without notification could degrade search quality without the user’s knowledge.
  3. **Improve cache invalidation with versioning and force-refresh** (HIGH finding). Relying solely on `mtime` risks stale or corrupted caches.
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