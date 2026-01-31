## Context

The HealthAdv project uses pytest for testing, with existing test files in tests/ following a consistent pattern:
- Class-based test organization (`TestClassName`)
- Descriptive test names (`test_method_scenario`)
- Use of pytest fixtures (defined in tests/conftest.py)
- Minimal mocking, preferring real implementations where practical

The CacheManager (src/cache_manager.py) uses SQLite for persistence, creating database files in a configurable directory. Tests need isolated storage to avoid interference.

## Goals / Non-Goals

**Goals:**
- Test all public methods of CacheManager
- Verify TTL expiration behavior
- Ensure cache isolation between data types
- Validate cleanup operations (clear_expired, clear_all)
- Test cache statistics accuracy
- Use temporary directories for test isolation

**Non-Goals:**
- Testing SQLite itself (we trust the database engine)
- Testing internal methods (focus on public API)
- Performance benchmarking (functional tests only)
- Integration with GarminClient (CacheManager is unit tested in isolation)

## Decisions

### Decision 1: Use pytest tmpdir fixture for isolation

**Approach:** Each test will receive a pytest `tmp_path` fixture and create a CacheManager instance pointing to that temporary directory.

**Rationale:**
- Prevents test interference (each test gets clean storage)
- Automatic cleanup by pytest
- Standard pytest pattern used elsewhere in the project

**Example:**
```python
def test_something(tmp_path):
    cache = CacheManager(cache_dir=str(tmp_path))
    # Test uses isolated cache
```

### Decision 2: Test TTL expiration with short TTL values

**Approach:** Create CacheManager instances with `ttl_hours=0` or very small values to test expiration without waiting.

**Rationale:**
- Fast test execution
- Predictable behavior (no timing races)
- TTL logic is the same regardless of duration

### Decision 3: Follow existing test pattern from test_prompt_manager.py

**Approach:** Mirror the structure and style of tests/test_prompt_manager.py:
- Single test class `TestCacheManager`
- Descriptive test method names
- Direct assertions without heavy mocking

**Rationale:**
- Consistency with existing test suite
- Familiar patterns for developers
- Proven approach already working in the project

### Decision 4: Test one cache type thoroughly, others briefly

**Approach:**
- Activities cache: comprehensive tests (lifecycle, expiration, stats)
- Body composition & user profile: basic tests (verify they work, check isolation)

**Rationale:**
- All three cache types use the same underlying logic
- Avoid repetitive tests
- Still validate that all types work correctly
