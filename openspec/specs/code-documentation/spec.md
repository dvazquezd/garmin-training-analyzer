# Feature: Documentación de Código (code-documentation)

## Context

El proyecto requiere documentación consistente en los métodos y clases públicas para mejorar la mantenibilidad, la experiencia de desarrolladores y la generación de documentación automática. Este spec recoge los requisitos mínimos para que los métodos públicos y las clases en `src/` tengan docstrings completas siguiendo el estilo Google.

**Valor que aporta**:
- Mejora la lectura y comprensión del código
- Facilita el onboarding de nuevos contribuidores
- Permite generar documentación automática y mejorar soporte de IDE

---

## Goal

Asegurar que los módulos prioritarios y, en general, todos los métodos públicos del código base tengan docstrings completas y consistentes en formato Google.

---

## Requirements

### Requirement: Public methods must have docstrings

All public methods (methods not starting with `_`) in modules under `src/` SHALL have comprehensive docstrings following the Google docstring format.

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

### Requirement: Class-level documentation

Public classes in `src/` SHALL have class-level docstrings explaining the class purpose and usage.

#### Scenario: Class has descriptive docstring

- **WHEN** a public class is defined
- **THEN** the class SHALL have a docstring immediately after the class declaration
- **AND** the docstring SHALL describe the class's purpose and responsibilities
- **AND** the docstring SHALL include usage examples if the class has a non-trivial interface

### Requirement: Priority files must be fully documented

The following high-priority modules SHALL have complete documentation for all public methods:
- `src/config.py` - Configuration management
- `src/visualizations.py` - Chart generation
- `src/garmin_client.py` - Garmin API client
- `src/prompt_manager.py` - Prompt management
- `src/cache_manager.py` - Caching functionality
- `src/html_reporter.py` - Report generation

#### Scenario: All public methods in priority files are documented

- **WHEN** reviewing priority files listed above
- **THEN** every public method (not starting with `_`) SHALL have a complete docstring
- **AND** no public method SHALL be missing documentation
- **AND** existing partial docstrings SHALL be completed with all required sections

---

## Technical Notes

- Use Google-style docstrings. Example:

```python
def method_name(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Optional longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
```

- Consider adding `pydocstyle` or CI checks to ensure coverage and consistency.

---

## Out of Scope

- Docstrings for private methods (beginning with `_`) unless exceptionally complex
- Automatic generation or publishing of documentation (Sphinx) in this change

---

## Verification

- Run `pydocstyle` / `pydocstyle src/` or a linter configured for docstrings
- Manually review the six priority modules to ensure no public methods are missing docstrings
