"""Data models for iNSIGHTS Research and Intelligence Layer.
Provides typed structures for Evidence, Sources, Knowledge Graphs, and Routing.
"""

from dataclasses import dataclass, field, asdict
import time
from typing import List, Dict, Any, Optional

@dataclass
class Source:
    """Individual verified source reference backing research claims."""
    title: str
    url: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    source_type: str = "official_docs"  # "official_docs", "manual", "technical", "government", "news", etc.
    confidence_score: float = 0.9
    snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvidenceChunk:
    """Specific verifiable excerpt extracted from a retrieved document or page."""
    chunk_text: str
    source_title: str
    relevance_score: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class KnowledgeCluster:
    """Contextual knowledge graph representation for an identified entity."""
    entity_name: str
    category: str = "general"  # "appliance", "document", "medicine", "hardware", "place", "general"
    attributes: Dict[str, Any] = field(default_factory=dict)
    # Common attributes:
    # - model / brand
    # - controls / operations
    # - programs / modes
    # - safety / warnings
    # - maintenance / troubleshooting
    # - manual_url
    # - deadlines / required_docs (for documents)
    verified_facts: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RouteDecision:
    """Decision produced by the IntelligenceRouter."""
    route: str  # "LOCAL_VISION" or "INSIGHTS_RESEARCH"
    confidence: float
    reason: str
    extracted_entity: str = ""
    suggested_task_token: str = "<DETAILED_CAPTION>"

    @property
    def is_research(self) -> bool:
        return self.route == "INSIGHTS_RESEARCH"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ResearchResult:
    """Evidence-first structured response from iNSIGHTS research."""
    query: str
    entity: str
    answer: str  # Concise, natural phrasing formatted for voice output / TTS
    confidence: float = 0.95
    sources: List[Source] = field(default_factory=list)
    evidence_chunks: List[EvidenceChunk] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    research_summary: str = ""  # Comprehensive summary for the visual UI / Judge Mode
    timestamp: float = field(default_factory=time.time)
    provider: str = "iNSIGHTS DeepSearch"
    route_reason: str = ""
    suggested_followups: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    knowledge_cluster: Optional[KnowledgeCluster] = None
    language: str = "en"
    latency_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.knowledge_cluster:
            data["knowledge_cluster"] = self.knowledge_cluster.to_dict()
        return data

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def is_reliable(self) -> bool:
        return self.confidence >= 0.70 and len(self.sources) > 0
