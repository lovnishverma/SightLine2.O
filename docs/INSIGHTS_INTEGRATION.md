# Official iNSIGHTS Integration Guide

## 1. Why iNSIGHTS?
Most visual assistive applications stop at **perception**: they can say *"A washing machine"* or *"A printed piece of paper"*. For a visually impaired individual, this is incomplete. They need to know:
- *"How do I start a quick wash?"*
- *"Which dial controls the program?"*
- *"Is this medicine safe for fever, and what is the adult dose?"*
- *"What is the deadline on this scholarship notice?"*

**iNSIGHTS** (`https://insights-ai.info/`) bridges the gap between raw sight and actionable intelligence:
$$\text{SightLine Florence-2 (Vision)} + \text{iNSIGHTS DeepSearch (Knowledge)} = \text{Independent Living}$$

---

## 2. Legitimacy & Inspection Findings
Following our live inspection of the official iNSIGHTS platform (`https://insights-ai.info/`), we identified its production architecture:
- **Platform Base:** Base44 AI Operating System by Thore Network
- **Application ID:** `6960af55d740f6d891a60e24`
- **Flagship Intelligence Engine:** DeepSearch (`https://insights-ai.info/DeepSearch`)
- **API Endpoint:** 
  `https://insights-ai.info/api/apps/6960af55d740f6d891a60e24/integration-endpoints/Core/InvokeLLM`

### Live API Verification
We executed real requests against this live endpoint with structured JSON schemas and internet context enabled. The endpoint responded with HTTP 200 and verified citations:
```json
{
  "voice_answer": "On a Bosch washing machine, the quick wash is usually labeled SuperQuick 15 or 30. It is designed for small loads of up to 2 kilograms...",
  "sources": [
    {
      "title": "Bosch Washing Machine Buying Guide",
      "url": "https://www.bosch-home.com/sa/en/experience-bosch/buying-guide/washing-machine-buying-guide"
    },
    {
      "title": "Overview of programmes",
      "url": "https://media3.bosch-home.com/Documents/9000941229_B.pdf"
    }
  ],
  "key_facts": [
    "Identified recent model: Bosch Series 6 Front Loader",
    "Super 15/30 quick wash cycle for light soiled loads",
    "EcoSilence Drive brushless motor"
  ]
}
```

---

## 3. Integration Architecture

### Clean Provider Abstraction (`src/insights/providers/base.py`)
```python
class ResearchProvider(ABC):
    @abstractmethod
    def research(self, query: str, entity: str = "", visual_scene: str = "", ocr_text: str = "", previous_facts: list = None, language: str = "en") -> ResearchResult:
        pass

    @abstractmethod
    def analyze_document(self, ocr_text: str, document_type: str = "general", language: str = "en") -> ResearchResult:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Source]:
        pass

    @abstractmethod
    def create_knowledge_context(self, entity: str, facts: List[str], attributes: dict = None) -> KnowledgeCluster:
        pass
```

### Provider Implementations
1. **`InsightsLiveProvider` (`src/insights/providers/live.py`)**:
   - Directly calls the official `InvokeLLM` endpoint.
   - Enforces `add_context_from_internet: True` for web knowledge.
   - Attaches `X-App-Id: 6960af55d740f6d891a60e24`.
   - Attaches optional `Authorization: Bearer <token>` if `INSIGHTS_API_KEY` is provided.
   - Implements exponential backoff retry (up to 2 retries) with timeouts.
2. **`MockResearchProvider` (`src/insights/providers/mock.py`)**:
   - Zero-dependency, offline provider for test suites, air-gapped evaluation, and fallback.
   - Contains high-fidelity models for appliances (Bosch Series 6), medicines (Paracetamol), documents (Merit Scholarship Notice), and general devices.

---

## 4. Request & Response Payload Specification

### Request Payload sent to iNSIGHTS:
```json
{
  "model": "gemini_3_flash",
  "add_context_from_internet": true,
  "prompt": "You are the iNSIGHTS DeepSearch engine powering SightLine...\nUSER QUERY: 'How do I use quick wash?'\nDETECTED ENTITY: 'Bosch Washing Machine'...",
  "response_json_schema": {
    "type": "object",
    "properties": {
      "voice_answer": {"type": "string"},
      "executive_summary": {"type": "string"},
      "key_facts": {"type": "array", "items": {"type": "string"}},
      "sources": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "url": {"type": "string"},
            "source_type": {"type": "string"},
            "snippet": {"type": "string"}
          },
          "required": ["title", "url"]
        }
      },
      "confidence_score": {"type": "number"}
    },
    "required": ["voice_answer", "key_facts", "sources", "confidence_score"]
  }
}
```

---

## 5. Performance, Caching & Resilience

### LRU & TTL Caching (`src/insights/cache.py`)
- Keyed on `hash(normalized_query, entity, ocr_snippet, language)`.
- Default TTL: 1800 seconds (30 minutes).
- Default capacity: 100 entries with LRU eviction.
- Cache hits resolve in `< 1ms`, eliminating unnecessary network roundtrips.

### Graceful Fallback Guarantee
If the network is interrupted or iNSIGHTS is temporarily unreachable:
1. The pipeline catches `InsightsError`.
2. SightLine **does not crash**.
3. It politely announces: *"Research is temporarily unavailable. I can still describe what I see."*
4. Provides full local Florence-2 scene description or OCR text immediately.

---

## 6. Switching Modes & Environment Variables
In `.env`:
```bash
# To run against the official live iNSIGHTS platform:
INSIGHTS_ENABLED=true
INSIGHTS_PROVIDER=live

# To run in offline/mock mode:
INSIGHTS_PROVIDER=mock
```
