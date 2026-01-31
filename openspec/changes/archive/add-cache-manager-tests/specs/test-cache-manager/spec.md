## ADDED Requirements

### Requirement: Cache Lifecycle Testing

The test suite must validate that CacheManager correctly stores, retrieves, and expires cached data across all cache types (activities, body composition, user profile).

#### Scenario: Store and retrieve activities from cache

- **WHEN** activities are saved with `set_activities()` and then retrieved with `get_activities()` using the same date range
- **THEN** the retrieved data matches the saved data exactly
- **AND** cache stats show one valid entry in the activities cache

#### Scenario: Cache miss returns None

- **WHEN** `get_activities()` is called with a date range that has never been cached
- **THEN** the method returns None
- **AND** cache stats show zero valid entries

#### Scenario: Expired cache entries are not returned

- **WHEN** an entry is cached with TTL=0 hours (immediate expiration) and then retrieved
- **THEN** `get_activities()` returns None
- **AND** the expired entry is automatically cleaned up from the database

### Requirement: Multi-Type Cache Testing

The test suite must validate caching behavior for all three data types: activities, body composition, and user profiles.

#### Scenario: Body composition caching works independently

- **WHEN** body composition data is saved and retrieved
- **THEN** it works correctly without interfering with activities cache
- **AND** cache keys are properly isolated between data types

#### Scenario: User profile caching with different TTL

- **WHEN** a user profile is saved (which has 7x longer TTL than other data)
- **THEN** the profile is retrievable
- **AND** cache stats reflect the extended expiration time

### Requirement: Cache Cleanup Operations

The test suite must validate that cleanup operations work correctly.

#### Scenario: Clear expired removes only expired entries

- **WHEN** cache contains both valid and expired entries, and `clear_expired()` is called
- **THEN** only expired entries are removed
- **AND** valid entries remain retrievable

#### Scenario: Clear all removes everything

- **WHEN** `clear_all()` is called on a cache with multiple entries
- **THEN** all cache tables are empty
- **AND** cache stats show zero total entries

### Requirement: Cache Statistics Accuracy

The test suite must validate that `get_cache_stats()` returns accurate information.

#### Scenario: Stats reflect cache state accurately

- **WHEN** multiple items are cached across different tables
- **THEN** `get_cache_stats()` shows correct counts for total, valid, and expired entries
- **AND** TTL configuration and database size are included in stats

### Requirement: Test Isolation and Cleanup

Each test must use isolated temporary storage to prevent test interference.

#### Scenario: Tests use temporary cache directories

- **WHEN** each test runs
- **THEN** it creates a CacheManager with a unique temporary directory (using pytest tmpdir fixture)
- **AND** the temporary directory is automatically cleaned up after the test
