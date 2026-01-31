## 1. Prepare Template Files

- [x] 1.1 Create `src/templates/` directory
- [x] 1.2 Extract CSS from `html_reporter.py` lines 188-595 to `src/templates/report_styles.css` (exact copy)
- [x] 1.3 Extract HTML from `html_reporter.py` lines 182-743 to `src/templates/report_template.html`
- [x] 1.4 Add `<style>{% include 'report_styles.css' %}</style>` in HTML template head section
- [x] 1.5 Verify template files are valid (no syntax errors in HTML/CSS)

## 2. Update HTMLReporter Class Initialization

- [x] 2.1 Import `Environment` and `FileSystemLoader` from `jinja2` in `html_reporter.py`
- [x] 2.2 Add template directory path resolution in `__init__`: `template_dir = Path(__file__).parent / "templates"`
- [x] 2.3 Initialize Jinja2 Environment with FileSystemLoader in `__init__`: `self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))`
- [x] 2.4 Add validation to raise clear error if templates directory doesn't exist
- [x] 2.5 Update `__init__` docstring to mention template directory initialization

## 3. Refactor _render_template Method

- [x] 3.1 Remove embedded `template_str` variable (lines 182-743)
- [x] 3.2 Load template from file: `template = self.jinja_env.get_template('report_template.html')`
- [x] 3.3 Keep markdown conversion logic identical (lines 747-751)
- [x] 3.4 Keep all template variable names unchanged in `template.render()` call
- [x] 3.5 Verify method is now ~50 lines instead of 590+
- [x] 3.6 Remove or update pylint disable comments that are no longer needed

## 4. Update Documentation

- [x] 4.1 Update module docstring in `html_reporter.py` to mention file-based templates
- [x] 4.2 Update class docstring to reflect template loading from `src/templates/`
- [x] 4.3 Update `_render_template()` docstring to reference external template files
- [x] 4.4 Remove references to "embedded" or "string literal" templates in docstrings
- [x] 4.5 Add docstring notes about `report_template.html` and `report_styles.css` location

## 5. Testing and Validation

- [x] 5.1 Run existing tests to verify they pass without modification
- [x] 5.2 Generate a test report and compare HTML output before/after refactoring (visual inspection)
- [x] 5.3 Test error handling: verify clear error when templates directory is missing
- [x] 5.4 Verify all report sections render correctly (header, stats, charts, table, analysis, footer)
- [x] 5.5 Verify embedded base64 charts still work correctly
- [x] 5.6 Verify markdown rendering in analysis section is identical
- [x] 5.7 Test responsive design on different screen sizes (if applicable)

## 6. Code Quality Checks

- [x] 6.1 Run linter (pylint) and verify no new violations introduced
- [x] 6.2 Verify code complies with SOLID principles (SRP satisfied, method <50 lines)
- [x] 6.3 Verify Clean Code guidelines (descriptive names, no magic strings, cohesive modules)
- [x] 6.4 Check that template files will be included in package distribution
- [x] 6.5 Review git diff to ensure only expected files changed
