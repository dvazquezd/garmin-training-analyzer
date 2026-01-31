## Why

The current `html_reporter.py` module violates multiple software engineering principles defined in `openspec/agents.md`. The CSS (400+ lines) and HTML (150+ lines) are embedded as string literals within the Python code, resulting in a 590+ line method that violates Single Responsibility Principle and Clean Code guidelines. This coupling makes the code difficult to maintain, test, and extend. Designers cannot modify styles without touching Python code, and version control diffs are polluted with CSS changes appearing as code changes.

## What Changes

- Extract embedded CSS into a separate `report_styles.css` file in a new `src/templates/` directory
- Extract embedded HTML into a Jinja2 template file `report_template.html` in `src/templates/`
- Refactor `HTMLReporter._render_template()` to load external template and CSS files
- Update `HTMLReporter` to use Jinja2's file-based template loading instead of string templates
- Add proper resource management for template and CSS file paths
- Maintain 100% backward compatibility with existing report generation API

## Capabilities

### New Capabilities
- `html-template-management`: System for managing HTML templates and CSS assets separately from Python code, enabling file-based template loading, proper separation of concerns, and independent versioning of presentation assets.

### Modified Capabilities
- `code-documentation`: The refactored module will require updated docstrings to reflect the new template loading mechanism and file structure.

## Impact

**Affected Code:**
- `src/html_reporter.py`: Major refactoring of `_render_template()` method from 590+ lines to ~50 lines
- `src/html_reporter.py`: Constructor will need to initialize Jinja2 file loader
- `src/html_reporter.py`: Method signatures remain unchanged (backward compatible)

**New Files:**
- `src/templates/report_template.html`: HTML structure for reports
- `src/templates/report_styles.css`: Stylesheet for reports

**Dependencies:**
- Already uses `jinja2` library (no new dependencies)

**Benefits:**
- ✅ Complies with Single Responsibility Principle
- ✅ Reduces method size from 590+ to ~50 lines (meets <50 line guideline)
- ✅ Enables designers to modify styles independently
- ✅ Improves testability (templates can be validated separately)
- ✅ Better version control (CSS changes don't pollute Python diffs)
- ✅ Reusable assets across multiple report types
