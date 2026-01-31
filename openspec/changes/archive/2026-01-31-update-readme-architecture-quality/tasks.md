## 1. Prepare and Update Project Structure Section

- [x] 1.1 Read current README.md to understand existing structure and content
- [x] 1.2 Create backup copy of current README.md for reference
- [x] 1.3 Update "Project Structure" section to include `src/templates/` directory
- [x] 1.4 Add `report_template.html` and `report_styles.css` to structure diagram with descriptions
- [x] 1.5 Add `openspec/` directory to structure diagram
- [x] 1.6 Add `openspec/specs/`, `openspec/changes/`, and `openspec/agents.md` with descriptions
- [x] 1.7 Verify all paths in structure diagram match actual filesystem

## 2. Add Architecture & Design Principles Section

- [x] 2.1 Create new "Architecture & Design Principles" section after Features section
- [x] 2.2 Add subsection explaining template separation architecture
- [x] 2.3 Document why HTML/CSS are in external files (SOLID compliance, Clean Code)
- [x] 2.4 Explain Jinja2 usage for template loading
- [x] 2.5 Add subsection on SOLID principles followed in the codebase
- [x] 2.6 Add subsection on Clean Code and DRY practices
- [x] 2.7 Document separation of concerns (logic, presentation, data)
- [x] 2.8 Reference `openspec/agents.md` for detailed engineering standards

## 3. Add Code Quality Standards Section

- [x] 3.1 Create new "Code Quality Standards" section before Development section
- [x] 3.2 Document pylint scores achieved (10/10 for refactored modules like html_reporter.py)
- [x] 3.3 Describe testing approach (pytest, fixtures, mocking)
- [x] 3.4 Document code style standards (Google docstrings, type hints)
- [x] 3.5 Reference engineering principles from `openspec/agents.md`
- [x] 3.6 Explain quality expectations for contributors
- [x] 3.7 Add example showing recent quality improvements (template refactoring)

## 4. Expand Development Section with OpenSpec Workflow

- [x] 4.1 Add new subsection "OpenSpec Workflow" within Development section
- [x] 4.2 Provide brief explanation of what OpenSpec is
- [x] 4.3 Document the workflow: proposal → design → specs → tasks → implementation
- [x] 4.4 Add example command for creating a new change
- [x] 4.5 Reference `openspec/agents.md` for complete workflow details
- [x] 4.6 Explain when to use full workflow vs. simple fixes
- [x] 4.7 Frame OpenSpec as helpful structure that improves quality

## 5. Update Table of Contents and Add Badges (Optional)

- [x] 5.1 Update Table of Contents to include new sections
- [x] 5.2 Verify all Table of Contents links work correctly
- [x] 5.3 Check if quality badges are available (CI/CD, coverage tools)
- [x] 5.4 If available, add quality badges near top of README
- [x] 5.5 Ensure badges link to actual metrics sources
- [x] 5.6 Skip badges if metrics systems not configured (no placeholders)

## 6. Validation and Review

- [x] 6.1 Verify all directory paths reference actual filesystem locations
- [x] 6.2 Validate all internal links and anchors work
- [x] 6.3 Check all external links are functional
- [x] 6.4 Verify code examples match current codebase
- [x] 6.5 Preview README rendering (GitHub/GitLab) to ensure proper formatting
- [x] 6.6 Verify new sections are scannable and not overwhelming
- [x] 6.7 Check that language is accessible (not too technical for general users)
- [x] 6.8 Ensure consistency between README and actual code/architecture
- [x] 6.9 Run markdown linter if available to check formatting
- [x] 6.10 Review against spec requirements to ensure all are met
