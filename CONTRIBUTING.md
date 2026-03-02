# Contributing to Persona Council

Contributions are welcome! Whether it's a new persona, a bug fix, or a feature idea — we'd love your help.

## Adding a New Persona

Personas live in `config/personas/` organized by review phase (`dev-plan`, `execution`, `prd`). Each persona is a Markdown file containing the system prompt that defines its review perspective.

To add one:

1. Pick the appropriate phase directory under `config/personas/`.
2. Create a new `.md` file named after the persona's role (e.g., `accessibility-reviewer.md`).
3. Write a system prompt that defines the persona's expertise, focus areas, and review style.
4. Use the existing personas as examples — keep prompts focused and actionable.

## Adding a New Model

Models are defined in the `MODELS` dict inside `council_api_budget.py`. To add one:

1. Add an entry with the model identifier, provider, and cost parameters.
2. Make sure the provider's API is supported by the existing `httpx` client logic.

## Running Experiments

```bash
# Install dependencies
pip install -r requirements.txt

# Run a council review via CLI
python council_cli.py --help

# Run via API with budget controls
python council_api_budget.py --help
```

## Reporting Issues

Use the [bug report](https://github.com/bennjph/persona-council/issues/new?template=bug_report.md) or [feature request](https://github.com/bennjph/persona-council/issues/new?template=feature_request.md) templates, or just open a blank issue. No wrong way to do it.

## Code Style

- Python 3.10+, asyncio, httpx.
- Keep it simple. This is a small tool, not a framework.
- No strict linter enforced yet — just write clean, readable code.
- If you're touching async code, make sure you're not blocking the event loop.

## Submitting Changes

1. Fork the repo and create a branch.
2. Make your changes.
3. Open a pull request with a short description of what and why.

Thanks for contributing!
