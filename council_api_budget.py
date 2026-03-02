#!/usr/bin/env python3
"""
Persona Council — Budget API stack via OpenRouter.

4 models × 7 personas. Optimized production stack after Experiments 3-4.
Dropped: Llama 4 Maverick (0% compliance), Kimi K2.5 (too slow), GPT 5.1 Codex Mini (token limit).
DeepSeek V3.2, Qwen 3.5-27B, and Gemini Flash 3.0 each serve 2 personas. ~$0.03/run.

Usage:
  python3 council_api_budget.py --plan path/to/plan.md --scenario prd --repo /path/to/project
  python3 council_api_budget.py --plan path/to/plan.md --scenario dev-plan --repo /path/to/project
"""

import argparse
import asyncio
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print("ERROR: httpx required. Install: pip install httpx", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"
PERSONAS_DIR = CONFIG_DIR / "personas"
OUTPUT_DIR = SCRIPT_DIR / "output"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_CONCURRENT = 4
MAX_OUTPUT_TOKENS = 4096
TEMPERATURE = 0.3
API_TIMEOUT = 120
TRANSPORT_RETRIES = 2
CONTRACT_RETRIES = 1

REQUIRED_SECTIONS = [
    "Findings",
    "Top 3 Recommendations",
    "What I Might Be Wrong About",
]
SEVERITY_TAGS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
MIN_FINDINGS = 2

# --- Budget model configs (optimized production stack) ---
# Tier 1: DeepSeek V3.2, Qwen 3.5-27B, Gemini Flash 3.0
# Tier 2: Mistral Large 2512
# Dropped: GPT 5.1 Codex Mini (hits 4096 token limit, 25% compliance),
#           Llama 4 Maverick (can't follow output format, 0% compliance),
#           Kimi K2.5 (too slow via API, hits token limit)

MODELS = {
    "deepseek-v3.2":      {"id": "deepseek/deepseek-v3.2",          "in": 0.25,  "out": 0.40},
    "qwen-3.5-27b":       {"id": "qwen/qwen3.5-27b",                "in": 0.20,  "out": 0.60},
    "gemini-3-flash":     {"id": "google/gemini-3-flash-preview",    "in": 0.50,  "out": 3.00},
    "mistral-large":      {"id": "mistralai/mistral-large-2512",     "in": 0.50,  "out": 1.50},
}

# --- Scenario configs: 7 personas × 4 models ---
# DeepSeek V3.2 × 2, Qwen 3.5-27B × 2, Gemini Flash 3.0 × 2, Mistral Large × 1

SCENARIOS = {
    "prd": [
        {"persona": "requirements-archaeologist", "model": "gemini-3-flash",       "label": "Requirements Archaeologist"},
        {"persona": "spec-prosecutor",            "model": "deepseek-v3.2",        "label": "Spec Prosecutor"},
        {"persona": "testability-auditor",         "model": "gemini-3-flash",       "label": "Testability Auditor"},
        {"persona": "edge-case-hunter",            "model": "qwen-3.5-27b",        "label": "Edge Case Hunter"},
        {"persona": "qa-test-case-reviewer",       "model": "deepseek-v3.2",        "label": "QA Test Case Reviewer"},
        {"persona": "acceptance-criteria-engineer", "model": "qwen-3.5-27b",       "label": "Acceptance Criteria Engineer"},
        {"persona": "dependency-risk-mapper",      "model": "mistral-large",        "label": "Dependency & Integration Risk Mapper"},
    ],
    "dev-plan": [
        {"persona": "architecture-stress-tester",  "model": "gemini-3-flash",       "label": "Architecture Stress Tester"},
        {"persona": "deployment-risk-assessor",    "model": "deepseek-v3.2",        "label": "Deployment Risk Assessor"},
        {"persona": "observability-advocate",      "model": "gemini-3-flash",       "label": "Observability Advocate"},
        {"persona": "coupling-detector",           "model": "qwen-3.5-27b",        "label": "Coupling Detector"},
        {"persona": "estimate-calibrator",         "model": "deepseek-v3.2",        "label": "Estimate Calibrator"},
        {"persona": "test-qa-strategy-auditor",    "model": "qwen-3.5-27b",        "label": "Test & QA Strategy Auditor"},
        {"persona": "dependency-risk-mapper",      "model": "mistral-large",        "label": "Dependency & Integration Risk Mapper"},
    ],
    "execution": [
        {"persona": "logic-correctness-auditor",       "model": "deepseek-v3.2",   "label": "Logic & Correctness Auditor"},
        {"persona": "security-trust-reviewer",          "model": "gemini-3-flash",  "label": "Security & Trust Boundary Reviewer"},
        {"persona": "performance-resource-analyst",     "model": "mistral-large",   "label": "Performance & Resource Efficiency Analyst"},
        {"persona": "plan-fidelity-checker",            "model": "deepseek-v3.2",   "label": "Plan Fidelity Checker"},
        {"persona": "test-coverage-verifier",           "model": "gemini-3-flash",  "label": "Test & Coverage Verifier"},
        {"persona": "code-health-inspector",            "model": "qwen-3.5-27b",   "label": "Code Health & Maintainability Inspector"},
        {"persona": "integration-contract-reviewer",    "model": "qwen-3.5-27b",   "label": "Integration & Contract Compliance Reviewer"},
    ],
}

# --- Helpers (same as council_api.py) ---


def get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def load_persona(scenario: str, name: str) -> str:
    path = PERSONAS_DIR / scenario / f"{name}.md"
    if not path.exists():
        print(f"  ERROR: Persona file missing: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text()


def build_repo_context(repo_path: str | None, plan_text: str) -> str:
    """Read files relevant to the plan and inject contents into prompt."""
    if not repo_path:
        return ""

    repo = Path(repo_path)

    path_pattern = r'[`"]([a-zA-Z0-9_/\-\.]+\.(py|ts|js|yml|yaml|toml|json|md))[`"]'
    mentioned = set(re.findall(path_pattern, plan_text))
    mentioned_files = [m[0] for m in mentioned]

    found_files = []
    for rel_path in mentioned_files:
        full = repo / rel_path
        if full.exists() and full.is_file():
            found_files.append(full)

    if len(found_files) < 3:
        key_patterns = ["*.py", "*.ts", "*.js"]
        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".obsidian"}
        for pattern in key_patterns:
            for f in repo.rglob(pattern):
                if any(skip in f.parts for skip in skip_dirs):
                    continue
                if f not in found_files:
                    found_files.append(f)
                if len(found_files) >= 5:
                    break
            if len(found_files) >= 5:
                break

    if not found_files:
        return _build_repo_brief(repo_path)

    lines = ["## Repo Context (pre-loaded file contents)\n"]
    lines.append("The following files have been pre-loaded from the target repository.")
    lines.append("Use these to ground your analysis. Do NOT request additional files.\n")

    for f in found_files[:5]:
        rel = f.relative_to(repo)
        try:
            content = f.read_text(errors="replace")
            content_lines = content.split("\n")
            if len(content_lines) > 200:
                content = "\n".join(content_lines[:200])
                content += f"\n\n... (truncated, {len(content_lines)} total lines)"
            lines.append(f"### `{rel}`\n")
            lines.append(f"```\n{content}\n```\n")
        except Exception:
            lines.append(f"### `{rel}`\n")
            lines.append("(could not read file)\n")

    return "\n".join(lines)


def _build_repo_brief(repo_path: str | None) -> str:
    if not repo_path:
        return ""
    repo = Path(repo_path)
    lines = ["## Repo Context Brief (file list only)\n"]
    key_patterns = ["*.py", "*.ts", "*.js", "*.yml", "*.yaml", "*.toml", "*.json"]
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".obsidian"}
    files = []
    for pattern in key_patterns:
        for f in repo.rglob(pattern):
            if any(skip in f.parts for skip in skip_dirs):
                continue
            files.append(str(f.relative_to(repo)))
            if len(files) >= 30:
                break
        if len(files) >= 30:
            break
    if files:
        lines.append("Key files in repo:")
        for f in sorted(files)[:30]:
            lines.append(f"- `{f}`")
    return "\n".join(lines)


def validate_review(output: str) -> tuple[bool, list[str]]:
    """Upgraded validation: sections + severity tags + minimum findings."""
    issues = []
    lower = output.lower()

    for s in REQUIRED_SECTIONS:
        if s.lower() not in lower:
            issues.append(f"missing section: {s}")

    has_severity = any(f"[{s}]" in output for s in SEVERITY_TAGS)
    if not has_severity:
        issues.append("no severity-tagged findings")

    finding_count = sum(output.count(f"[{s}]") for s in SEVERITY_TAGS)
    if finding_count < MIN_FINDINGS:
        issues.append(f"only {finding_count} findings (min {MIN_FINDINGS})")

    return (len(issues) == 0, issues)


# --- API dispatch ---

@dataclass
class ReviewResult:
    label: str
    model_key: str
    model_id: str
    status: str
    output: str
    duration: float
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    retried: bool = False
    validation_issues: list = field(default_factory=list)


async def call_openrouter(
    client: httpx.AsyncClient,
    api_key: str,
    model_id: str,
    model_key: str,
    system_prompt: str,
    user_content: str,
    label: str,
) -> ReviewResult:
    """Single API call with transport retry + backoff."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://persona-council.local",
        "X-Title": "Persona Council Budget",
    }

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": TEMPERATURE,
    }

    t0 = time.monotonic()

    for attempt in range(TRANSPORT_RETRIES + 1):
        try:
            resp = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT,
            )

            if resp.status_code == 429:
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"    429 rate limited: {label}, retrying in {wait:.1f}s...")
                await asyncio.sleep(wait)
                continue

            if resp.status_code >= 500:
                wait = 2 ** attempt
                print(f"    {resp.status_code} server error: {label}, retrying in {wait}s...")
                await asyncio.sleep(wait)
                continue

            elapsed = time.monotonic() - t0

            if resp.status_code != 200:
                return ReviewResult(
                    label, model_key, model_id, "error",
                    f"HTTP {resp.status_code}: {resp.text[:500]}",
                    elapsed,
                )

            data = resp.json()
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            usage = data.get("usage", {})

            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            pricing = MODELS.get(model_key, {})
            cost = (
                input_tokens * pricing.get("in", 0) / 1_000_000
                + output_tokens * pricing.get("out", 0) / 1_000_000
            )

            return ReviewResult(
                label, model_key, model_id, "ok", content, elapsed,
                input_tokens, output_tokens, round(cost, 6),
            )

        except httpx.TimeoutException:
            if attempt < TRANSPORT_RETRIES:
                wait = 2 ** attempt
                print(f"    Timeout: {label}, retrying in {wait}s...")
                await asyncio.sleep(wait)
                continue
            return ReviewResult(
                label, model_key, model_id, "timeout", "",
                time.monotonic() - t0,
            )
        except Exception as e:
            return ReviewResult(
                label, model_key, model_id, "error", str(e),
                time.monotonic() - t0,
            )

    return ReviewResult(
        label, model_key, model_id, "error",
        "Exhausted transport retries",
        time.monotonic() - t0,
    )


async def run_one(
    client: httpx.AsyncClient,
    api_key: str,
    model_id: str,
    model_key: str,
    system_prompt: str,
    user_content: str,
    label: str,
    semaphore: asyncio.Semaphore,
) -> ReviewResult:
    async with semaphore:
        return await call_openrouter(
            client, api_key, model_id, model_key,
            system_prompt, user_content, label,
        )


async def run_council(
    scenario: str,
    plan_text: str,
    repo_path: str | None,
) -> list[ReviewResult]:
    """Dispatch all 7 reviewers with validation and retry."""
    api_key = get_api_key()
    reviewers = SCENARIOS[scenario]
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    repo_context = build_repo_context(repo_path, plan_text)

    user_content = ""
    if repo_context:
        user_content += repo_context + "\n\n---\n\n"
    user_content += f"## Document to Review\n\n{plan_text}"

    tasks_data = []
    for r in reviewers:
        persona_text = load_persona(scenario, r["persona"])
        model_cfg = MODELS[r["model"]]
        tasks_data.append({
            "model_key": r["model"],
            "model_id": model_cfg["id"],
            "system_prompt": persona_text,
            "user_content": user_content,
            "label": r["label"],
        })

    print(f"  Dispatching {len(tasks_data)} reviewers (max {MAX_CONCURRENT} concurrent)...")

    async with httpx.AsyncClient() as client:
        coros = [
            run_one(
                client, api_key,
                t["model_id"], t["model_key"],
                t["system_prompt"], t["user_content"],
                t["label"], semaphore,
            )
            for t in tasks_data
        ]
        results = list(await asyncio.gather(*coros))

    for r in results:
        status_icon = "ok" if r.status == "ok" else r.status.upper()
        print(f"  [{status_icon}] {r.label} ({r.model_key}) — {r.duration:.1f}s")

    # Validate + retry
    final = []
    retry_needed = []

    for i, result in enumerate(results):
        if result.status == "ok":
            passed, issues = validate_review(result.output)
            if passed:
                final.append(result)
            else:
                result.validation_issues = issues
                retry_needed.append((i, tasks_data[i], result))
        else:
            final.append(result)

    if retry_needed:
        print(f"\n  Retrying {len(retry_needed)} reviews (contract validation failed)...")
        async with httpx.AsyncClient() as client:
            for idx, task, orig in retry_needed:
                print(f"  Retry: {orig.label} ({', '.join(orig.validation_issues)})")
                retry_result = await call_openrouter(
                    client, api_key,
                    task["model_id"], task["model_key"],
                    task["system_prompt"], task["user_content"],
                    task["label"],
                )
                retry_result.retried = True

                if retry_result.status == "ok":
                    passed, issues = validate_review(retry_result.output)
                    if passed:
                        final.append(retry_result)
                    else:
                        retry_result.status = "invalid"
                        retry_result.validation_issues = issues
                        final.append(retry_result)
                else:
                    final.append(retry_result)

    return final


# --- Output ---

def write_output(
    scenario: str,
    plan_path: str,
    repo_path: str | None,
    results: list[ReviewResult],
    wall_time: float,
) -> tuple[Path, Path, Path]:
    """Write full review, synthesis, and metrics."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d-%H%M%S")

    ok_count = sum(1 for r in results if r.status == "ok")
    total_cost = sum(r.cost_usd for r in results)
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)

    lines = [
        f"# Persona Council Review (Budget API): {scenario}",
        "",
        f"**Plan:** `{plan_path}`",
    ]
    if repo_path:
        lines.append(f"**Repo:** `{repo_path}`")
    lines.extend([
        f"**Date:** {timestamp}",
        f"**Stack:** Budget (4 models, 7 personas, optimized)",
        f"**Reviewers:** {len(results)} ({ok_count} passed)",
        f"**Execution:** parallel (max {MAX_CONCURRENT})",
        f"**Wall time:** {wall_time:.1f}s",
        f"**Total cost:** ${total_cost:.4f}",
        f"**Total tokens:** {total_in} in / {total_out} out",
        "",
        "## Summary",
        "",
        "| # | Reviewer | Model | Status | Time | Tokens (in/out) | Cost | Retried |",
        "|---|----------|-------|--------|------|-----------------|------|---------|",
    ])

    for i, r in enumerate(results, 1):
        status_str = r.status.upper()
        if r.status == "invalid" and r.validation_issues:
            status_str = f"INVALID ({', '.join(r.validation_issues[:2])})"
        lines.append(
            f"| {i} | {r.label} | {r.model_key} | {status_str} | "
            f"{r.duration:.1f}s | {r.input_tokens}/{r.output_tokens} | "
            f"${r.cost_usd:.4f} | {'yes' if r.retried else 'no'} |"
        )

    lines.extend(["", "---", ""])

    for r in results:
        lines.append(f"## {r.label} ({r.model_key})")
        lines.append("")
        if r.status == "ok":
            lines.append(r.output)
        elif r.status == "invalid":
            lines.append(f"> **INVALID** — {', '.join(r.validation_issues)}")
            lines.append("")
            lines.append("Raw output preserved below:")
            lines.append("")
            lines.append(r.output)
        else:
            lines.append(f"> **{r.status.upper()}**: {r.output[:500]}")
        lines.extend(["", "---", ""])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{scenario}-budget-{ts_file}.md"
    output_path.write_text("\n".join(lines))

    synthesis_path = OUTPUT_DIR / f"{scenario}-budget-{ts_file}-synthesis.md"
    synthesis_path.write_text(write_synthesis(results, plan_path, wall_time))

    metrics_path = OUTPUT_DIR / f"{scenario}-budget-{ts_file}-metrics.json"
    metrics_path.write_text(json.dumps(build_metrics(results, wall_time), indent=2))

    return output_path, synthesis_path, metrics_path


def write_synthesis(results: list[ReviewResult], plan_path: str, wall_time: float) -> str:
    """Condensed synthesis brief."""
    ok_results = [r for r in results if r.status == "ok"]
    failed = [r for r in results if r.status != "ok"]
    total_cost = sum(r.cost_usd for r in results)

    lines = [
        "# Council Synthesis Brief (Budget API)",
        "",
        f"**Source:** {plan_path}",
        f"**Reviewers:** {len(ok_results)}/{len(results)} completed | {wall_time:.1f}s | ${total_cost:.4f}",
        "",
    ]

    if failed:
        lines.append(f"**Failed reviewers:** {', '.join(f'{r.label} ({r.status})' for r in failed)}")
        lines.append("")

    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    all_findings = {s: [] for s in severity_order}

    for r in ok_results:
        for sev in severity_order:
            pattern = rf'\*\*\[{sev}\]\s+(.+?)\*\*'
            matches = re.findall(pattern, r.output)
            for title in matches:
                all_findings[sev].append({
                    "title": title.strip(),
                    "reviewer": r.label,
                    "model": r.model_key,
                })

    total_findings = sum(len(v) for v in all_findings.values())
    counts = " | ".join(f"{s}: {len(all_findings[s])}" for s in severity_order if all_findings[s])
    lines.append(f"**Total findings:** {total_findings} ({counts})")
    lines.append("")

    for sev in severity_order:
        findings = all_findings[sev]
        if not findings:
            continue
        lines.append(f"### {sev}")
        lines.append("")
        for f in findings:
            lines.append(f"- **{f['title']}** — _{f['reviewer']}_ ({f['model']})")
        lines.append("")

    lines.append("### Reviewer Top Recommendations")
    lines.append("")
    for r in ok_results:
        lines.append(f"**{r.label}** ({r.model_key}):")
        top3_match = re.search(
            r'###?\s*Top 3 Recommendations\s*\n(.*?)(?=\n###|\n##|\Z)',
            r.output, re.DOTALL,
        )
        if top3_match:
            for line in top3_match.group(1).strip().split("\n"):
                if line.strip():
                    lines.append(f"  {line.strip()}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Instructions for Primary Agent",
        "",
        "You are receiving this synthesis from a 7-persona review council (budget API stack, 5 models).",
        "Process these findings as follows:",
        "",
        "1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan.",
        "2. **Discredit**: If a finding is wrong (reviewer lacked context), note why and discard it.",
        "3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge.",
        "4. **Prioritize**: Rank validated findings by implementation impact.",
        "5. **Act**: Fix the plan or document why the risk is accepted.",
        "",
        "Do NOT blindly accept all findings. These are cheap models with focused prompts —",
        "they catch real issues but also produce false positives. Your job is to be the judge.",
    ])

    return "\n".join(lines)


def build_metrics(results: list[ReviewResult], wall_time: float) -> dict:
    return {
        "stack": "budget",
        "wall_time_s": round(wall_time, 1),
        "total_cost_usd": round(sum(r.cost_usd for r in results), 4),
        "total_input_tokens": sum(r.input_tokens for r in results),
        "total_output_tokens": sum(r.output_tokens for r in results),
        "reviewers": [
            {
                "label": r.label,
                "model": r.model_key,
                "model_id": r.model_id,
                "status": r.status,
                "duration_s": round(r.duration, 1),
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cost_usd": r.cost_usd,
                "retried": r.retried,
            }
            for r in results
        ],
    }


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Persona Council — Budget API stack via OpenRouter (4 models, 7 personas)"
    )
    parser.add_argument("--plan", required=True, help="Path to the document to review")
    parser.add_argument("--scenario", required=True, choices=list(SCENARIOS.keys()),
                        help="Review scenario (prd or dev-plan)")
    parser.add_argument("--repo", default=None,
                        help="Target repo path for code-grounded context injection")

    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    plan_text = plan_path.read_text()

    print(f"Council (Budget API): {args.scenario} | {len(SCENARIOS[args.scenario])} reviewers | "
          f"max {MAX_CONCURRENT} concurrent")
    print(f"Plan: {plan_path} ({len(plan_text)} chars)")
    if args.repo:
        print(f"Repo: {args.repo}")

    print(f"\nModel lineup:")
    for r in SCENARIOS[args.scenario]:
        model_cfg = MODELS[r["model"]]
        print(f"  {r['label']:42s} → {r['model']} ({model_cfg['id']})")
    print()

    t0 = time.monotonic()
    results = asyncio.run(run_council(args.scenario, plan_text, args.repo))
    wall_time = time.monotonic() - t0

    output_path, synthesis_path, metrics_path = write_output(
        args.scenario, str(plan_path), args.repo, results, wall_time,
    )

    ok = sum(1 for r in results if r.status == "ok")
    total = len(results)
    total_cost = sum(r.cost_usd for r in results)

    print(f"\nDone: {ok}/{total} passed | {wall_time:.1f}s wall time | ${total_cost:.4f}")
    print(f"Full output:  {output_path}")
    print(f"Synthesis:    {synthesis_path}")
    print(f"Metrics:      {metrics_path}")

    failed = sum(1 for r in results if r.status in ("error", "timeout", "invalid"))
    if failed > total // 2:
        print("\nWARNING: >50% reviews failed. Results unreliable.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
