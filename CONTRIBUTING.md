# Contributing to Nexarag

Thanks for your interest in contributing! This guide covers how to set up a local development environment, propose changes, and submit pull requests.

## Ways to Contribute
- Report bugs or request features via GitHub Issues.
- Improve documentation.
- Add or refine functionality in the backend, frontend, or knowledge graph components.


## Before You Start
- For small fixes, feel free to jump straight to a PR.
- For larger changes (new features, architecture shifts, major refactors), please open an Issue first to discuss direction and scope.

## Development Setup (Docker Compose)
Local development is done via Docker Compose.

1. Pick the dev compose file that matches your platform (from `docker/dev`):
   - MacOS: `docker-compose.macos.yml`
   - Linux/WSL (CPU): `docker-compose.cpu.yml`
   - Linux/WSL (GPU): `docker-compose.gpu.yml`

2. From `docker/dev`, run:
   - `docker compose -f <compose-file> up -d`

3. Visit the app in your browser (see README for the default URL).

> If you need to work outside Docker (for IDE tooling, debugging, etc.), try to keep changes aligned with the containerized environment and existing project structure.


## Code Style
There is no formal style guide yet. Please follow existing patterns and keep changes consistent with surrounding code.

If you introduce new dependencies or project-wide patterns, explain why in the PR description.

## Tests
Tests are encouraged, but not required in all cases (some LLM-driven behavior can be difficult to test reliably).

When feasible:
- Add or update automated tests.
- Otherwise, include clear manual verification steps in the PR description (what you clicked, what command you ran, expected output).

## Documentation
If your change affects user-facing behavior, configuration, or workflows, update the relevant documentation under docs/.

## Git Workflow
- Fork the repo and create a branch from `main`.
- Keep PRs focused and reasonably sized when possible.
- Open a pull request to `main`.
- Maintainer approval is required before merging.

### PR Guidelines (Lightweight Checklist)
In your PR description, please include:
- What changed, and why
- How you tested it (tests or manual steps)
- Any screenshots or short clips for UI changes (optional but helpful)

## Reporting Issues
Please use GitHub Issues for bugs, feature requests, and questions to keep discussion open and searchable.

### Security
If you believe you’ve found a security vulnerability, please do not open a public Issue. Use the project’s contact email listed in the README instead.

## License
By contributing, you agree that your contributions will be licensed under the repository’s GPL-3.0 license.
