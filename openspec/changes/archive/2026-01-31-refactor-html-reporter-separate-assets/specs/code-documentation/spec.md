## MODIFIED Requirements

### Requirement: Public methods must have docstrings

All public methods (methods not starting with `_`) in modules under `src/` SHALL have comprehensive docstrings following the Google docstring format.

**Updated for template-based architecture**: Docstrings in `html_reporter.py` SHALL reflect the new file-based template loading mechanism, including references to template files and the Jinja2 environment.

#### Scenario: Method has complete docstring with all sections

- **WHEN** a public method is defined in any module under `src/`
- **THEN** the method SHALL have a docstring that includes:
  - A one-line summary describing what the method does
  - An `Args:` section listing all parameters with types and descriptions (if method has parameters)
  - A `Returns:` section describing the return value and type (if method returns a value)
  - A `Raises:` section documenting exceptions that may be raised (if applicable)

#### Scenario: Method docstring uses consistent format

- **WHEN** examining docstrings across the codebase
- **THEN** all docstrings SHALL follow the same format (Google style)
- **AND** parameter types SHALL be documented using type hints or in the docstring
- **AND** return types SHALL be clearly specified

#### Scenario: HTMLReporter docstrings reflect template-based architecture

- **WHEN** reviewing `html_reporter.py` documentation
- **THEN** the class docstring SHALL mention that templates are loaded from external files
- **AND** the `__init__` docstring SHALL document the template directory initialization
- **AND** the `_render_template()` docstring SHALL reference template files instead of embedded strings
- **AND** docstrings SHALL indicate that templates are located in `src/templates/`

### Requirement: Priority files must be fully documented

The following high-priority modules SHALL have complete documentation for all public methods:
- `src/config.py` - Configuration management
- `src/visualizations.py` - Chart generation
- `src/garmin_client.py` - Garmin API client
- `src/prompt_manager.py` - Prompt management
- `src/cache_manager.py` - Caching functionality
- `src/html_reporter.py` - Report generation

**Updated**: `html_reporter.py` documentation SHALL be updated to reflect the refactored template management system.

#### Scenario: All public methods in priority files are documented

- **WHEN** reviewing priority files listed above
- **THEN** every public method (not starting with `_`) SHALL have a complete docstring
- **AND** no public method SHALL be missing documentation
- **AND** existing partial docstrings SHALL be completed with all required sections

#### Scenario: html_reporter.py reflects new architecture

- **WHEN** reviewing `html_reporter.py` after refactoring
- **THEN** docstrings SHALL accurately describe the file-based template system
- **AND** references to "string templates" or "embedded HTML/CSS" SHALL be removed or updated
- **AND** docstrings SHALL mention template file names where relevant (`report_template.html`, `report_styles.css`)
- **AND** the module docstring SHALL be updated to reflect separation of templates and code
