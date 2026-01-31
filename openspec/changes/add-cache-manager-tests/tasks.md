## 1. Create test file structure

- [x] 1.1 Create `tests/test_cache_manager.py` with imports and TestCacheManager class
- [x] 1.2 Add pytest fixture for creating isolated CacheManager instances

## 2. Test activities cache lifecycle

- [x] 2.1 Test `set_activities()` and `get_activities()` with matching data
- [x] 2.2 Test cache miss returns None for uncached date range
- [x] 2.3 Test expired entries are not returned (TTL=0)

## 3. Test body composition and user profile caching

- [x] 3.1 Test `set_body_composition()` and `get_body_composition()` work correctly
- [x] 3.2 Test `set_user_profile()` and `get_user_profile()` work correctly
- [x] 3.3 Verify cache isolation between data types

## 4. Test cleanup operations

- [x] 4.1 Test `clear_expired()` removes only expired entries
- [x] 4.2 Test `clear_all()` removes all entries from all tables

## 5. Test cache statistics

- [x] 5.1 Test `get_cache_stats()` returns accurate counts for valid/expired entries
- [x] 5.2 Test stats include TTL config and database size

## 6. Verify and run

- [x] 6.1 Run tests with `pytest tests/test_cache_manager.py -v`
- [x] 6.2 Verify all tests pass and coverage is comprehensive
