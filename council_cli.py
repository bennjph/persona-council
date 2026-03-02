#!/usr/bin/env python3
"""
Persona Council — CLI-based multi-persona review dispatcher.

Dispatches reviews to Codex CLI and OpenCode CLI in bounded-parallel execution.
Each reviewer gets a rich persona prompt + plan content.

Usage:
  python3 council_cli.py --plan path/to/plan.md --scenario prd --repo /path/to/project
  python3 council_cli.py --plan path/to/plan.md --scenario dev-plan --repo /path/to/project
  python3 council_cli.py --plan path/to/plan.md --scenario prd --sequential

Cost: $0/review (uses existing Codex + Kimi subscriptions)
"""

import argparse
import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"
PERSONAS_DIR = CONFIG_DIR / "personas"
OUTPUT_DIR = SCRIPT_DIR / "output"

MAX_CONCURRENT = 4
RETRY_BUDGET = 1
TIMEOUT_S = 300

REQUIRED_SECTIONS = [
    "Findings",
    "Top 3 Recommendations",
    "What I Might Be Wrong About",
]

# --- Scenario configs ---

SCENARIOS = {
    "prd": [
        {"persona": "requirements-archaeologist", "cli": "codex", "label": "Requirements Archaeologist"},
        {"persona": "spec-prosecutor",            "cli": "codex", "label": "Spec Prosecutor"},
        {"persona": "testability-auditor",         "cli": "codex", "label": "Testability Auditor"},
        {"persona": "edge-case-hunter",            "cli": "opencode", "label": "Edge Case Hunter"},
        {"persona": "qa-test-case-reviewer",       "cli": "opencode", "label": "QA Test Case Reviewer"},
        {"persona": "acceptance-criteria-engineer", "cli": "opencode", "label": "Acceptance Criteria Engineer"},
    ],
    "dev-plan": [
        {"persona": "architecture-stress-tester",  "cli": "codex", "label": "Architecture Stress Tester"},
        {"persona": "deployment-risk-assessor",    "cli": "codex", "label": "Deployment Risk Assessor"},
        {"persona": "observability-advocate",      "cli": "codex", "label": "Observability Advocate"},
        {"persona": "coupling-detector",           "cli": "opencode", "label": "Coupling Detector"},
        {"persona": "estimate-calibrator",         "cli": "opencode", "label": "Estimate Calibrator"},
        {"persona": "test-qa-strategy-auditor",    "cli": "opencode", "label": "Test & QA Strategy Auditor"},
    ],
}

# --- Helpers ---

def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def load_persona(scenario: str, name: str) -> str:
    path = PERSONAS_DIR / scenario / f"{name}.md"
    if not path.exists():
        print(f"  ERROR: Persona file missing: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text()


def build_repo_brief(repo_path: str | None) -> str:
    """Build a short context brief from the repo so agents don't need to explore."""
    if not repo_path:
        return ""

    repo = Path(repo_path)
    lines = ["## Repo Context Brief (pre-computed — do NOT explore beyond these files)\n"]

    # Find key files: scripts, configs, CI, tests (max 30 entries)
    key_patterns = ["*.py", "*.ts", "*.js", "*.yml", "*.yaml", "*.toml", "*.json"]
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".obsidian"}
    files = []
    for pattern in key_patterns:
        for f in repo.rglob(pattern):
            if any(skip in f.parts for skip in skip_dirs):
                continue
            rel = f.relative_to(repo)
            files.append(str(rel))
            if len(files) >= 30:
                break
        if len(files) >= 30:
            break

    if files:
        lines.append("Key files in repo:")
        for f in sorted(files)[:30]:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append("IMPORTANT: Only read files from this list that are directly relevant to the plan.")
        lines.append("Do NOT scan directories or read more than 3-5 files total.")

    return "\n".join(lines)


def assemble_prompt(persona_text: str, plan_text: str, repo_brief: str = "") -> str:
    parts = [persona_text]
    if repo_brief:
        parts.append(f"\n---\n\n{repo_brief}")
    parts.append(f"\n---\n\n## Document to Review\n\n{plan_text}")
    return "\n".join(parts)


SEVERITY_TAGS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
MIN_FINDINGS = 2


def validate_review(output: str) -> tuple:
    """Check output contract compliance. Returns (passed, issues)."""
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


# --- Preflight ---

def preflight(repo_path: str | None) -> None:
    """Verify assumptions before running any reviews."""
    errors = []

    # Check CLIs exist
    for cli in ("codex", "opencode"):
        if not shutil.which(cli):
            errors.append(f"CLI not found: {cli}")

    # Check repo path
    if repo_path and not os.path.isdir(repo_path):
        errors.append(f"Repo path does not exist: {repo_path}")

    if errors:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print("Preflight: OK")


# --- CLI dispatch ---

@dataclass
class ReviewResult:
    label: str
    cli: str
    status: str       # ok | error | timeout | invalid
    output: str
    duration: float
    retried: bool = False
    missing_sections: list = None


async def run_one(
    cli: str,
    prompt: str,
    label: str,
    repo_path: str | None,
    semaphore: asyncio.Semaphore,
) -> ReviewResult:
    """Run a single CLI review with semaphore-bounded concurrency."""
    async with semaphore:
        return await _exec_cli(cli, prompt, label, repo_path)


async def _exec_cli(
    cli: str,
    prompt: str,
    label: str,
    repo_path: str | None,
) -> ReviewResult:
    """Execute a single CLI subprocess."""
    t0 = time.monotonic()

    if cli == "codex":
        cmd = ["codex", "exec", "-s", "read-only", "-m", "gpt-5.3-codex"]
        if repo_path:
            cmd.extend(["-C", repo_path])
        cmd.append("-")
        stdin_bytes = prompt.encode()
    elif cli == "opencode":
        cmd = ["opencode", "run", "-m", "openrouter/moonshotai/kimi-k2.5"]
        if repo_path:
            cmd.extend(["--dir", repo_path])
        cmd.append(prompt)
        stdin_bytes = None
    else:
        return ReviewResult(label, cli, "error", f"Unknown CLI: {cli}", 0.0)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_bytes else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_bytes),
                timeout=TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ReviewResult(label, cli, "timeout", "", time.monotonic() - t0)

        elapsed = time.monotonic() - t0
        output = strip_ansi(stdout.decode(errors="replace")).strip()
        stderr_text = strip_ansi(stderr.decode(errors="replace")).strip()

        if proc.returncode != 0 and not output:
            return ReviewResult(label, cli, "error",
                                f"Exit {proc.returncode}: {stderr_text[:500]}", elapsed)

        return ReviewResult(label, cli, "ok", output, elapsed)

    except FileNotFoundError:
        return ReviewResult(label, cli, "error", f"CLI '{cli}' not found", 0.0)
    except Exception as e:
        return ReviewResult(label, cli, "error", str(e), time.monotonic() - t0)


async def run_council(
    scenario: str,
    plan_text: str,
    repo_path: str | None,
    sequential: bool = False,
) -> list:
    """Dispatch all reviewers with validation and retry."""
    reviewers = SCENARIOS[scenario]
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    # Pre-compute repo brief once (shared by all reviewers)
    repo_brief = build_repo_brief(repo_path)

    # Build prompts
    tasks_data = []
    for r in reviewers:
        persona_text = load_persona(scenario, r["persona"])
        prompt = assemble_prompt(persona_text, plan_text, repo_brief)
        tasks_data.append((r["cli"], prompt, r["label"]))

    # First pass
    if sequential:
        results = []
        for cli, prompt, label in tasks_data:
            print(f"  Dispatching: {label}...")
            result = await _exec_cli(cli, prompt, label, repo_path)
            print(f"  [{result.status}] {label} ({result.duration:.1f}s)")
            results.append(result)
    else:
        print(f"  Dispatching {len(tasks_data)} reviewers (max {MAX_CONCURRENT} concurrent)...")
        coros = [run_one(cli, prompt, label, repo_path, semaphore)
                 for cli, prompt, label in tasks_data]
        results = list(await asyncio.gather(*coros))
        for r in results:
            print(f"  [{r.status}] {r.label} ({r.duration:.1f}s)")

    # Validate + retry
    final = []
    retry_needed = []

    for i, result in enumerate(results):
        if result.status == "ok":
            passed, missing = validate_review(result.output)
            if passed:
                final.append(result)
            else:
                result.missing_sections = missing
                retry_needed.append((i, tasks_data[i], result))
        else:
            final.append(result)

    if retry_needed:
        print(f"\n  Retrying {len(retry_needed)} reviews (missing required sections)...")
        for idx, (cli, prompt, label), orig in retry_needed:
            print(f"  Retry: {label} (missing: {', '.join(orig.missing_sections)})")
            retry_result = await _exec_cli(cli, prompt, label, repo_path)
            retry_result.retried = True

            if retry_result.status == "ok":
                passed, missing = validate_review(retry_result.output)
                if passed:
                    final.append(retry_result)
                else:
                    retry_result.status = "invalid"
                    retry_result.missing_sections = missing
                    final.append(retry_result)
            else:
                final.append(retry_result)

    return final


# --- Output ---

def write_output(
    scenario: str,
    plan_path: str,
    repo_path: str | None,
    results: list,
    wall_time: float,
    parallel: bool,
) -> tuple[Path, Path]:
    """Write structured review output."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d-%H%M%S")

    ok_count = sum(1 for r in results if r.status == "ok")
    invalid_count = sum(1 for r in results if r.status == "invalid")
    error_count = sum(1 for r in results if r.status in ("error", "timeout"))

    lines = [
        f"# Persona Council Review: {scenario}",
        "",
        f"**Plan:** `{plan_path}`",
    ]
    if repo_path:
        lines.append(f"**Repo:** `{repo_path}`")
    lines.extend([
        f"**Date:** {timestamp}",
        f"**Reviewers:** {len(results)} ({ok_count} passed, {invalid_count} invalid, {error_count} failed)",
        f"**Execution:** {'parallel' if parallel else 'sequential'} (max {MAX_CONCURRENT})",
        f"**Wall time:** {wall_time:.1f}s",
        f"**Cost:** $0 (subscription-based)",
        "",
        "## Summary",
        "",
        "| # | Reviewer | CLI | Status | Time | Retried |",
        "|---|----------|-----|--------|------|---------|",
    ])

    for i, r in enumerate(results, 1):
        status_str = r.status.upper()
        if r.status == "invalid" and r.missing_sections:
            status_str = f"INVALID (missing: {', '.join(r.missing_sections)})"
        lines.append(
            f"| {i} | {r.label} | {r.cli} | {status_str} | {r.duration:.1f}s | {'yes' if r.retried else 'no'} |"
        )

    lines.extend(["", "---", ""])

    for r in results:
        lines.append(f"## {r.label} ({r.cli})")
        lines.append("")
        if r.status == "ok":
            lines.append(r.output)
        elif r.status == "invalid":
            lines.append(f"> **INVALID** — missing sections: {', '.join(r.missing_sections or [])}")
            lines.append("")
            lines.append("Raw output preserved below:")
            lines.append("")
            lines.append(r.output)
        else:
            lines.append(f"> **{r.status.upper()}**: {r.output}")
        lines.extend(["", "---", ""])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{scenario}-{ts_file}.md"
    output_path.write_text("\n".join(lines))

    # Write synthesis brief for primary agent consumption
    synthesis_path = OUTPUT_DIR / f"{scenario}-{ts_file}-synthesis.md"
    synthesis_path.write_text(write_synthesis(results, plan_path, wall_time))

    return output_path, synthesis_path


def write_synthesis(results: list, plan_path: str, wall_time: float) -> str:
    """Write a condensed synthesis brief for the primary agent to consume.

    This is the structured input the main agent receives. It should:
    - Be scannable in <30 seconds
    - Group findings by severity across all reviewers
    - Deduplicate overlapping findings
    - Provide a clear action list
    """
    ok_results = [r for r in results if r.status == "ok"]
    failed = [r for r in results if r.status != "ok"]

    lines = [
        "# Council Synthesis Brief",
        "",
        f"**Source:** {plan_path}",
        f"**Reviewers:** {len(ok_results)}/{len(results)} completed | {wall_time:.1f}s",
        "",
    ]

    if failed:
        lines.append(f"**Failed reviewers:** {', '.join(r.label for r in failed)} ({', '.join(r.status for r in failed)})")
        lines.append("")

    # Extract findings by severity from all successful reviews
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    all_findings = {s: [] for s in severity_order}

    for r in ok_results:
        for sev in severity_order:
            # Find findings blocks matching [SEVERITY]
            pattern = rf'\*\*\[{sev}\]\s+(.+?)\*\*'
            matches = re.findall(pattern, r.output)
            for title in matches:
                all_findings[sev].append({"title": title.strip(), "reviewer": r.label})

    # Count
    total_findings = sum(len(v) for v in all_findings.values())
    counts = " | ".join(f"{s}: {len(all_findings[s])}" for s in severity_order if all_findings[s])
    lines.append(f"**Total findings:** {total_findings} ({counts})")
    lines.append("")

    # List findings grouped by severity
    for sev in severity_order:
        findings = all_findings[sev]
        if not findings:
            continue
        lines.append(f"### {sev}")
        lines.append("")
        for f in findings:
            lines.append(f"- **{f['title']}** — _{f['reviewer']}_")
        lines.append("")

    # Top 3 recommendations from each reviewer
    lines.append("### Reviewer Top Recommendations")
    lines.append("")
    for r in ok_results:
        lines.append(f"**{r.label}:**")
        # Extract the Top 3 section
        top3_match = re.search(
            r'###?\s*Top 3 Recommendations\s*\n(.*?)(?=\n###|\n##|\Z)',
            r.output, re.DOTALL
        )
        if top3_match:
            for line in top3_match.group(1).strip().split("\n"):
                if line.strip():
                    lines.append(f"  {line.strip()}")
        lines.append("")

    # Instructions for the primary agent
    lines.extend([
        "---",
        "",
        "## Instructions for Primary Agent",
        "",
        "You are receiving this synthesis from a 6-persona review council.",
        "Process these findings as follows:",
        "",
        "1. **Validate**: For each CRITICAL/HIGH finding, verify it against the plan. Is the reviewer correct?",
        "2. **Discredit**: If a finding is wrong (reviewer lacked context, misread the plan), note why and discard it.",
        "3. **Deduplicate**: Multiple reviewers may flag the same issue differently. Merge overlapping findings.",
        "4. **Prioritize**: Rank the validated findings by implementation impact.",
        "5. **Act**: For each validated finding, either fix the plan or document why the risk is accepted.",
        "",
        "Do NOT blindly accept all findings. The council uses cheap models with focused prompts —",
        "they catch real issues but also produce false positives. Your job is to be the judge.",
    ])

    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Persona Council — CLI-based multi-persona review dispatcher"
    )
    parser.add_argument("--plan", required=True, help="Path to the document to review")
    parser.add_argument("--scenario", required=True, choices=list(SCENARIOS.keys()),
                        help="Review scenario (prd or dev-plan)")
    parser.add_argument("--repo", default=None,
                        help="Target repo path for code-grounded personas (codex -C, opencode --dir)")
    parser.add_argument("--sequential", action="store_true",
                        help="Run sequentially instead of parallel")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_S,
                        help=f"Per-reviewer timeout in seconds (default: {TIMEOUT_S})")

    args = parser.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"Error: plan not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    plan_text = plan_path.read_text()
    parallel = not args.sequential

    print(f"Council: {args.scenario} | {len(SCENARIOS[args.scenario])} reviewers | "
          f"{'parallel' if parallel else 'sequential'}")
    print(f"Plan: {plan_path} ({len(plan_text)} chars)")
    if args.repo:
        print(f"Repo: {args.repo}")
    print()

    # Preflight
    preflight(args.repo)
    print()

    # Run
    t0 = time.monotonic()
    results = asyncio.run(
        run_council(args.scenario, plan_text, args.repo, sequential=args.sequential)
    )
    wall_time = time.monotonic() - t0

    # Output
    output_path, synthesis_path = write_output(
        args.scenario, str(plan_path), args.repo,
        results, wall_time, parallel,
    )

    # Summary
    ok = sum(1 for r in results if r.status == "ok")
    invalid = sum(1 for r in results if r.status == "invalid")
    total = len(results)

    print(f"\nDone: {ok}/{total} passed | {wall_time:.1f}s wall time")
    print(f"Full output:  {output_path}")
    print(f"Synthesis:    {synthesis_path}")

    if invalid + sum(1 for r in results if r.status in ("error", "timeout")) > total // 2:
        print("\nWARNING: >50% reviews failed. Results unreliable.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
