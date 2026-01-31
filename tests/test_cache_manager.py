"""
Tests for the cache manager (src/cache_manager.py).
"""
# pylint: disable=protected-access

import pytest

from src.cache_manager import CacheManager


class TestCacheManager:
    """Tests for the CacheManager class."""

    @pytest.fixture
    def cache(self, tmp_path):
        """
        Fixture that creates a CacheManager with isolated temporary storage.

        Args:
            tmp_path: pytest fixture providing temporary directory

        Returns:
            CacheManager instance using temporary directory
        """
        return CacheManager(cache_dir=str(tmp_path / "test_cache"), ttl_hours=24)

    def test_set_and_get_activities(self, cache):
        """Test that activities can be stored and retrieved from cache."""
        # Arrange
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        activities = [
            {"id": 1, "name": "Morning Run", "distance": 5.2},
            {"id": 2, "name": "Evening Bike", "distance": 15.0}
        ]

        # Act
        cache.set_activities(start_date, end_date, activities)
        retrieved = cache.get_activities(start_date, end_date)

        # Assert
        assert retrieved == activities

        # Verify cache stats show one valid entry
        stats = cache.get_cache_stats()
        assert stats["activities"]["valid"] == 1
        assert stats["activities"]["total"] == 1

    def test_cache_miss_returns_none(self, cache):
        """Test that get_activities returns None for uncached date range."""
        # Act
        result = cache.get_activities("2024-02-01", "2024-02-28")

        # Assert
        assert result is None

        # Verify cache stats show zero entries
        stats = cache.get_cache_stats()
        assert stats["activities"]["valid"] == 0
        assert stats["activities"]["total"] == 0

    def test_expired_entries_not_returned(self, tmp_path):
        """Test that expired cache entries are not returned and are cleaned up."""
        # Arrange - Create cache with TTL=0 (immediate expiration)
        cache = CacheManager(cache_dir=str(tmp_path / "expired_cache"), ttl_hours=0)
        activities = [{"id": 1, "name": "Test Activity"}]

        # Act
        cache.set_activities("2024-01-01", "2024-01-31", activities)
        retrieved = cache.get_activities("2024-01-01", "2024-01-31")

        # Assert - Should return None because entry is expired
        assert retrieved is None

        # Verify the expired entry was automatically cleaned up
        stats = cache.get_cache_stats()
        assert stats["activities"]["total"] == 0

    def test_body_composition_caching(self, cache):
        """Test that body composition data can be stored and retrieved."""
        # Arrange
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        composition = [
            {"date": "2024-01-01", "weight": 75.5, "bodyFat": 15.2},
            {"date": "2024-01-15", "weight": 74.8, "bodyFat": 14.9}
        ]

        # Act
        cache.set_body_composition(start_date, end_date, composition)
        retrieved = cache.get_body_composition(start_date, end_date)

        # Assert
        assert retrieved == composition

        # Verify it doesn't interfere with activities cache
        stats = cache.get_cache_stats()
        assert stats["body_composition"]["valid"] == 1
        assert stats["activities"]["valid"] == 0

    def test_user_profile_caching(self, cache):
        """Test that user profile can be stored and retrieved."""
        # Arrange
        profile = {
            "name": "Test User",
            "email": "test@example.com",
            "ftp": 250,
            "max_hr": 185
        }

        # Act
        cache.set_user_profile(profile, user_id="user123")
        retrieved = cache.get_user_profile(user_id="user123")

        # Assert
        assert retrieved == profile

        # Verify cache stats
        stats = cache.get_cache_stats()
        assert stats["user_profiles"]["valid"] == 1

    def test_cache_isolation_between_types(self, cache):
        """Test that different cache types are properly isolated."""
        # Arrange
        activities = [{"id": 1, "name": "Run"}]
        composition = [{"weight": 75.0}]
        profile = {"name": "Test"}

        # Act - Store data in all three caches
        cache.set_activities("2024-01-01", "2024-01-31", activities)
        cache.set_body_composition("2024-01-01", "2024-01-31", composition)
        cache.set_user_profile(profile)

        # Assert - Each type returns its own data
        assert cache.get_activities("2024-01-01", "2024-01-31") == activities
        assert cache.get_body_composition("2024-01-01", "2024-01-31") == composition
        assert cache.get_user_profile() == profile

        # Verify stats show one entry in each cache
        stats = cache.get_cache_stats()
        assert stats["activities"]["valid"] == 1
        assert stats["body_composition"]["valid"] == 1
        assert stats["user_profiles"]["valid"] == 1

    def test_clear_expired_removes_only_expired(self, tmp_path):
        """Test that clear_expired removes only expired entries."""
        # Arrange - Create cache with valid and expired entries
        valid_cache = CacheManager(cache_dir=str(tmp_path / "mixed"), ttl_hours=24)
        expired_cache = CacheManager(cache_dir=str(tmp_path / "mixed"), ttl_hours=0)

        # Add valid entry
        valid_cache.set_activities("2024-01-01", "2024-01-31", [{"id": 1}])

        # Add expired entry (using same cache dir but TTL=0)
        expired_cache.set_activities("2024-02-01", "2024-02-28", [{"id": 2}])

        # Act
        valid_cache.clear_expired()

        # Assert - Valid entry still retrievable, expired entry gone
        assert valid_cache.get_activities("2024-01-01", "2024-01-31") == [{"id": 1}]
        assert valid_cache.get_activities("2024-02-01", "2024-02-28") is None

        # Verify stats
        stats = valid_cache.get_cache_stats()
        assert stats["activities"]["valid"] == 1
        assert stats["activities"]["total"] == 1

    def test_clear_all_removes_everything(self, cache):
        """Test that clear_all removes all entries from all cache tables."""
        # Arrange - Add entries to all cache types
        cache.set_activities("2024-01-01", "2024-01-31", [{"id": 1}])
        cache.set_body_composition("2024-01-01", "2024-01-31", [{"weight": 75}])
        cache.set_user_profile({"name": "Test"})

        # Verify data exists
        stats_before = cache.get_cache_stats()
        assert stats_before["activities"]["total"] == 1
        assert stats_before["body_composition"]["total"] == 1
        assert stats_before["user_profiles"]["total"] == 1

        # Act
        cache.clear_all()

        # Assert - All caches are empty
        assert cache.get_activities("2024-01-01", "2024-01-31") is None
        assert cache.get_body_composition("2024-01-01", "2024-01-31") is None
        assert cache.get_user_profile() is None

        # Verify stats show zero entries
        stats_after = cache.get_cache_stats()
        assert stats_after["activities"]["total"] == 0
        assert stats_after["body_composition"]["total"] == 0
        assert stats_after["user_profiles"]["total"] == 0

    def test_cache_stats_accuracy(self, tmp_path):
        """Test that get_cache_stats returns accurate counts for valid and expired entries."""
        # Arrange - Create cache and add mix of valid and expired entries
        valid_cache = CacheManager(cache_dir=str(tmp_path / "stats_test"), ttl_hours=24)
        expired_cache = CacheManager(cache_dir=str(tmp_path / "stats_test"), ttl_hours=0)

        # Add 2 valid entries
        valid_cache.set_activities("2024-01-01", "2024-01-31", [{"id": 1}])
        valid_cache.set_body_composition("2024-01-01", "2024-01-31", [{"weight": 75}])

        # Add 1 expired entry
        expired_cache.set_activities("2024-02-01", "2024-02-28", [{"id": 2}])

        # Act
        stats = valid_cache.get_cache_stats()

        # Assert - Stats show correct counts
        assert stats["activities"]["total"] == 2  # 1 valid + 1 expired
        assert stats["activities"]["valid"] == 1
        assert stats["activities"]["expired"] == 1

        assert stats["body_composition"]["total"] == 1
        assert stats["body_composition"]["valid"] == 1
        assert stats["body_composition"]["expired"] == 0

    def test_cache_stats_includes_config_and_size(self, cache):
        """Test that cache stats include TTL config and database size."""
        # Arrange - Add some data to ensure DB exists
        cache.set_activities("2024-01-01", "2024-01-31", [{"id": 1}])

        # Act
        stats = cache.get_cache_stats()

        # Assert - Stats include TTL and database size
        assert "ttl_hours" in stats
        assert stats["ttl_hours"] == 24  # From fixture

        assert "cache_dir" in stats
        assert "db_size_bytes" in stats
        assert stats["db_size_bytes"] > 0  # DB has some size after adding data
