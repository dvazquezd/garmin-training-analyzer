# Feature: Análisis de Entrenamiento con Múltiples Proveedores LLM

## Context
**Por qué existe**: Los usuarios necesitan análisis inteligente de sus datos de entrenamiento. Los datos brutos (actividades, métricas) son difíciles de interpretar. Los LLMs pueden identificar patrones, sugerir mejoras y personalizar recomendaciones. Soportar múltiples proveedores (Anthropic, OpenAI, Google) permite flexibilidad según disponibilidad, coste y preferencias.

**Valor que aporta**:
- Análisis personalizado basado en historial completo
- Recomendaciones accionables (volumen, intensidad, recovery)
- Identificación de patrones y tendencias
- Flexibilidad de proveedor (Claude, GPT-4, Gemini)
- Gestión inteligente de tokens y costes

---

## User Story
**Como** atleta que analiza su entrenamiento  
**Quiero** recibir análisis inteligente generado por IA de mi progreso y recomendaciones personalizadas  
**Para** mejorar mi rendimiento basándome en datos objetivos

---

## Acceptance Criteria

### Scenario 1: Análisis exitoso con Claude (Anthropic)
**Given** el usuario tiene configurado:
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=3000
TEMPERATURE=0.7
```
**And** tiene 15 actividades y datos de composición corporal  
**When** ejecuta el análisis  
**Then** construye prompt con:
- System prompt (instrucciones de análisis)
- User prompt (datos estructurados en Markdown)
- Contexto: periodo, objetivos, métricas clave
**And** llama a Claude API:
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=3000,
    temperature=0.7,
    messages=[
        {"role": "user", "content": user_prompt}
    ]
)
```
**And** retorna análisis estructurado:
```markdown
## 1. RESUMEN EJECUTIVO
Tu entrenamiento muestra progresión consistente...

## 2. ANÁLISIS DE VOLUMEN
Total: 312 km en 60 días...

## 3. ZONAS DE FRECUENCIA CARDÍACA
Distribución adecuada con 65% en Z2...

## 4. COMPOSICIÓN CORPORAL
Reducción de 1.2 kg en peso, -0.7% grasa...

## 5. RECOMENDACIONES
1. Mantener volumen actual...
2. Añadir 1 sesión semanal de Z4...
```
**And** registra metadata:
```
✅ Análisis generado con Claude Sonnet 4
   Tokens usados: 2,847 / 3,000
   Tiempo: 4.2s
   Coste estimado: $0.021
```

---

### Scenario 2: Fallback a GPT-4 si Claude falla
**Given** el usuario tiene configurado `LLM_PROVIDER=anthropic`  
**And** Claude API retorna error `503 Service Unavailable`  
**When** intenta generar análisis  
**Then** el sistema detecta el fallo  
**And** registra: `"⚠️  Claude no disponible. Intentando con GPT-4..."`  
**And** verifica que existe `OPENAI_API_KEY`  
**And** reintentar con OpenAI API  
**And** retorna análisis exitoso de GPT-4  
**And** registra: `"✅ Análisis generado con GPT-4 (fallback)"`  
**And** NO falla completamente (resiliencia)

---

### Scenario 3: Análisis con GPT-4 (OpenAI)
**Given** el usuario configura:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o
MAX_TOKENS=3000
TEMPERATURE=0.7
```
**When** ejecuta el análisis  
**Then** llama a OpenAI API:
```python
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=3000,
    temperature=0.7,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)
```
**And** extrae respuesta: `response.choices[0].message.content`  
**And** retorna análisis estructurado  
**And** registra metadata con tokens y coste estimado

---

### Scenario 4: Análisis con Gemini (Google)
**Given** el usuario configura:
```env
LLM_PROVIDER=google
GOOGLE_API_KEY=AIxxxxx
GOOGLE_MODEL=gemini-2.0-flash-exp
MAX_TOKENS=3000
TEMPERATURE=0.7
```
**When** ejecuta el análisis  
**Then** llama a Google Gemini API:
```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(
    prompt,
    generation_config={
        'max_output_tokens': 3000,
        'temperature': 0.7
    }
)
```
**And** extrae respuesta: `response.text`  
**And** retorna análisis estructurado  
**And** registra metadata

---

### Scenario 5: Datos insuficientes para análisis
**Given** el usuario solo tiene 2 actividades en el periodo  
**When** intenta generar análisis  
**Then** el sistema detecta datos insuficientes  
**And** muestra warning:
```
⚠️  Datos insuficientes para análisis completo
   Actividades encontradas: 2
   Mínimo recomendado: 5

   Sugerencias:
   - Aumenta ANALYSIS_DAYS a 60 o 90
   - Sincroniza más actividades desde Garmin
   - Espera a tener más entrenamientos
```
**And** pregunta al usuario: `"¿Deseas continuar con análisis limitado? (s/n)"`  
**And** si usuario dice "no", termina sin llamar LLM (ahorro de tokens)  
**And** si dice "sí", genera análisis con disclaimer

---

### Scenario 6: Límite de tokens excedido - truncar datos
**Given** el usuario tiene 150 actividades en periodo largo (180 días)  
**And** el prompt completo requiere 12,000 tokens  
**And** `MAX_TOKENS=8000` (límite del modelo)  
**When** construye el prompt  
**Then** detecta que datos exceden límite  
**And** registra: `"⚠️  Datos exceden límite de tokens (12k > 8k)"`  
**And** aplica estrategia de truncamiento:
  1. Prioriza actividades más recientes (últimas 50)
  2. Resume composición corporal (solo inicio/fin/tendencia)
  3. Agrupa actividades por semana (en lugar de individual)
**And** verifica que prompt final < 6,000 tokens (margen de seguridad)  
**And** incluye nota en prompt: `"[Datos resumidos debido a límite de tokens]"`  
**And** el análisis menciona que se trabajó con muestra representativa

---

### Scenario 7: Rate limiting del proveedor LLM
**Given** el usuario ejecuta análisis 10 veces en 1 minuto  
**And** el proveedor retorna `429 Too Many Requests`  
**When** intenta el request 11  
**Then** detecta rate limit  
**And** extrae header `Retry-After: 60` (segundos)  
**And** muestra mensaje:
```
⏸️  Rate limit alcanzado con Anthropic API
   Esperando 60 segundos antes de reintentar...
   [████████████░░░░░░░░] 40s / 60s
```
**And** espera el tiempo indicado  
**And** reintenta automáticamente  
**And** si falla 3 veces, termina con error explicativo

---

### Scenario 8: API Key inválida o expirada
**Given** el usuario configura `ANTHROPIC_API_KEY=sk-ant-invalid`  
**When** intenta generar análisis  
**Then** Claude API retorna `401 Unauthorized`  
**And** el sistema detecta error de autenticación  
**And** muestra mensaje claro:
```
❌ API Key de Anthropic inválida o expirada

   Verifica tu configuración en .env:
   - ANTHROPIC_API_KEY debe empezar con 'sk-ant-'
   - Obtén una nueva key en: console.anthropic.com

   Si acabas de crear la key, espera 5 minutos para propagación.
```
**And** NO revela la API key en logs (seguridad)  
**And** termina con código de salida `1`

---

### Scenario 9: Respuesta malformada del LLM - retry
**Given** el LLM retorna respuesta incompleta o corrupta (JSON inválido si esperamos JSON)  
**When** intenta parsear la respuesta  
**Then** detecta formato inválido  
**And** registra: `"⚠️  Respuesta malformada del LLM. Reintentando..."`  
**And** modifica prompt añadiendo: `"IMPORTANTE: Responde solo con Markdown bien formateado"`  
**And** reintenta con temperatura reducida (0.3 para más determinismo)  
**And** máximo 2 reintentos  
**And** si persiste, retorna respuesta raw con warning al usuario

---

### Scenario 10: Personalización del system prompt
**Given** el usuario tiene archivo custom `prompts/system_prompt.txt`:
```
Eres un entrenador de running experto. 
Analiza datos con enfoque en:
- Prevención de lesiones
- Progresión gradual
- Balance trabajo-descanso
```
**When** carga el prompt  
**Then** lee desde `prompts/system_prompt.txt`  
**And** verifica que el archivo existe y es legible  
**And** usa ese prompt en lugar del default  
**And** registra: `"📝 Usando system prompt personalizado"`  
**And** si el archivo no existe, usa prompt default + warning

---

### Scenario 11: Análisis multiidioma (español/inglés)
**Given** el usuario configura `LANGUAGE=es` en `.env`  
**When** genera análisis  
**Then** el system prompt incluye: `"Responde en español"`  
**And** el análisis retornado está completamente en español  
**And** términos técnicos traducidos correctamente:
  - "Heart Rate Zones" → "Zonas de Frecuencia Cardíaca"
  - "Training Load" → "Carga de Entrenamiento"
  - "Recovery" → "Recuperación"
**And** formato de fechas localizado (DD/MM/YYYY para español)

---

### Scenario 12: Estimación de costes antes de ejecutar
**Given** el usuario ejecuta con flag `--estimate-cost`  
**When** construye el prompt  
**Then** calcula estimación sin llamar API:
```
📊 Estimación de Coste
┌─────────────────────┬──────────┐
│ Proveedor           │ Claude   │
│ Modelo              │ Sonnet 4 │
│ Tokens input (est.) │ 4,200    │
│ Tokens output (max) │ 3,000    │
│ Coste input         │ $0.012   │
│ Coste output        │ $0.045   │
│ Total estimado      │ $0.057   │
└─────────────────────┴──────────┘

Precios actualizados: 2025-01-30
¿Continuar con el análisis? (s/n):
```
**And** espera confirmación del usuario  
**And** si dice "no", termina sin consumir tokens

---

## Technical Notes
- **Proveedores soportados**:
  - Anthropic: Claude Opus 4.5, Sonnet 4.5, Haiku 4.5
  - OpenAI: GPT-4o, GPT-4o-mini
  - Google: Gemini 2.0 Flash, Gemini Pro
- **Librerías**:
  - `anthropic` (pip install anthropic)
  - `openai` (pip install openai)
  - `google-generativeai` (pip install google-generativeai)
- **Gestión de tokens**:
  - Usar tokenizer apropiado para cada modelo (tiktoken para OpenAI, etc.)
  - Siempre dejar margen de seguridad (usar 80% del max_tokens)
- **Costes aproximados** (a enero 2025):
  - Claude Sonnet 4: $3/MTok input, $15/MTok output
  - GPT-4o: $2.50/MTok input, $10/MTok output
  - Gemini Flash: $0.075/MTok input, $0.30/MTok output
- **Rate limits**:
  - Anthropic: ~50 requests/min (tier 1)
  - OpenAI: ~500 requests/min (tier 1)
  - Google: ~60 requests/min (free tier)
- **Retry logic**:
  - Exponential backoff: 2s, 4s, 8s
  - Máximo 3 reintentos
  - Respetar header `Retry-After`

---

## Out of Scope
❌ Fine-tuning de modelos propios  
❌ Embeddings para búsqueda semántica  
❌ Streaming de respuestas (todo o nada)  
❌ Función calling / Tool use  
❌ Análisis de imágenes (fotos de entrenamientos)  
❌ Multi-turn conversations (solo single-shot)

---

## Testing Strategy
```python
# tests/test_llm_analyzer.py

import pytest
from unittest.mock import patch, MagicMock
from src.llm_analyzer import LLMAnalyzer

def test_successful_analysis_with_claude():
    """Scenario 1: Claude analysis"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="## ANÁLISIS...")]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 2000
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        analyzer = LLMAnalyzer(provider='anthropic')
        result = analyzer.analyze(activities=mock_activities(15))
        
        assert "## ANÁLISIS" in result['text']
        assert result['tokens_used'] == 3000
        assert result['provider'] == 'anthropic'

def test_fallback_to_gpt4_when_claude_fails():
    """Scenario 2: Fallback logic"""
    with patch('anthropic.Anthropic') as mock_anthropic, \
         patch('openai.OpenAI') as mock_openai:
        
        # Claude fails
        mock_anthropic.return_value.messages.create.side_effect = Exception("503")
        
        # GPT-4 succeeds
        mock_gpt_response = MagicMock()
        mock_gpt_response.choices = [MagicMock(message=MagicMock(content="Analysis..."))]
        mock_openai.return_value.chat.completions.create.return_value = mock_gpt_response
        
        analyzer = LLMAnalyzer(provider='anthropic', fallback='openai')
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert result['provider'] == 'openai'
        assert result['was_fallback'] is True

def test_analysis_with_gpt4():
    """Scenario 3: GPT-4 analysis"""
    with patch('openai.OpenAI') as mock_openai:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="## Analysis..."))]
        mock_response.usage.prompt_tokens = 1500
        mock_response.usage.completion_tokens = 2500
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        analyzer = LLMAnalyzer(provider='openai')
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert "## Analysis" in result['text']
        assert result['tokens_used'] == 4000

def test_analysis_with_gemini():
    """Scenario 4: Gemini analysis"""
    with patch('google.generativeai.GenerativeModel') as mock_gemini:
        mock_response = MagicMock()
        mock_response.text = "## Análisis detallado..."
        mock_gemini.return_value.generate_content.return_value = mock_response
        
        analyzer = LLMAnalyzer(provider='google')
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert "## Análisis" in result['text']

def test_insufficient_data_warning(caplog):
    """Scenario 5: Insufficient data"""
    analyzer = LLMAnalyzer()
    
    with pytest.raises(ValueError, match="Datos insuficientes"):
        analyzer.analyze(activities=mock_activities(2))
    
    assert "Mínimo recomendado: 5" in caplog.text

def test_token_limit_truncation(caplog):
    """Scenario 6: Token limit handling"""
    analyzer = LLMAnalyzer(max_tokens=8000)
    large_activities = mock_activities(150)  # Huge dataset
    
    with patch.object(analyzer, '_estimate_tokens', return_value=12000):
        prompt = analyzer._build_prompt(large_activities)
        
        assert "[Datos resumidos" in prompt
        assert "⚠️  Datos exceden límite" in caplog.text

def test_rate_limit_retry():
    """Scenario 7: Rate limiting"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        from anthropic import RateLimitError
        
        mock_anthropic.return_value.messages.create.side_effect = [
            RateLimitError("429", response=MagicMock(headers={'Retry-After': '5'})),
            MagicMock(content=[MagicMock(text="Analysis...")])
        ]
        
        analyzer = LLMAnalyzer()
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert result is not None
        assert mock_anthropic.return_value.messages.create.call_count == 2

def test_invalid_api_key():
    """Scenario 8: Invalid API key"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        from anthropic import AuthenticationError
        
        mock_anthropic.return_value.messages.create.side_effect = AuthenticationError("401")
        
        analyzer = LLMAnalyzer(provider='anthropic')
        
        with pytest.raises(SystemExit) as exc_info:
            analyzer.analyze(activities=mock_activities(10))
        
        assert exc_info.value.code == 1

def test_malformed_response_retry():
    """Scenario 9: Malformed response"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = [
            MagicMock(content=[MagicMock(text="<incomplete")]),  # Bad
            MagicMock(content=[MagicMock(text="## Complete analysis...")])  # Good
        ]
        
        analyzer = LLMAnalyzer()
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert "## Complete" in result['text']

def test_custom_system_prompt(tmp_path):
    """Scenario 10: Custom prompt"""
    custom_prompt = tmp_path / "system_prompt.txt"
    custom_prompt.write_text("Eres un entrenador experto...")
    
    analyzer = LLMAnalyzer(system_prompt_path=custom_prompt)
    
    assert "entrenador experto" in analyzer.system_prompt

def test_multilingual_analysis_spanish():
    """Scenario 11: Spanish language"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="## Análisis en español...")]
        mock_anthropic.return_value.messages.create.return_value = mock_response
        
        analyzer = LLMAnalyzer(language='es')
        result = analyzer.analyze(activities=mock_activities(10))
        
        assert "español" in result['text'].lower()
        assert "Responde en español" in analyzer.system_prompt

def test_cost_estimation():
    """Scenario 12: Cost estimation"""
    analyzer = LLMAnalyzer(provider='anthropic', model='claude-sonnet-4-20250514')
    
    estimate = analyzer.estimate_cost(
        activities=mock_activities(10),
        execute=False
    )
    
    assert 'input_tokens' in estimate
    assert 'output_tokens' in estimate
    assert 'total_cost' in estimate
    assert estimate['total_cost'] > 0
```

---

## Implementation Checklist
- [ ] Crear módulo `src/llm_analyzer.py` con clase `LLMAnalyzer`
- [ ] Implementar soporte para 3 proveedores (Anthropic, OpenAI, Google)
- [ ] Añadir lógica de fallback automático
- [ ] Implementar gestión de tokens (estimación y truncamiento)
- [ ] Añadir retry logic con exponential backoff
- [ ] Implementar manejo de rate limits (respeto de `Retry-After`)
- [ ] Crear sistema de carga de prompts externos
- [ ] Añadir soporte multiidioma (español/inglés)
- [ ] Implementar estimación de costes
- [ ] Crear detector de datos insuficientes
- [ ] Añadir logging detallado (provider, tokens, tiempo, coste)
- [ ] Crear tests en `tests/test_llm_analyzer.py` (12 tests)
- [ ] Documentar configuración de cada proveedor en README
- [ ] Añadir ejemplos de prompts en `prompts/examples/`

---

## Related Specs
- [Prompt Management](./prompt-management.spec.md) - Gestión de prompts externos
- [Activities Extraction](../02-data-extraction/activities.spec.md) - Datos fuente para análisis
- [HTML Reports](../05-reporting/html-reports.spec.md) - Consume el análisis generado

---

## Changelog
- **2025-01-30**: Spec inicial creada con 12 escenarios
- **2025-01-30**: Añadido Scenario 11 (multiidioma) para soporte español/inglés
- **2025-01-30**: Añadido Scenario 12 (estimación de costes) para transparencia
