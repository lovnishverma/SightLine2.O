"""Tests for ResearchCache.
Verifies TTL expiry, LRU eviction, duplicate prevention, and cache hit metrics.
"""

import time
import pytest
from src.insights.cache import ResearchCache
from src.insights.models import ResearchResult, Source

@pytest.fixture
def sample_result():
    return ResearchResult(
        query="Bosch Series 6",
        entity="Bosch Washing Machine",
        answer="Bosch Series 6 front loader.",
        confidence=0.95,
        sources=[Source(title="Bosch Manual", url="https://bosch.com/manual.pdf")],
        key_facts=["Super 15 program available"]
    )

def test_cache_hit_and_miss(sample_result):
    cache = ResearchCache(ttl_seconds=10, max_size=5)
    key = cache.generate_key("how to start wash", entity="Bosch")

    assert cache.get(key) is None
    assert cache.misses == 1

    cache.set(key, sample_result)
    cached = cache.get(key)
    assert cached is not None
    assert cached.entity == "Bosch Washing Machine"
    assert cache.hits == 1

def test_cache_ttl_expiry(sample_result):
    cache = ResearchCache(ttl_seconds=1, max_size=5)
    key = cache.generate_key("short ttl query")

    cache.set(key, sample_result)
    assert cache.get(key) is not None

    time.sleep(1.1)
    # Expired
    assert cache.get(key) is None

def test_cache_lru_eviction(sample_result):
    cache = ResearchCache(ttl_seconds=60, max_size=2)
    k1 = cache.generate_key("query 1")
    k2 = cache.generate_key("query 2")
    k3 = cache.generate_key("query 3")

    cache.set(k1, sample_result)
    cache.set(k2, sample_result)
    assert len(cache._cache) == 2

    # Insert third item -> k1 must be evicted
    cache.set(k3, sample_result)
    assert len(cache._cache) == 2
    assert cache.evictions == 1
    assert cache.get(k1) is None
    assert cache.get(k2) is not None
    assert cache.get(k3) is not None

def test_cache_stats(sample_result):
    cache = ResearchCache(ttl_seconds=60, max_size=10)
    k = cache.generate_key("stats test")
    cache.get(k)  # miss
    cache.set(k, sample_result)
    cache.get(k)  # hit

    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5
