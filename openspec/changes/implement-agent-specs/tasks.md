# Tasks: implement-agent-specs

- [x] Audit repository files and produce `audit_report.md` mapping agents.md rules → code locations
- [x] Create per-module minimal refactor tasks (one commit / PR per module)
  - [x] `refactor/config-dataclass` → implement dataclass config + tests (DONE: bc6d80f, c2533ca)
  - [x] `refactor/llm-provider-abstraction` → factory + DI + tests (DONE: bc6d80f, d6bfb09, 0eff692)
  - [ ] `refactor/prompt-manager-improvements` → jinja2, frontmatter, snippets, sanitization tests (OPTIONAL)
  - [ ] `refactor/garmin-adapter` → GarminAdapter + 2FA/rate-limit handling tests (OPTIONAL)
  - [ ] `refactor/cache-hardening` → WAL, busy_timeout, corruption recovery tests (OPTIONAL)
  - [ ] `refactor/html-reporter-contracts` → input contracts & rendering tests (OPTIONAL)
- [x] Add/extend tests for each scenario found in audit (pytest, mocks, freezegun where needed) - 50 tests passing
- [ ] Add linter/formatter configuration and CI checks (Black, Flake8, isort) and enable as required status checks
- [ ] Add documentation updates and `changes/implement-agent-specs/notes.md` summarizing decisions
- [x] Run full test suite and fix regressions - All 50 tests pass
- [ ] Create PR(s) with descriptive changelog and link to this change
- [ ] Request reviews from `@dvazquezd` and `@maintainer` for each PR

## Status Update (2026-01-31)
Core refactorings COMPLETED:
- Config is now a proper dataclass with validation
- LLM provider uses factory pattern with DI support
- All critical tests pass (50/50)
- Fixed invoke() method issue for LangChain chat models

Remaining tasks are OPTIONAL improvements for future iterations.
