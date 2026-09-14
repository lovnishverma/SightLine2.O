"""High-level iNSIGHTS client managing caching, provider selection, and graceful fallback.
Ensures network resilience and observability.
"""

import time
import logging
from typing import Optional, List, Dict, Any

from src.config import CONFIG
from src.insights.models import ResearchResult, Source
from src.insights.cache import ResearchCache
from src.insights.providers.base import ResearchProvider
from src.insights.providers.live import InsightsLiveProvider
from src.insights.providers.mock import MockResearchProvider
from src.insights.exceptions import InsightsError, InsightsUnavailableError

logger = logging.getLogger("sightline.insights")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class InsightsClient:
    """Client orchestrating iNSIGHTS research with LRU/TTL caching and fallback protection."""

    def __init__(
        self,
        provider: Optional[ResearchProvider] = None,
        cache: Optional[ResearchCache] = None,
        enable_cache: bool = True
    ):
        self.enable_cache = enable_cache
        self.cache = cache or ResearchCache(ttl_seconds=CONFIG.INSIGHTS_CACHE_TTL)
        
        if provider:
            self.provider = provider
        elif CONFIG.INSIGHTS_PROVIDER == "mock":
            self.provider = MockResearchProvider()
        else:
            self.provider = InsightsLiveProvider()

        # Offline fallback provider
        self._mock_fallback = MockResearchProvider()

    def research(
        self,
        query: str,
        entity: str = "",
        visual_scene: str = "",
        ocr_text: str = "",
        previous_facts: Optional[List[str]] = None,
        language: str = "en"
    ) -> ResearchResult:
        """Execute deep research with caching and fallback protection."""
        if not CONFIG.INSIGHTS_ENABLED:
            logger.info("iNSIGHTS disabled via config. Skipping research.")
            raise InsightsUnavailableError("iNSIGHTS integration is currently disabled in settings.")

        cache_key = ""
        if self.enable_cache:
            cache_key = self.cache.generate_key(
                query=query,
                entity=entity,
                ocr_text=ocr_text,
                language=language
            )
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"cache.hit=true key={cache_key[:8]} entity='{entity}'")
                cached_result.research_summary += " *(Served from fast cache)*"
                return cached_result
            else:
                logger.info(f"cache.hit=false key={cache_key[:8]}")

        t0 = time.time()
        try:
            logger.info(f"research.start provider='{self.provider.name}' query='{query}' entity='{entity}'")
            result = self.provider.research(
                query=query,
                entity=entity,
                visual_scene=visual_scene,
                ocr_text=ocr_text,
                previous_facts=previous_facts,
                language=language
            )
            logger.info(
                f"research.completed sources={result.source_count} "
                f"latency={result.latency_seconds}s confidence={result.confidence}"
            )

        except InsightsError as ie:
            logger.warning(f"research.failed error='{ie.message}'. Attempting offline fallback.")
            try:
                result = self._mock_fallback.research(
                    query=query,
                    entity=entity,
                    visual_scene=visual_scene,
                    ocr_text=ocr_text,
                    previous_facts=previous_facts,
                    language=language
                )
                result.research_summary = (
                    f"*(Live research endpoint unreachable; resolved via offline knowledge base)*\n\n"
                    f"{result.research_summary}"
                )
                logger.info("research.fallback.success")
            except Exception:
                raise ie

        except Exception as e:
            logger.error(f"research.unexpected_error: {e}")
            raise InsightsUnavailableError(f"Research service error: {e}")

        # Store in cache
        if self.enable_cache and cache_key and result:
            self.cache.set(cache_key, result)

        return result

    def analyze_document(
        self,
        ocr_text: str,
        document_type: str = "general",
        language: str = "en"
    ) -> ResearchResult:
        """Process document OCR text with Document Intelligence."""
        if not CONFIG.INSIGHTS_ENABLED:
            raise InsightsUnavailableError("iNSIGHTS integration is currently disabled.")

        cache_key = ""
        if self.enable_cache:
            cache_key = self.cache.generate_key(
                query="analyze_document",
                ocr_text=ocr_text,
                language=language
            )
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        try:
            logger.info(f"document.analysis.start provider='{self.provider.name}'")
            result = self.provider.analyze_document(
                ocr_text=ocr_text,
                document_type=document_type,
                language=language
            )
            logger.info(f"document.analysis.completed latency={result.latency_seconds}s")
        except InsightsError as ie:
            logger.warning(f"document.analysis.failed error='{ie.message}'. Using mock fallback.")
            result = self._mock_fallback.analyze_document(ocr_text=ocr_text, language=language)

        if self.enable_cache and cache_key and result:
            self.cache.set(cache_key, result)

        return result

    def search(self, query: str, limit: int = 5) -> List[Source]:
        """Direct search query."""
        try:
            return self.provider.search(query=query, limit=limit)
        except Exception as e:
            logger.warning(f"search error: {e}. Fallback to mock search.")
            return self._mock_fallback.search(query=query, limit=limit)
