# Security, Privacy & Assistive Safety Architecture

## 1. Assistive Safety Disclaimers
SightLine is an artificial intelligence assistive prototype designed to empower blind and low-vision individuals with situational understanding.

> [!WARNING]
> **Essential Safety Notice:**
> SightLine is **NOT** a certified replacement for a white cane, guide dog, trained human caregiver, or mobility aid. Users must always exercise caution, situational awareness, and tactile confirmation when navigating physical spaces or crossing roadways.

### Healthcare & Medication Safeguards
- SightLine **never** claims to perform medical diagnosis or prescribe treatments.
- When pharmaceutical packaging, pills, or medicinal compounds (such as Paracetamol) are identified:
  - The pipeline automatically appends cautionary instructions:
    *"Please verify the medication label, expiry date, and dosage with a licensed doctor, pharmacist, or trusted individual before taking it."*
  - Responses highlight high-risk contraindications and liver toxicity risks associated with active ingredients.

---

## 2. Privacy-by-Design
Blind and low-vision users frequently point cameras at personal environments, identity documents, bills, and private spaces. SightLine implements rigorous privacy protocols:

1. **Zero Permanent Image Storage:**
   - Camera feeds and uploaded images are processed in-memory as ephemeral NumPy arrays or PIL Image objects.
   - Images are **never written to disk or logged** on the server.
2. **Ephemeral Audio Generation:**
   - Synthesized speech audio files are created in temporary OS directories (`tempfile`) and purged by the `AudioQueue` once dequeued or interrupted.
3. **No PII Transmission in Research Queries:**
   - Raw personal data (such as bank account numbers or home addresses detected via OCR) is stripped before research queries are dispatched.
   - DeepSearch queries focus strictly on generic product models, notice dates, or official manuals.

---

## 3. Credential & Environment Security
- **No Hardcoded Secrets:**
  - Zero API keys, passwords, or participant credentials are baked into source files.
  - Integration variables are loaded through Python's `os.getenv` via `src/config.py`.
- **Public & Service Role Isolation:**
  - Base44 Core InvokeLLM requests utilize public App ID headers (`X-App-Id: 6960af55d740f6d891a60e24`) and support standard Bearer token authorization (`INSIGHTS_API_KEY`) when provided.

---

## 4. Operational Resilience & Rate Limiting
- **Timeout Protection:** External network calls are strictly bound by `INSIGHTS_TIMEOUT` (default 15 seconds) to prevent frozen UI threads.
- **Graceful Fallback:** If iNSIGHTS encounters HTTP 429 (Rate Limit) or HTTP 500 (Outage), SightLine falls back to local Florence-2 visual descriptions without failing or crashing.
