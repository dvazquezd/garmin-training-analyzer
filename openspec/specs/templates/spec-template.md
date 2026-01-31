# Feature: [Nombre Descriptivo de la Feature]

## Context
**Por qué existe**: [Describe el problema del negocio o del usuario que esta feature resuelve]

**Valor que aporta**: 
- [Beneficio 1]
- [Beneficio 2]
- [Beneficio 3]

---

## User Story
**Como** [tipo de usuario/rol]  
**Quiero** [acción o capacidad]  
**Para** [beneficio o resultado deseado]

---

## Acceptance Criteria

### Scenario 1: [Título del caso feliz - happy path]
**Given** [contexto inicial, precondiciones]  
**And** [precondición adicional si es necesaria]  
**When** [acción del usuario o del sistema]  
**Then** [resultado esperado observable]  
**And** [consecuencia o verificación adicional]  
**And** [otra consecuencia si aplica]

---

### Scenario 2: [Título del caso de error principal]
**Given** [contexto inicial diferente]  
**When** [acción que provoca el error]  
**Then** [comportamiento de manejo del error]  
**And** [mensaje o estado del sistema después]

---

### Scenario 3: [Otro caso edge importante]
**Given** [contexto]  
**When** [acción]  
**Then** [resultado]

---

### Scenario 4: [Caso con datos faltantes/incompletos]
**Given** [contexto con datos ausentes]  
**When** [acción]  
**Then** [manejo graceful del caso]

---

### Scenario 5: [Caso de integración o dependencia externa]
**Given** [dependencia externa en estado X]  
**When** [acción que interactúa con dependencia]  
**Then** [resultado esperado]  
**And** [verificación de side effects]

---

## Technical Notes
- **Dependencias**: [Librerías, APIs, servicios externos]
- **Consideraciones de rendimiento**: [Si aplica]
- **Seguridad**: [Si maneja datos sensibles]
- **Compatibilidad**: [Versiones, plataformas]
- **Límites conocidos**: [Rate limits, cuotas, restricciones]

---

## Out of Scope
❌ [Qué NO cubre esta spec - feature 1]  
❌ [Qué NO cubre esta spec - feature 2]  
❌ [Qué NO cubre esta spec - feature 3]

---

## Testing Strategy
```python
# tests/test_[feature_name].py

def test_scenario_1_happy_path():
    """Scenario 1: [Título]"""
    # Arrange
    [setup del contexto]
    
    # Act
    [ejecutar acción]
    
    # Assert
    [verificar resultado esperado]

def test_scenario_2_error_handling():
    """Scenario 2: [Título]"""
    with pytest.raises(ExpectedException):
        [acción que debe fallar]

def test_scenario_3_edge_case():
    """Scenario 3: [Título]"""
    # ...

# Agregar más tests según el número de escenarios
```

---

## Implementation Checklist
- [ ] Crear módulo `src/[feature_name].py`
- [ ] Implementar función/clase principal
- [ ] Añadir logging apropiado
- [ ] Crear tests en `tests/test_[feature_name].py`
- [ ] Verificar todos los escenarios pasan
- [ ] Actualizar README.md con documentación
- [ ] Añadir ejemplos de uso
- [ ] Revisar manejo de errores
- [ ] Validar con datos reales

---

## Related Specs
- [Link a spec relacionada 1]
- [Link a spec relacionada 2]

---

## Changelog
- **[YYYY-MM-DD]**: Spec inicial creada
- **[YYYY-MM-DD]**: Añadido Scenario X por [razón]
- **[YYYY-MM-DD]**: Actualizado comportamiento Y
