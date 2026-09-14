"""Bounded in-memory LRU cache with TTL for iNSIGHTS research results.
Prevents redundant external network queries and maintains high responsiveness.
"""

import threading
import time
import hashlib
from typing import Optional, Dict, Any, Tuple
from collections import OrderedDict

from src.insights.models import ResearchResult

class ResearchCache:
    """Thread-safe LRU cache with time-to-live (TTL) expiry."""

    def __init__(self, ttl_seconds: int = 1800, max_size: int = 100):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[ResearchResult, float]] = OrderedDict()
        self._lock = threading.Lock()
        
        # Statistics
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0

    @staticmethod
    def generate_key(query: str, entity: str = "", ocr_text: str = "", language: str = "en") -> str:
        """Create a deterministic hash key from query attributes."""
        norm_query = " ".join(query.lower().strip().split())
        norm_entity = " ".join(entity.lower().strip().split())
        # Use first 100 chars of OCR text if present to differentiate similar visual scenes
        norm_ocr = " ".join(ocr_text[:120].lower().strip().split()) if ocr_text else ""
        norm_lang = language.lower().strip()

        composite = f"q:{norm_query}|e:{norm_entity}|ocr:{norm_ocr}|l:{norm_lang}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[ResearchResult]:
        """Retrieve cached research result if not expired."""
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None

            result, insert_time = self._cache[key]
            current_time = time.time()

            # Check TTL expiry
            if current_time - insert_time > self.ttl:
                del self._cache[key]
                self.misses += 1
                return None

            # Move to end for LRU ordering
            self._cache.move_to_end(key)
            self.hits += 1
            return result

    def set(self, key: str, result: ResearchResult):
        """Store research result in cache, evicting oldest if capacity reached."""
        with self._lock:
            current_time = time.time()

            if key in self._cache:
                self._cache[key] = (result, current_time)
                self._cache.move_to_end(key)
                return

            if len(self._cache) >= self.max_size:
                # Evict oldest
                self._cache.popitem(last=False)
                self.evictions += 1

            self._cache[key] = (result, current_time)

    def clear(self):
        """Clear all cache items."""
        with self._lock:
            self._cache.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        """Return cache health metrics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate": round(hit_rate, 3)
            }
