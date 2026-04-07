# Repository Guidelines

## Project Structure & Module Organization

This repository is a `uv` workspace monorepo. Core code lives under `packages/*/src`: `packages/agent/src/netdriver_agent` exposes the FastAPI-based agent, `packages/simunet/src/netdriver_simunet` provides simulated SSH devices, and `packages/core`, `packages/discovery`, and `packages/textfsm` hold shared logic. Package-level unit tests live beside each package in `packages/*/tests`. Cross-package and simulator-backed scenarios live in `tests/integration`. Runtime config defaults are in `config/agent` and `config/simunet`; docs live in `docs`, and helper scripts live in `scripts`.

## Build, Test, and Development Commands

- `uv sync --all-packages` — install all workspace dependencies.
- `uv run agent` — start the agent service on the local FastAPI entry point.
- `uv run simunet` — start simulated network devices for local integration work.
- `uv run pytest -m unit` — run unit tests only.
- `uv run pytest --mock-dev -m integration` — run integration tests against `simunet`.
- `uv build --directory packages/agent` or `uv build --directory packages/simunet` — build distributable wheels for release targets.

## Coding Style & Naming Conventions

Target Python is 3.12+. Use 4-space indentation, PEP 8 naming, and explicit Type Hints on new functions and methods. Prefer `async/await` for network or device I/O. Use `snake_case` for modules, functions, and test files; use `PascalCase` for classes. Keep plugin filenames descriptive and consistent with existing patterns such as `cisco_nexus.py` or `huawei_usg.py`. Follow the logging and exception-handling patterns already used in `netdriver_core`; do not introduce `print()` debugging. CI checks rely on `pylint`, and `pyright`/`basedpyright` settings are defined in `pyproject.toml`.

## Testing Guidelines

Tests use `pytest` and `pytest-asyncio`. Mark tests explicitly with `@pytest.mark.unit` or `@pytest.mark.integration`, matching the root pytest configuration. Name files `test_*.py`. Add narrow unit tests under the relevant package first, then add `tests/integration` coverage when behavior depends on agent/simulator interaction. Use `--mock-dev` unless you are intentionally validating against real lab devices.

## Commit & Pull Request Guidelines

Recent history favors short, imperative subjects, sometimes with prefixes like `fix:`, `docs:`, or `refactor(agent):`. Keep the first line under 72 characters and scope each commit to one concern. PRs should state the affected package(s), link related issues, list commands run, and mention config or docs updates. Include request/response examples or screenshots only when they clarify changed behavior.

## Security & Configuration Tips

Never commit real device IPs, usernames, passwords, or tokens. Keep local overrides in `config/*/*.yml` or environment variables, and avoid committing transient `logs/` output unless the default logging setup itself changes.
