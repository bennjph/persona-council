# Council Synthesis Brief (Budget API)

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 7/7 completed | 175.9s | $0.0420

**Total findings:** 40 (CRITICAL: 4 | HIGH: 11 | MEDIUM: 16 | LOW: 9)

### CRITICAL

- **Unbounded memory growth in embedding cache** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **Missing Test Suite for Semantic Search Logic** — _Test & Coverage Verifier_ (gemini-3-flash)
- **Match dataclass missing 'title' attribute** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)
- **Unverified library exports will cause import failure** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)

### HIGH

- **Semantic search may return no results silently when Ollama is unavailable** — _Logic & Correctness Auditor_ (deepseek-v3.2)
- **Potential SSRF and Internal Port Scanning via Ollama API URL** — _Security & Trust Boundary Reviewer_ (gemini-3-flash)
- **O(n) file I/O in `_iter_markdown_files` during semantic search** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **No batching in Ollama embedding requests** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **Semantic search results display format does not match specification** — _Plan Fidelity Checker_ (deepseek-v3.2)
- **Tautological Cache Refresh Logic** — _Test & Coverage Verifier_ (gemini-3-flash)
- **Untested Edge Case: Empty/Corrupt Cache File** — _Test & Coverage Verifier_ (gemini-3-flash)
- **Missing numpy dependency declaration** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)
- **search_semantic signature compatibility unknown** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)
- **Argument parser bypass for --refresh-cache** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)
- **Imports inside conditional block violate Python conventions** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)

### MEDIUM

- **Missing null/empty check for embedding result could cause runtime error** — _Logic & Correctness Auditor_ (deepseek-v3.2)
- **Cache refresh may fail silently on individual file errors** — _Logic & Correctness Auditor_ (deepseek-v3.2)
- **Insecure File Permissions on Embedding Cache** — _Security & Trust Boundary Reviewer_ (gemini-3-flash)
- **Denial of Service via Large Input to Embedding Endpoint** — _Security & Trust Boundary Reviewer_ (gemini-3-flash)
- **No error handling for malformed markdown files** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **Inefficient string concatenation in `_extract_learning_text`** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **No retry logic for Ollama API failures** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **Missing incremental refresh based on file modification time** — _Plan Fidelity Checker_ (deepseek-v3.2)
- **Cache TTL configuration not implemented** — _Plan Fidelity Checker_ (deepseek-v3.2)
- **Fragile Title Extraction Logic** — _Test & Coverage Verifier_ (gemini-3-flash)
- **Missing Timeout on Ollama API Calls** — _Test & Coverage Verifier_ (gemini-3-flash)
- **Fragile CLI argument parsing** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)
- **Cache file existence not handled** — _Integration & Contract Compliance Reviewer_ (qwen-3.5-27b)
- **Cache refresh does not implement incremental logic as documented** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)
- **No deduplication between semantic and keyword results** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)
- **Missing error handling for cache file operations** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)

### LOW

- **Potential integer overflow in similarity score calculation** — _Logic & Correctness Auditor_ (deepseek-v3.2)
- **`--refresh-cache` flag bypasses normal argument parsing order** — _Logic & Correctness Auditor_ (deepseek-v3.2)
- **Path Traversal Risk in Cache Key Resolution** — _Security & Trust Boundary Reviewer_ (gemini-3-flash)
- **Hardcoded model name in `embed_text`** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **No progress feedback during cache refresh** — _Performance & Resource Efficiency Analyst_ (mistral-large)
- **Embedding target fields concatenation format differs from spec** — _Plan Fidelity Checker_ (deepseek-v3.2)
- **Unplanned addition: `--refresh-cache` flag does not require `--query`** — _Plan Fidelity Checker_ (deepseek-v3.2)
- **Generic variable name `cache` lacks specificity** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)
- **Print statements used for progress instead of logging** — _Code Health & Maintainability Inspector_ (qwen-3.5-27b)

### Reviewer Top Recommendations

**Logic & Correctness Auditor** (deepseek-v3.2):
  1. **Ensure semantic search failure is clearly communicated to the user** — when Ollama is unavailable, the CLI should explicitly state that semantic results are empty and it's falling back, not just print a warning to stderr that might be missed. (Relates to HIGH finding)
  2. **Validate cached embeddings before use** — add a check in `search_semantic` to skip cache entries with missing or malformed embeddings to prevent runtime errors. (Relates to MEDIUM finding on null embedding)
  3. **Add error handling to cache refresh loop** — wrap file processing in try-except to log per-file errors and continue, ensuring robustness. (Relates to MEDIUM finding on silent failure)

**Security & Trust Boundary Reviewer** (gemini-3-flash):
  1. **Harden the Ollama API Interaction**: Restrict the `embed_text` function to only communicate with `127.0.0.1` and implement a timeout to prevent the search tool from hanging indefinitely if the service is unresponsive.
  2. **Secure the Cache File**: Ensure `logs/cache/vault_embeddings.json` is created with restrictive permissions (0600) to prevent other local users from reading the indexed "thesis" lines of private vault documents.
  3. **Input Validation for Embeddings**: Truncate the text sent to the embedding model. Large inputs can cause significant latency or memory exhaustion in local inference engines like Ollama.

**Performance & Resource Efficiency Analyst** (mistral-large):
  1. **Implement cache eviction and compression** to prevent unbounded memory growth in the embedding cache. This is critical to avoid outages as the vault grows. (Relates to [CRITICAL] Unbounded memory growth in embedding cache)
  2. **Batch Ollama embedding requests** to reduce network overhead and improve performance during cache refresh. This will significantly speed up the embedding process for large vaults. (Relates to [HIGH] No batching in Ollama embedding requests)
  3. **Cache the list of markdown files** to avoid O(n) file I/O operations during semantic search. This will improve query latency and reduce filesystem load. (Relates to [HIGH] O(n) file I/O in `_iter_markdown_files`)
  ---

**Plan Fidelity Checker** (deepseek-v3.2):
  1. **Fix the semantic results display format** to match the specified markdown table (Finding: "Semantic search results display format does not match specification"). This ensures the deliverable meets the documented user interface.
  2. **Implement incremental cache refresh** as specified by modifying the `--refresh-cache` logic to use `get_stale_files` (Finding: "Missing incremental refresh based on file modification time"). This is a core efficiency requirement.
  3. **Add Cache TTL configuration** as planned (Finding: "Cache TTL configuration not implemented"). This prevents potential use of stale embeddings beyond a reasonable timeframe.

**Test & Coverage Verifier** (gemini-3-flash):
  1. **Unit Test Vector Math**: Add tests for `_cosine_similarity` in `cto_context_lib.py` to verify it handles zero vectors and identical vectors correctly (Finding 1).
  2. **Resilient Cache Writing**: Refactor the `--refresh-cache` loop in `cto_context_search.py` to save incrementally and handle `embed_text` failures without losing all progress (Finding 2).
  3. **Mock Ollama Failures**: Create a test suite that mocks `urllib.error.URLError` and `HTTPError` to verify that the "Warning: Ollama not available" fallback actually triggers without leaking exceptions to the user (Finding 5).

**Integration & Contract Compliance Reviewer** (qwen-3.5-27b):
  1. **Fix `Match` dataclass** — Add `title: str` field to `scripts/cto_context_lib.py` to prevent `AttributeError` in `scripts/cto_context_search.py`.
  2. **Verify library exports** — Confirm `search_semantic`, `ollama_available`, and `embed_text` are defined in `scripts/cto_context_lib.py` before merging to avoid import crashes.
  3. **Add `numpy` to dependencies** — Update `requirements.txt` or `pyproject.toml` to include `numpy` to ensure vector math functions work in clean environments.

**Code Health & Maintainability Inspector** (qwen-3.5-27b):
  1. **Fix the argument parser bypass** — Add `--refresh-cache` as a proper argparse argument so it appears in help text and follows standard CLI patterns (relates to HIGH finding #1)
  2. **Move imports to top of file** — Consolidate all imports at the top for better static analysis and code clarity (relates to HIGH finding #2)
  3. **Implement incremental cache refresh** — Load existing cache, check mtimes, and only re-embed modified files as documented in the plan (relates to MEDIUM finding #3)

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