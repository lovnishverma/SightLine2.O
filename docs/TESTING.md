# Testing & Verification Guide

## 1. Overview
The SightLine Intelligence testing suite ensures that intelligence routing, bounded caching, provider integrations, document extraction, and error fallbacks execute deterministically across all environments without requiring active network connectivity for standard CI runs.

---

## 2. Running Automated Unit Tests
To run the complete test suite:
```powershell
pytest tests/ -v
```

### Test Coverage Highlights:
- `tests/test_router.py`:
  - Validates that direct sensory queries (*"What color is this shirt?"*, *"Is the traffic light red?"*, *"Where are my keys?"*) route to `LOCAL_VISION`.
  - Validates that contextual queries (*"How do I operate this?"*, *"Find the manual"*, *"What does this notice mean?"*) route to `INSIGHTS_RESEARCH`.
  - Validates Hindi research queries (*"Isko kaise use kare?"*).
  - Validates explicit UI mode overrides.
- `tests/test_cache.py`:
  - Validates deterministic hash generation across query, entity, and OCR text.
  - Validates hit/miss transitions and TTL expiry.
  - Validates LRU eviction when cache capacity is exceeded.
  - Validates metrics calculations (`hit_rate`, `hits`, `misses`, `evictions`).
- `tests/test_models.py`:
  - Validates serialization of `Source`, `EvidenceChunk`, `KnowledgeCluster`, `RouteDecision`, and `ResearchResult`.
  - Validates the `is_reliable` heuristic.
- `tests/test_providers.py`:
  - Validates `MockResearchProvider` appliance, medicine, and document research flows.
  - Validates Hindi output containing native Devanagari characters.
  - Validates `InsightsLiveProvider` error translation for timeouts, HTTP 401, HTTP 429, and HTTP 500.
- `tests/test_pipeline.py`:
  - Validates end-to-end execution of `IntelligencePipeline`.
  - Validates citation symbol sanitization from spoken answers.
  - Validates guaranteed fallback when external research services are offline.
- `tests/test_document.py`:
  - Validates extraction of deadlines, required documents, and action steps from scanned university notices.

---

## 3. Testing the Live iNSIGHTS Provider
To verify live connectivity against the official iNSIGHTS Core InvokeLLM endpoint:
```powershell
python -c "from src.insights.providers.live import InsightsLiveProvider; p = InsightsLiveProvider(); res = p.research('What is the quick wash program on a Bosch washing machine?', entity='Bosch'); print('Status: Success | Sources:', len(res.sources), '| Answer:', res.answer[:120])"
```

Expected output:
```text
Status: Success | Sources: 2 | Answer: On a Bosch washing machine, the quick wash is usually labeled SuperQuick 15 or 30...
```

---

## 4. Manual UI Verification
1. Run `python app.py`.
2. Navigate to `http://localhost:7860`.
3. Upload a sample image or test with your webcam.
4. Click **⚙️ How to Use?** and verify that the Judge Mode panel displays:
   - `● iNSIGHTS DeepSearch Active`
   - Verified Sources with URLs
   - Verified Knowledge Context bullet points.
5. Click **🇮🇳 Explain in Hindi** and verify that spoken audio is generated via Indic neural TTS (`hi-IN-SwaraNeural`).
