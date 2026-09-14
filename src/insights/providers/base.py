"""Abstract base interface for all iNSIGHTS research providers.
Ensures loose coupling, dependency injection, and testability.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.insights.models import ResearchResult, Source, KnowledgeCluster

class ResearchProvider(ABC):
    """Abstract interface defining required intelligence and research capabilities."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name."""
        pass

    @abstractmethod
    def research(
        self,
        query: str,
        entity: str = "",
        visual_scene: str = "",
        ocr_text: str = "",
        previous_facts: Optional[List[str]] = None,
        language: str = "en"
    ) -> ResearchResult:
        """Perform contextual deep research backed by verified web sources."""
        pass

    @abstractmethod
    def analyze_document(
        self,
        ocr_text: str,
        document_type: str = "general",
        language: str = "en"
    ) -> ResearchResult:
        """Extract structured intelligence, deadlines, and summaries from OCR text."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Source]:
        """Retrieve verified sources for an explicit query."""
        pass

    @abstractmethod
    def create_knowledge_context(
        self,
        entity: str,
        facts: List[str],
        attributes: Optional[Dict[str, Any]] = None
    ) -> KnowledgeCluster:
        """Synthesize a structured knowledge graph cluster for an entity."""
        pass
