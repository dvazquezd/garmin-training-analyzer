# Feature: HTML Template Management (html-template-management)

## Purpose

System for managing HTML templates and CSS assets separately from Python code, enabling file-based template loading with Jinja2, proper separation of concerns, and independent versioning of presentation assets.

This capability ensures that HTML report generation uses external template files instead of embedded string literals, following SOLID principles and Clean Code guidelines.

---

## Requirements

### Requirement: HTMLReporter SHALL use file-based Jinja2 templates

The `HTMLReporter` class SHALL load HTML templates from external files using Jinja2's `FileSystemLoader` instead of embedding templates as string literals in Python code.

#### Scenario: Template loaded from file system

- **WHEN** `HTMLReporter` is initialized
- **THEN** the system SHALL create a Jinja2 `Environment` with `FileSystemLoader` pointing to the templates directory
- **AND** the templates directory path SHALL be resolved relative to the module location (`Path(__file__).parent / "templates"`)
- **AND** the system SHALL raise a clear error if the templates directory does not exist

#### Scenario: Report generation uses external template

- **WHEN** `generate_report()` is called
- **THEN** the system SHALL load the template from `report_template.html` using the Jinja2 environment
- **AND** the template SHALL be rendered with the same variables as the current implementation
- **AND** the output SHALL be functionally identical to the current string-based approach

### Requirement: CSS SHALL be separated into external file

The CSS styles for HTML reports SHALL be maintained in a separate `.css` file that is included during template rendering.

#### Scenario: CSS file exists in templates directory

- **WHEN** the templates directory is created
- **THEN** a `report_styles.css` file SHALL exist containing all report styling
- **AND** the CSS file SHALL contain the exact same styles as currently embedded in the Python code
- **AND** the CSS file SHALL be maintainable by designers without Python knowledge

#### Scenario: CSS included in rendered HTML

- **WHEN** the HTML template is rendered
- **THEN** the CSS SHALL be included in the output HTML using Jinja2's `{% include 'report_styles.css' %}` directive within a `<style>` tag
- **AND** the final HTML output SHALL remain self-contained (single file with embedded styles)
- **AND** the report SHALL work offline without external CSS dependencies

### Requirement: Template directory SHALL be organized and discoverable

The templates directory SHALL be located at `src/templates/` adjacent to `html_reporter.py` for easy discovery and maintenance.

#### Scenario: Templates directory structure

- **WHEN** examining the project structure
- **THEN** a `src/templates/` directory SHALL exist
- **AND** the directory SHALL contain `report_template.html`
- **AND** the directory SHALL contain `report_styles.css`
- **AND** template files SHALL be included in package distribution

#### Scenario: Clear error when templates missing

- **WHEN** `HTMLReporter` is initialized and the templates directory does not exist
- **THEN** the system SHALL raise a `FileNotFoundError` or similar exception
- **AND** the error message SHALL clearly indicate the expected templates directory path
- **AND** the error SHALL occur at initialization time (fail fast), not at report generation time

### Requirement: Template variable contract SHALL remain unchanged

The Jinja2 template variables SHALL maintain the exact same names and structure as the current implementation to ensure backward compatibility.

#### Scenario: Template variables unchanged

- **WHEN** the template is rendered
- **THEN** all existing variable names SHALL be preserved (e.g., `athlete_name`, `report_date`, `total_distance`, `activities`, `charts`)
- **AND** variable types and formats SHALL remain identical
- **AND** no changes to calling code SHALL be required

#### Scenario: Markdown rendering preserved

- **WHEN** the analysis text is rendered
- **THEN** markdown-to-HTML conversion SHALL function identically to the current implementation
- **AND** the `analysis_html` variable SHALL be marked as safe using Jinja2's `|safe` filter
- **AND** markdown extensions used SHALL remain the same (`extra`, `nl2br`, `sane_lists`)

### Requirement: Report output SHALL be functionally identical

The refactored implementation SHALL produce HTML reports that are functionally identical to the current implementation.

#### Scenario: Output comparison validates refactor

- **WHEN** comparing reports generated before and after refactoring
- **THEN** the HTML structure SHALL be identical
- **AND** the visual rendering SHALL be identical
- **AND** all embedded charts (base64) SHALL work the same way
- **AND** responsive design SHALL function identically
- **AND** all sections (header, stats, charts, table, analysis, footer) SHALL render correctly

#### Scenario: Public API remains unchanged

- **WHEN** external code calls `HTMLReporter` methods
- **THEN** the `generate_report()` method signature SHALL remain unchanged
- **AND** the constructor parameters SHALL remain unchanged
- **AND** the return type SHALL remain unchanged (`Path` to generated HTML file)
- **AND** all existing tests SHALL pass without modification
