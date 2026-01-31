## Context

The README.md is the primary documentation entry point for the project. It was created early in development and hasn't been updated to reflect significant architectural improvements made in recent refactorings, particularly:

- HTML report generation was refactored from embedded string literals (590+ lines) to external Jinja2 templates
- Project follows SOLID principles and Clean Code guidelines as defined in `openspec/agents.md`
- Code quality standards achieved (pylint 10/10 on refactored modules)
- Development uses OpenSpec workflow for spec-driven changes

**Current State:**
- README shows outdated project structure (missing `src/templates/`, `openspec/`)
- No mention of engineering principles or quality standards
- No documentation of architectural decisions
- Development section doesn't explain OpenSpec workflow
- Missing quality/standards badges

**Stakeholders:**
- New contributors who need to understand project architecture and standards
- Maintainers who need accurate documentation
- Users evaluating code quality and maintenance practices

## Goals / Non-Goals

**Goals:**
- Document current architecture accurately (template separation, Jinja2 usage)
- Communicate engineering principles followed (SOLID, Clean Code, DRY)
- Show quality standards achieved (linting scores, test coverage)
- Explain OpenSpec workflow for contributors
- Improve project structure documentation
- Add relevant quality badges
- Maintain consistency with actual codebase

**Non-Goals:**
- Changing any code or functionality
- Adding new features or capabilities
- Modifying configuration or dependencies
- Creating comprehensive API documentation (that's for code docstrings)
- Writing detailed tutorials (keep README at overview level)

## Decisions

### Decision 1: Add "Architecture & Design Principles" section

**Chosen Approach:** Create dedicated section after Features explaining key architectural patterns and engineering principles.

**Rationale:**
- Makes architectural decisions visible and intentional
- Helps contributors understand "why" behind code structure
- Demonstrates professional engineering practices
- Explains template separation rationale (SOLID compliance)

**Content:**
- Template-based architecture (HTML/CSS separation)
- SOLID principles adherence
- Clean Code practices
- Separation of concerns (logic, presentation, data)

### Decision 2: Update "Project Structure" with accurate directory tree

**Chosen Approach:** Expand structure diagram to include `src/templates/` and `openspec/` with explanations.

**Rationale:**
- Current structure is outdated (missing key directories)
- Developers need accurate map of codebase
- Shows template files explicitly
- Documents OpenSpec artifacts location

**New directories to document:**
```
src/templates/           # Jinja2 templates and CSS
│   ├── report_template.html
│   └── report_styles.css
openspec/                # Spec-driven development
│   ├── specs/           # Main specifications
│   ├── changes/         # Active changes
│   └── agents.md        # Engineering standards
```

### Decision 3: Add "Code Quality Standards" section

**Chosen Approach:** New section before "Development" documenting standards and metrics.

**Rationale:**
- Communicates quality expectations to contributors
- Shows professionalism and maintainability focus
- Provides context for PR review standards
- Highlights recent quality improvements

**Content:**
- Pylint scores (10/10 for refactored modules)
- Testing approach (pytest, fixtures, mocking)
- Code style (Google docstrings, type hints)
- Engineering principles from `openspec/agents.md`

### Decision 4: Expand "Development" section with OpenSpec workflow

**Chosen Approach:** Add subsection explaining spec-driven development process.

**Rationale:**
- Contributors need to understand workflow before contributing
- OpenSpec is core to development process
- Shows structured approach to changes
- Links to existing agent standards

**Content:**
- Brief explanation of OpenSpec
- Workflow: proposal → design → specs → tasks → implementation
- Reference to `openspec/agents.md` for details
- Example of creating a change

### Decision 5: Add quality badges (optional, if available)

**Chosen Approach:** Add badges for code quality, test coverage if metrics exist.

**Rationale:**
- Visual indicators of quality standards
- Industry standard practice
- Quick credibility signal

**Alternatives Considered:**
- Skip badges if metrics not available: Acceptable
- Use placeholder badges: No, misleading
- Only add when CI/CD configured: Yes, preferred

### Decision 6: Keep existing structure, add new sections

**Chosen Approach:** Insert new sections without removing existing content, only updating outdated parts.

**Rationale:**
- Preserve what works (installation, usage already good)
- Minimize disruption
- Additive changes are safer
- Existing examples and explanations remain valuable

**Placement:**
- Architecture section: After Features, before Table of Contents
- Code Quality: Before Development
- Updated structure: Replace existing Project Structure section
- OpenSpec workflow: Subsection within Development

## Risks / Trade-offs

**Risk:** README becomes too long and overwhelming
→ **Mitigation:** Keep new sections concise, use collapsible sections or links to external docs for details. Maintain scannable structure with clear headings.

**Risk:** Information becomes outdated again over time
→ **Mitigation:** Add to PR review checklist: "Update README if architectural changes made". Include README updates in OpenSpec changes when relevant.

**Risk:** Too technical for general users
→ **Mitigation:** Balance depth - keep architecture section accessible, put deep technical details in code comments and specs. Use clear language and examples.

**Trade-off:** More content vs. discoverability
→ **Acceptable:** Table of contents helps navigation. Quality of information justifies length increase.

**Trade-off:** Documenting OpenSpec workflow may create barrier to entry
→ **Mitigation:** Frame as helpful structure, not strict requirement. Show it improves quality. Simple fixes can skip full workflow.

## Migration Plan

**Implementation Steps:**

1. **Preserve existing content**: Copy current README as backup for reference
2. **Update Project Structure section**: Add missing directories with descriptions
3. **Add Architecture section**: Insert after Features section
4. **Add Code Quality section**: Insert before Development
5. **Expand Development section**: Add OpenSpec workflow subsection
6. **Add badges** (if available): Insert at top near existing badges
7. **Review for accuracy**: Verify all code references, directory paths, and examples are current
8. **Validate links**: Ensure all internal and external links work
9. **Test rendering**: Preview README on GitHub/GitLab to ensure proper formatting

**Validation:**
- All directory paths match actual structure
- Code examples match current codebase
- Links to files and sections work
- Markdown renders correctly
- Table of contents includes new sections

**Rollback Strategy:**
Simple git revert if needed - documentation only, no code changes.

## Open Questions

None - this is straightforward documentation update with clear scope.
