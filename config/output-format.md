## Output Format

You MUST use this exact structure. Do not deviate.

### Findings

For each finding, use exactly this structure:

**[SEVERITY] Title**
- Location: [section name from the document, or file:line if reviewing code]
- Issue: [one sentence describing the problem]
- Evidence: [direct quote from the document or code that supports this finding]
- Recommendation: [specific, actionable fix — not vague advice]

Severity levels (use exactly these):
- CRITICAL: Blocks success or causes failure if not addressed
- HIGH: Significant risk or gap that should be addressed before implementation
- MEDIUM: Notable concern that could cause problems later
- LOW: Minor improvement opportunity

### Top 3 Recommendations

1. [Most important action — reference the finding it relates to]
2. [Second most important]
3. [Third most important]

### What I Might Be Wrong About

You MUST include at least 3 items. Be honest about your uncertainty.

- [Assumption you made that could be wrong, and what changes if it is]
- [Area where you lack context that could change your findings]
- [Finding that might be less severe than you rated it, and why]
