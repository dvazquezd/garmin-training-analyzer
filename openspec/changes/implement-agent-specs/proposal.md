# Proposal: implement-agent-specs

## Why

To ensure the project strictly follows the agent standards defined in `openspec/agents.md` (SOLID, DRY, clean architecture, rigorous testing and secure handling of secrets). The current codebase contains deviations (configuration loaded at import, imperative prints, provider branching with tight coupling, inconsistent templating and validation, scattered responsibility) that reduce testability, maintainability and safety.

## Goals

- Bring codebase into compliance with `openspec/agents.md` and the project's style & quality gates
- Make modules small, testable and well-separated (domain / application / infrastructure)
- Improve test coverage and determinism (mock external dependencies, isolate I/O)
- Introduce small, incremental refactors with clear PR boundaries
- Add or improve CI checks (formatting, linting, tests) and developer docs

## Scope

### In scope (first wave)
- `src/config.py` → Dataclass-based, validated config, CLI overrides, docs, tests
- `src/llm_analizer.py` → Replace prints with logging, introduce LLM provider abstraction/factory, move prompt formatting to `PromptManager` and small formatting helpers, add unit tests
- `src/prompt_manager.py` → Support Jinja2 templates, YAML frontmatter parsing, snippet expansion, sanitize and validate prompts, tests
- `src/garmin_client.py` → Dependency‑inject Garmin adapter, improve error handling (2FA, rate-limit detection), ensure retries and testability
- `src/cache_manager.py` → Add WAL mode, busy timeout, better recovery handling, tests for concurrency
- `src/html_reporter.py` & `src/visualizations.py` → Ensure clean separation of rendering, deterministic outputs, tests for responsive behavior
- Tests: add/update tests under `tests/` (unit/integration as spec requires)

### Out of scope (for this change)
- Full rewrite of large modules; we will prefer incremental, well-tested refactors
- Introducing new runtime dependencies without justification
- UI or web server components (no new web interfaces)

## Deliverables

- Detailed `audit_report.md` mapping agents.md rules → code locations and remediation steps
- Updated `proposal.md` (this document) and `tasks.md` with fine-grained tasks per module
- Implementation PRs (one module / small feature per PR) with tests and changelog
- CI updates to run Black, Flake8, isort and pytest on PRs
- `notes.md` summarizing decisions and trade-offs

## Implementation plan (phased)

1. Audit (2–3 days): scan repository, list violations, rank by severity (P0, P1, P2). Produce `audit_report.md`.
2. Config refactor (1–2 days): implement dataclass config, validation, CLI overrides and tests.
3. Prompt & LLM refactor (2–4 days): harden `PromptManager`, introduce `LLMProvider` abstraction and factory, replace prints with logging, add unit tests and mocks for external providers.
4. Garmin client refactor (2–4 days): introduce adapter interface, improve retry & error handling, tests with mocked `garminconnect`.
5. Cache & visualizations cleanup (1–3 days): WAL/timeout, concurrency tests, ensure deterministic outputs for charts.
6. Reporting & export validation (1–2 days): ensure HTML renderer is robust, add tests for markdown→HTML and base64 embedding.
7. CI & quality gates (1 day): add format/lint/test steps and failing PRs if checks fail.
8. Documentation & final verification (1–2 days): update specs, README, and `openspec` artifacts.

> Each phase will produce one or more small PRs with a descriptive title and clear test coverage. We will not merge large combined PRs to minimize risk.

## Testing strategy

- Follow spec-driven development: write tests matching Given‑When‑Then for each acceptance criterion.
- Use pytest with mocks (monkeypatch / unittest.mock) for external services (garminconnect, LLM clients, filesystem, network).
- Add deterministic fixtures (freezegun for time‑related tests) and avoid reliance on network or real API keys.
- Add unit tests for every refactor and add minimal integration tests where appropriate.

## Success Criteria

- Audit report created and approved in `openspec/changes/implement-agent-specs/audit_report.md` ✅
- Each modified module has focused PR with tests and simple changelog
- All new and existing unit tests pass locally and in CI
- Code passes linting and formatting checks automatically in CI
- No secrets or API keys logged; config validated at startup

## Risks & Mitigations

- Risk: Large refactor introduces regressions. Mitigation: small PRs, robust tests, CI gate, feature toggles where needed.
- Risk: External APIs change behavior. Mitigation: use mocks in tests and retain defensive parsing.
- Risk: Time constraints. Mitigation: prioritize P0 items and defer P1/P2 to follow-up changes.

## Reviewers & Approvals

- Primary reviewers: `@dvazquezd` (repo owner) and `@maintainer` (team lead)
- For LLM/provider changes, include a reviewer with LLM or security experience

## Next steps (immediate)

1. Create `audit_report.md` with initial findings (I will draft it now).  
2. Triage findings and convert the highest‑priority items into tasks in `tasks.md`.  
3. Begin the first PR: `refactor/config-dataclass` (small, test-driven).

---

*If you confirm, I'll add the `audit_report.md` now with an initial prioritized list of findings and proposed fixes so we can start implementing PR #1.*
