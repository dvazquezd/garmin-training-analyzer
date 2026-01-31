# Agents

This project uses AI-assisted, spec-driven development with OpenSpec.  
All agents must follow the standards and workflows defined in `openspec/specs/project.md`.

---

## Global Rules for All Agents

- Always respect the OpenSpec workflow: **proposal → review → apply → tests → archive**.
- Never modify code outside the scope of the current approved change.
- Always preserve existing behavior unless the spec explicitly approves a change.
- Prefer **small, incremental changes** over large refactors.
- Before writing code, restate the spec in your own words and identify:
  - main responsibilities
  - constraints
  - edge cases
  - non-functional requirements (performance, security, UX, etc.)

---

## Software Engineering Principles (Mandatory)

All generated code must comply with:

- **SOLID**
  - Single Responsibility: each class/function has one clear reason to change.
  - Open/Closed: prefer extension over modification; use composition over inheritance.
  - Liskov Substitution: subclasses/interfaces must be safely interchangeable.
  - Interface Segregation: small, focused interfaces; avoid “fat” interfaces.
  - Dependency Inversion: depend on abstractions, not concrete implementations.

- **DRY (Don’t Repeat Yourself)**
  - Extract shared logic into reusable functions, helpers, or modules.
  - Avoid copy‑pasting; if you duplicate code, refactor it.

- **Clean Code**
  - Descriptive, intention‑revealing names for variables, functions, classes, and modules.
  - Small functions (ideally under 40–50 lines) with a single responsibility.
  - Minimize comments by making the code self‑explanatory.
  - Comments should explain **why**, not **what**.
  - Avoid magic numbers and strings; use named constants.
  - Keep modules cohesive and loosely coupled.

- **KISS & YAGNI**
  - Keep solutions as simple as possible.
  - Do not add features or abstractions that are not required by the current spec.

- **Error Handling & Robustness**
  - Validate inputs and handle predictable failure modes.
  - Fail fast with clear, actionable error messages.
  - Avoid swallowing exceptions silently.

---

## Architecture & Project Structure

When applicable, follow a layered / hexagonal / clean architecture style:

- `domain/`
  - Business entities, value objects, domain services, use cases.
  - Pure logic, no external framework or I/O dependencies.

- `application/`
  - Application services, use case orchestration, ports/interfaces.
  - Coordinates domain logic and infrastructure.

- `infrastructure/`
  - Implementations of interfaces (database, HTTP clients, external APIs, filesystem, etc.).
  - Framework- and technology-specific code.

- `interface/` or `presentation/` (if relevant)
  - Controllers, handlers, CLI/HTTP/UI adapters.

- `tests/`
  - Unit, integration, and end‑to‑end tests.
  - Mirror the structure of `src/` as much as possible.

Agents must:
- Respect existing architecture and naming conventions.
- Place new code in the appropriate layer and module.
- Propose refactors when architecture violations are detected.

---

## Testing Requirements

- Prefer **test‑driven** or **spec‑driven** approach: write or update tests with every change.
- For each new feature or bug fix:
  - Add or update unit tests covering success and failure paths.
  - Include edge cases derived from the spec.
- Tests must be:
  - Deterministic (no random or time‑sensitive flakiness without control).
  - Isolated (use mocks/stubs for external services).
  - Readable and maintainable (arrange–act–assert pattern is recommended).

If the spec does not define tests, propose a minimal but meaningful test suite before implementing the feature.

---

## Interaction with OpenSpec

When working with OpenSpec changes:

1. **Read & Clarify**
   - Read the relevant spec and change files thoroughly.
   - Restate goals, constraints, and acceptance criteria in your own words.
   - If information is missing or ambiguous, propose clarifications in the spec before coding.

2. **Plan**
   - Identify impacted modules, layers, and contracts.
   - Outline a small, ordered list of implementation steps.
   - Plan necessary refactors if existing code violates the standards above.

3. **Implement**
   - Make the smallest change that fully satisfies the spec.
   - Keep functions, classes, and modules focused and cohesive.
   - Avoid introducing new dependencies or technologies unless justified by the spec.

4. **Validate**
   - Run and, if necessary, extend automated tests.
   - Verify that the solution matches the spec and does not break existing behavior.
   - Check for violations of SOLID, DRY, and Clean Code principles.

5. **Document**
   - Update relevant documentation, specs, or comments when behavior or contracts change.
   - Summarize the change in a concise, technical note (what changed, why, and impact).

---

## Style, Tooling, and Quality Gates

- Follow existing language- and framework-specific style guides in this repository.
- Use configured linters, formatters, and static analysis tools (e.g. ESLint, Prettier, Black, Flake8, etc.).
- Code that does not pass:
  - linter
  - formatter
  - unit test suite  
  must be considered **incomplete**.

If the repository does not yet define tooling, propose a minimal, standard setup for the tech stack in use.

---

## Agent Behavior Guidelines

- Think step by step; explain design decisions when they are non-trivial.
- Prefer refactoring and incremental improvement over rewriting large areas of code.
- Maintain backward compatibility unless the spec explicitly allows breaking changes.
- When forced to choose between:
  - quick hacks vs. maintainable design  
  always choose **maintainable design** aligned with the principles above.
