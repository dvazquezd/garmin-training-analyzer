## Context

The `HTMLReporter` class in `src/html_reporter.py` currently embeds CSS (400+ lines) and HTML (150+ lines) as string literals within the `_render_template()` method, resulting in a 590+ line function that violates Single Responsibility Principle and Clean Code guidelines. The module already uses Jinja2 for templating but uses `Template()` constructor with string literals instead of file-based loading.

**Current Architecture:**
- Python code contains CSS and HTML as multi-line strings
- `_render_template()` constructs template from string literal
- Changes to presentation require modifying Python code
- Version control diffs mix code and styling changes

**Constraints:**
- Must maintain 100% backward compatibility with existing API
- No new dependencies (already has Jinja2)
- Must support embedded base64 charts (current behavior)
- Report generation must remain self-contained (no external CDN dependencies)

## Goals / Non-Goals

**Goals:**
- Separate CSS into `src/templates/report_styles.css` for independent styling
- Separate HTML structure into `src/templates/report_template.html` using Jinja2 file loader
- Reduce `_render_template()` method from 590+ to ~50 lines
- Enable designers to modify styles without touching Python code
- Maintain exact same output format and functionality
- Comply with SOLID principles and Clean Code guidelines from `openspec/agents.md`

**Non-Goals:**
- Changing report layout or visual design
- Adding new features to reports
- Modifying the public API of `HTMLReporter`
- Supporting multiple themes or customizable templates (future enhancement)
- Externalizing JavaScript (none currently exists)

## Decisions

### Decision 1: Use Jinja2 FileSystemLoader instead of Template constructor

**Chosen Approach:** Use `jinja2.FileSystemLoader` with `Environment` to load templates from `src/templates/` directory.

**Rationale:**
- Jinja2 already in use, no new dependency
- FileSystemLoader is the standard approach for file-based templates
- Enables template caching and better error messages
- Separates concerns: Python handles logic, templates handle presentation

**Alternatives Considered:**
- Keep string templates with external CSS only: Still violates SRP, HTML remains in Python
- Use PackageLoader: Unnecessary complexity for simple file structure
- Use external templating engine (Mako, Django): Adds dependency, overkill for single template

### Decision 2: Inline CSS in HTML template using `<style>` tag

**Chosen Approach:** Place CSS in separate file, but include it in HTML template via `{% include 'report_styles.css' %}` within a `<style>` tag.

**Rationale:**
- Keeps reports self-contained (single HTML file output)
- No external CSS file dependencies for end users
- Maintains current behavior where reports work offline
- Separates CSS for development while preserving single-file distribution
- Designers can edit CSS independently during development

**Alternatives Considered:**
- Link external CSS file: Breaks self-contained report requirement
- Keep CSS inline but load from file in Python: Still couples loading logic
- Use CSS modules: Adds build complexity, unnecessary for static reports

### Decision 3: Template directory location at `src/templates/`

**Chosen Approach:** Create `src/templates/` directory adjacent to `html_reporter.py`.

**Rationale:**
- Standard Python practice: templates near the code that uses them
- Easy relative path resolution from module location
- Consistent with project structure (code in `src/`)
- Simplifies packaging and distribution

**Alternatives Considered:**
- Root-level `templates/`: Mixes source and config concerns
- Inside `html_reporter/` package: Would require creating package, overkill
- User-configurable path: Unnecessary complexity, no use case

### Decision 4: Preserve exact template variable names and structure

**Chosen Approach:** Keep all template variables identical to current implementation (`athlete_name`, `report_date`, `total_distance`, etc.).

**Rationale:**
- Zero-risk refactoring: only internal structure changes
- Easier to verify correctness (diff the outputs)
- No need to update calling code
- Can improve variable names in future refactor if needed

### Decision 5: Update `__init__` to initialize Jinja2 Environment

**Chosen Approach:** Add template directory detection and Jinja2 Environment initialization in `HTMLReporter.__init__()`.

**Rationale:**
- One-time setup cost, reused across reports
- Fails fast if template directory missing
- Enables template caching (Jinja2 default behavior)
- Follows dependency injection pattern (Environment as instance attribute)

**Implementation:**
```python
from jinja2 import Environment, FileSystemLoader

def __init__(self, output_dir: str = "analysis_reports"):
    self.output_dir = Path(output_dir)
    self.output_dir.mkdir(exist_ok=True)
    self.logger = logging.getLogger(self.__class__.__name__)

    # Initialize Jinja2 template environment
    template_dir = Path(__file__).parent / "templates"
    self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
```

## Risks / Trade-offs

**Risk:** Template files not found at runtime (missing deployment, incorrect paths)
→ **Mitigation:** Add explicit validation in `__init__` with clear error message. Include templates in package manifest. Add integration test that validates template loading.

**Risk:** Markdown rendering differences after refactor
→ **Mitigation:** Markdown processing logic remains identical, only template loading changes. Add test comparing output before/after refactor.

**Trade-off:** Template files must be distributed with package
→ **Acceptable:** Templates are part of the module, standard Python practice. Simpler than embedding as package data.

**Trade-off:** Two-file development (HTML + CSS) vs single-file output
→ **Benefit:** Development ergonomics improved, output format preserved. Best of both worlds.

**Risk:** Breaking changes to template syntax if Jinja2 version changes
→ **Mitigation:** Jinja2 has stable syntax. Pin version in requirements if needed. Templates use basic features only (variables, loops, conditionals).

## Migration Plan

**Phase 1: Extract and verify (no behavior change)**
1. Create `src/templates/` directory
2. Extract CSS to `report_styles.css` (exact copy from string)
3. Extract HTML to `report_template.html` with `{% include 'report_styles.css' %}`
4. Update `__init__` to create Jinja2 Environment
5. Update `_render_template()` to use file-based template
6. Run existing tests to verify no output changes

**Phase 2: Cleanup**
1. Remove pylint disable comments that are now unnecessary
2. Update module docstrings to reflect new structure
3. Remove old string template code

**Rollback Strategy:**
Git revert is sufficient - no database migrations, no external dependencies, no configuration changes. If issues found post-merge, revert commit and investigate.

**Validation:**
- Existing tests must pass without modification
- Manual comparison of HTML output before/after (should be identical)
- Verify report generation works with missing/invalid template directory (should raise clear error)

## Open Questions

None - design is straightforward refactoring with clear path.
