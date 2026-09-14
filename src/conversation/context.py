"""Thread-safe application state and conversational memory.
Extends baseline session context with bounded Research Memory and Knowledge Clusters.
"""

from dataclasses import dataclass, field
import threading
import time
from typing import List, Dict, Any, Optional, Tuple

from src.insights.models import ResearchResult, KnowledgeCluster, Source

@dataclass
class SessionContext:
    """Thread-safe application state and bounded conversational context."""

    # Scene hashing & baseline tracking
    last_hash: Optional[bytes] = None
    last_task: str = ""
    last_text: str = ""
    last_audio: Optional[str] = None

    # Realtime stream tracking
    realtime_active: bool = False
    last_capture_time: float = 0.0
    last_frame: Optional[Any] = None

    # History
    history: List[Dict[str, Any]] = field(default_factory=list)
    max_history: int = 50

    # Research & Context Memory (Bounded)
    last_ocr: str = ""
    active_entity: str = ""
    researched_entities: List[str] = field(default_factory=list)
    knowledge_clusters: Dict[str, KnowledgeCluster] = field(default_factory=dict)
    verified_facts: List[str] = field(default_factory=list)
    recent_sources: List[Source] = field(default_factory=list)
    last_research: Optional[ResearchResult] = None
    
    # Memory limits
    max_entities: int = 10
    max_facts: int = 30
    max_sources: int = 20

    # Lock
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def update(self, hash_val: bytes, task: str, text: str, audio: Optional[str]):
        """Update state with new capture results."""
        with self._lock:
            self.last_hash = hash_val
            self.last_task = task
            self.last_text = text
            self.last_audio = audio
            
            # Add to history
            self.history.insert(0, {
                "time": time.strftime("%H:%M:%S"),
                "task": task,
                "text": text,
            })
            if len(self.history) > self.max_history:
                self.history = self.history[: self.max_history]

    def store_frame(self, frame: Any):
        """Store the latest live webcam frame in memory."""
        with self._lock:
            self.last_frame = frame

    def get_last_frame(self) -> Optional[Any]:
        """Retrieve the latest live webcam frame from memory."""
        with self._lock:
            return self.last_frame

    def store_ocr(self, ocr_text: str):
        """Store the most recently detected OCR text."""
        with self._lock:
            self.last_ocr = ocr_text.strip()

    def store_research(self, result: ResearchResult):
        """Store a research result into bounded memory and update knowledge cluster."""
        with self._lock:
            self.last_research = result
            if result.entity:
                self.active_entity = result.entity
                if result.entity not in self.researched_entities:
                    self.researched_entities.insert(0, result.entity)
                    if len(self.researched_entities) > self.max_entities:
                        evicted = self.researched_entities.pop()
                        self.knowledge_clusters.pop(evicted, None)

            # Store knowledge cluster
            if result.knowledge_cluster and result.entity:
                self.knowledge_clusters[result.entity] = result.knowledge_cluster

            # Store facts (FIFO bounded)
            for fact in result.key_facts:
                if fact not in self.verified_facts:
                    self.verified_facts.insert(0, fact)
            if len(self.verified_facts) > self.max_facts:
                self.verified_facts = self.verified_facts[: self.max_facts]

            # Store sources (FIFO bounded)
            for s in result.sources:
                if not any(existing.url == s.url for existing in self.recent_sources):
                    self.recent_sources.insert(0, s)
            if len(self.recent_sources) > self.max_sources:
                self.recent_sources = self.recent_sources[: self.max_sources]

    def get_recent_facts(self, entity: str = "") -> List[str]:
        """Retrieve verified facts, prioritizing the active entity."""
        with self._lock:
            if entity and entity in self.knowledge_clusters:
                return self.knowledge_clusters[entity].verified_facts
            return list(self.verified_facts[:10])

    def get_active_entity(self) -> str:
        """Get the current physical entity being explored."""
        with self._lock:
            return self.active_entity

    def get_knowledge_cluster(self, entity: str = "") -> Optional[KnowledgeCluster]:
        """Retrieve active knowledge graph for an entity."""
        with self._lock:
            target = entity or self.active_entity
            return self.knowledge_clusters.get(target)

    def get_last_research(self) -> Optional[ResearchResult]:
        """Get last research result."""
        with self._lock:
            return self.last_research

    def is_duplicate(self, hash_val: bytes, task: str) -> bool:
        """Check if this hash+task combination was already processed."""
        with self._lock:
            return (
                self.last_hash is not None
                and self.last_hash == hash_val
                and self.last_task == task
                and self.last_text != ""
            )

    def get_last(self) -> Tuple[str, Optional[str]]:
        """Get last description text and audio."""
        with self._lock:
            return self.last_text, self.last_audio

CONTEXT = SessionContext()
