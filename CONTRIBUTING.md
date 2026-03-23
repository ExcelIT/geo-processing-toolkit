# Contributing

Thanks for contributing to Geo Processing Toolkit.

Please review and follow `CODE_OF_CONDUCT.md`.

## Principles

- Keep utilities practical and reusable
- Prefer explicit behavior over hidden assumptions
- Preserve CRS and nodata handling carefully
- Add tests for new behavior when possible
- Document CLI usage for every new command

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install --upgrade pip
pip install -e .[dev]
```

## Run tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Pull requests

Please include:

- a short summary of the change
- the motivation/problem addressed
- example command or usage snippet
- tests where applicable

## Issues

When reporting a problem, include:

- input format(s)
- CRS details if relevant
- exact command used
- traceback or error message
- whether the issue is data-specific or reproducible

## Security issues

For sensitive vulnerabilities, do not open a public issue first.
Follow `SECURITY.md` for private reporting guidance.
