# Tasks: implement-agent-specs

- [x] Audit repository files and produce `audit_report.md` mapping agents.md rules → code locations
- [ ] Create per-module minimal refactor tasks (one commit / PR per module)
  - [ ] `refactor/config-dataclass` → implement dataclass config + tests
  - [ ] `refactor/llm-provider-abstraction` → factory + DI + tests
  - [ ] `refactor/prompt-manager-improvements` → jinja2, frontmatter, snippets, sanitization tests
  - [ ] `refactor/garmin-adapter` → GarminAdapter + 2FA/rate-limit handling tests
  - [ ] `refactor/cache-hardening` → WAL, busy_timeout, corruption recovery tests
  - [ ] `refactor/html-reporter-contracts` → input contracts & rendering tests
- [ ] Add/extend tests for each scenario found in audit (pytest, mocks, freezegun where needed)
- [ ] Add linter/formatter configuration and CI checks (Black, Flake8, isort) and enable as required status checks
- [ ] Add documentation updates and `changes/implement-agent-specs/notes.md` summarizing decisions
- [ ] Run full test suite and fix regressions
- [ ] Create PR(s) with descriptive changelog and link to this change
- [ ] Request reviews from `@dvazquezd` and `@maintainer` for each PR
