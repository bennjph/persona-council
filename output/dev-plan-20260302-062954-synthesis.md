# Council Synthesis Brief

**Source:** /Users/benison/Documents/Obsidian Vault/cto-mentor/boardroom/plans/2026-03-01-plan-18-semantic-search-ollama.md
**Reviewers:** 6/6 completed | 242.0s

**Total findings:** 46 (CRITICAL: 8 | HIGH: 18 | MEDIUM: 15 | LOW: 5)

### CRITICAL

- **Completion Status Conflicts With Actual Runtime Entry Points** — _Architecture Stress Tester_
- **Ollama Is a Hard Single Point of Failure for Semantic Mode** — _Architecture Stress Tester_
- **No phase-level rollback procedure for refactored search path** — _Deployment Risk Assessor_
- **No phase-level rollback procedure for refactored search path** — _Deployment Risk Assessor_
- **Completion Status Conflicts With Observable Runtime Behavior** — _Observability Advocate_
- **Golden Signals Are Not Defined for the New Ollama Dependency** — _Observability Advocate_
- **No automated tests for semantic search functionality** — _Test & QA Strategy Auditor_
- **No CI pipeline to enforce quality gates** — _Test & QA Strategy Auditor_

### HIGH

- **Query Path Performs Index Maintenance, Creating Latency Spikes and Throughput Collapse** — _Architecture Stress Tester_
- **JSON Cache File Is Shared Mutable State and a Concurrency Bottleneck** — _Architecture Stress Tester_
- **Model/Vector Contract Is Implicit and Fragile** — _Architecture Stress Tester_
- **Scalability Validation Is Missing Critical Throughput and Latency Gates** — _Architecture Stress Tester_
- **Cache schema lacks backward-compatible versioning** — _Deployment Risk Assessor_
- **Full refresh has no last-known-good restore path** — _Deployment Risk Assessor_
- **Output contract change can cascade to downstream tooling** — _Deployment Risk Assessor_
- **Cache schema lacks backward-compatible versioning** — _Deployment Risk Assessor_
- **Output contract change can cascade to downstream tooling** — _Deployment Risk Assessor_
- **Logging Plan Is Not Incident-Grade (No Structured Context or Correlation ID)** — _Observability Advocate_
- **Metrics Are Proposed Without Paging/Warning Thresholds** — _Observability Advocate_
- **Trace Context Is Not Propagated Across the HTTP Boundary** — _Observability Advocate_
- **Hidden Cache Format Coupling** — _Coupling Detector_
- **Temporal Coupling in Ollama Availability Check** — _Coupling Detector_
- **Single-number estimates lack decomposition** — _Estimate Calibrator_
- **Zero contingency for discovery work** — _Estimate Calibrator_
- **Test environment dependency on live Ollama service** — _Test & QA Strategy Auditor_
- **No error handling tests for embedding failures** — _Test & QA Strategy Auditor_

### MEDIUM

- **Global TTL Introduces Temporal Coupling and Herd Behavior** — _Architecture Stress Tester_
- **Retrieval Signal Is Too Thin for 10x/100x Corpus Growth** — _Architecture Stress Tester_
- **Multi-Copy Script Topology Creates Lock-In and Rewrite Risk** — _Architecture Stress Tester_
- **Fallback behavior is graceful but operationally silent** — _Deployment Risk Assessor_
- **Feature gating is caller-controlled, not operator-controlled** — _Deployment Risk Assessor_
- **Partial indexing risk is unbounded** — _Deployment Risk Assessor_
- **Incident Simulation Path Is Incomplete** — _Observability Advocate_
- **Saturation Control for Refresh Work Is Undefined** — _Observability Advocate_
- **Conditional Import Creates Hidden Dependency** — _Coupling Detector_
- **Hardcoded Model Defaults Create Cross-Module Coupling** — _Coupling Detector_
- **Shared Global State for Cache Directory** — _Coupling Detector_
- **Text extraction complexity underestimated** — _Estimate Calibrator_
- **Missing test coverage in estimates** — _Estimate Calibrator_
- **Cache file I/O has no tests for atomic write failures** — _Test & QA Strategy Auditor_
- **Missing test for cache TTL behavior** — _Test & QA Strategy Auditor_

### LOW

- **Capacity Planning Math Is Internally Inconsistent** — _Architecture Stress Tester_
- **Validation omits rollback drill and recovery SLO** — _Deployment Risk Assessor_
- **Duplicate File Discovery Logic** — _Coupling Detector_
- **Cache size estimate 6.7x off** — _Estimate Calibrator_
- **No regression tests for keyword search after semantic additions** — _Test & QA Strategy Auditor_

### Reviewer Top Recommendations

**Architecture Stress Tester:**
  1. Establish one canonical semantic-search runtime and enforce parity across all script copies with CI checks (Findings: Completion Status Conflicts, Multi-Copy Topology).
  2. Decouple indexing from query execution and replace single JSON cache with a concurrent, versioned store (Findings: Query Path Index Maintenance, Shared Mutable Cache, Model Contract Fragility, TTL Herding).
  3. Add scale gates before rollout: concurrency load tests, p95/p99 SLOs, and degraded-mode observability for Ollama outages (Findings: Ollama SPOF, Missing Scalability Validation).

**Deployment Risk Assessor:**
  1. Add a phase-by-phase rollback runbook with explicit irreversible checkpoints and timed recovery validation (Finding: **[CRITICAL] No phase-level rollback procedure for refactored search path**).
  2. Version the embedding cache format and support dual-read compatibility before any rollout (Finding: **[HIGH] Cache schema lacks backward-compatible versioning**).
  3. Protect downstream consumers with output versioning and contract tests before enabling hybrid semantic output (Finding: **[HIGH] Output contract change can cascade to downstream tooling**).

**Observability Advocate:**
  1. Define and implement full golden-signal instrumentation for the semantic/Ollama path before rollout (Finding: **Golden Signals Are Not Defined for the New Ollama Dependency**).
  2. Add explicit warning and paging thresholds tied to those metrics, with on-call ownership (Finding: **Metrics Are Proposed Without Paging/Warning Thresholds**).
  3. Enforce structured logs plus end-to-end trace correlation IDs across CLI, cache, and Ollama calls (Findings: **Logging Plan Is Not Incident-Grade** and **Trace Context Is Not Propagated Across the HTTP Boundary**).

**Coupling Detector:**
  1. **Create explicit CacheEntry dataclass with model versioning** — addresses HIGH cache format coupling and MEDIUM model default coupling
  2. **Remove conditional imports and either move all to top or extract `--refresh-cache` to separate script** — addresses HIGH temporal coupling and MEDIUM hidden dependency
  3. **Add cache format version field and validation** — prevents silent failures when model or format changes

**Estimate Calibrator:**
  1. **Add 20% contingency buffer (1 day)** — Plan has zero slack for Ollama setup issues, API debugging, or cache corruption scenarios.
  2. **Decompose estimates into sub-tasks with tests** — Break Phase 1 into: embed function (0.5 day), cache management (0.5 day), text extraction (0.75 day), tests (1 day).
  3. **Upgrade Phase 1 effort from 2/10 to 3/10** — Text extraction logic (`_extract_learning_text`) is significantly more complex than plan implies, handling YAML frontmatter and multiple fallbacks.

**Test & QA Strategy Auditor:**
  1. **Block merge until CI pipeline created with Ollama mocking** — The CRITICAL finding on missing CI means no quality enforcement exists; create `.github/workflows/ci.yml` with pytest and mocked Ollama responses before considering this complete.
  2. **Require minimum 70% unit test coverage for semantic search module** — The CRITICAL finding on zero tests means regression risk is unbounded; prioritize tests for `embed_text()` failure modes and `search_semantic()` integration paths.
  3. **Implement test doubles for Ollama dependency** — The HIGH finding on live service dependency blocks CI execution; extract HTTP client into injectable class with mock implementation.

---

## Instructions for Primary Agent

You are receiving this synthesis from a 6-persona review council.
Process these findings as follows:

1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan. Is the reviewer correct?
2. **Discredit**: If a finding is wrong (reviewer lacked context, misread the plan), note why and discard it.
3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge overlapping findings.
4. **Prioritize**: Rank the validated findings by implementation impact.
5. **Act**: For each validated finding, either fix the plan or document why the risk is accepted.

Do NOT blindly accept all findings. The council uses cheap models with focused prompts —
they catch real issues but also produce false positives. Your job is to be the judge.