## Purpose

This capability defines standards for project-level documentation, including README structure, architecture explanations, quality metrics, development workflows, and contributor guidelines.

Proper project documentation ensures that:
- New contributors can quickly understand the project architecture and standards
- Design decisions are visible and traceable
- Quality standards are clearly communicated
- The development workflow is documented and accessible

---

## Requirements

### Requirement: README SHALL document project architecture and design principles

The project README SHALL include a dedicated section explaining the architectural patterns, design decisions, and engineering principles followed in the codebase.

#### Scenario: Architecture section explains template separation

- **WHEN** reviewing the README architecture section
- **THEN** it SHALL explain why HTML templates are separated into external files
- **AND** it SHALL mention the use of Jinja2 for template loading
- **AND** it SHALL reference the `src/templates/` directory structure
- **AND** it SHALL explain the benefits of separating presentation from logic

#### Scenario: Engineering principles are documented

- **WHEN** reviewing the README architecture section
- **THEN** it SHALL list the SOLID principles followed in the codebase
- **AND** it SHALL mention Clean Code practices and DRY principles
- **AND** it SHALL reference `openspec/agents.md` for detailed standards
- **AND** it SHALL explain separation of concerns (logic, presentation, data)

### Requirement: README SHALL accurately reflect current project structure

The project structure section in README SHALL show all significant directories and files with accurate paths and descriptions matching the actual codebase.

#### Scenario: Template directory is documented

- **WHEN** reviewing the project structure diagram in README
- **THEN** it SHALL include `src/templates/` directory
- **AND** it SHALL list `report_template.html` file
- **AND** it SHALL list `report_styles.css` file
- **AND** it SHALL include descriptions explaining their purpose

#### Scenario: OpenSpec directory is documented

- **WHEN** reviewing the project structure diagram in README
- **THEN** it SHALL include `openspec/` directory
- **AND** it SHALL list `openspec/specs/` subdirectory for main specifications
- **AND** it SHALL list `openspec/changes/` subdirectory for active changes
- **AND** it SHALL mention `openspec/agents.md` for engineering standards

### Requirement: README SHALL document code quality standards and metrics

The README SHALL include a section communicating quality standards, metrics achieved, and expectations for contributors.

#### Scenario: Quality metrics are visible

- **WHEN** reviewing the code quality section
- **THEN** it SHALL mention pylint scores for refactored modules (e.g., 10/10)
- **AND** it SHALL describe testing approach (pytest, fixtures, mocking)
- **AND** it SHALL reference code style standards (Google docstrings, type hints)
- **AND** it SHALL link to engineering principles in `openspec/agents.md`

#### Scenario: Standards are clear for contributors

- **WHEN** a new contributor reads the code quality section
- **THEN** they SHALL understand expected quality levels
- **AND** they SHALL know which linting tools are used
- **AND** they SHALL understand testing requirements
- **AND** they SHALL see examples of quality standards achieved

### Requirement: README SHALL explain OpenSpec workflow for contributors

The README SHALL document the spec-driven development workflow used in the project, enabling contributors to understand the change process.

#### Scenario: OpenSpec workflow is explained

- **WHEN** reviewing the Development section
- **THEN** it SHALL explain what OpenSpec is briefly
- **AND** it SHALL outline the workflow: proposal → design → specs → tasks → implementation
- **AND** it SHALL reference `openspec/agents.md` for detailed standards
- **AND** it SHALL provide an example of creating a change

#### Scenario: Workflow integration is clear

- **WHEN** a contributor wants to make a change
- **THEN** the README SHALL guide them to the OpenSpec process
- **AND** it SHALL explain when to use full workflow vs. simple fixes
- **AND** it SHALL show how specs improve code quality
- **AND** it SHALL indicate this is a structured but helpful approach

### Requirement: README SHALL include visual quality indicators where applicable

The README MAY include badges or indicators of code quality, test coverage, and other relevant metrics when such systems are configured.

#### Scenario: Quality badges are present

- **WHEN** quality metrics systems are available (CI/CD, coverage tools)
- **THEN** the README SHALL include relevant badges near the top
- **AND** badges SHALL be accurate and link to actual metric sources
- **AND** badges SHALL not be placeholders or misleading

#### Scenario: Badges are omitted when not available

- **WHEN** quality metrics systems are not yet configured
- **THEN** the README SHALL NOT include placeholder or fake badges
- **AND** it MAY mention quality standards in text form instead
- **AND** badges SHALL only be added when actual metrics exist

### Requirement: README content SHALL remain accurate and synchronized with codebase

The README documentation SHALL accurately reflect the current state of the codebase, including recent refactorings and architectural changes.

#### Scenario: Architecture documentation matches implementation

- **WHEN** reviewing README architecture section
- **THEN** all architectural descriptions SHALL match actual code structure
- **AND** all file paths SHALL be valid and current
- **AND** all code examples SHALL work with current codebase
- **AND** all external links SHALL be functional

#### Scenario: Updates accompany significant changes

- **WHEN** significant architectural changes are made to the codebase
- **THEN** corresponding README updates SHALL be included in the same PR
- **AND** OpenSpec changes SHALL consider README impact
- **AND** PR review checklist SHALL verify README accuracy
