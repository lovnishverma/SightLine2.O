# SightLine Intelligence — Hackathon Pitch Deck
**Build With Bharat 3.0 — Chitkara University, Himachal Pradesh**

---

### Slide 1: Title & Vision
**SightLine Intelligence: Empowering the Visually Impaired to Understand the Physical World**
- *Tagline:* Moving beyond visual perception to actionable real-world intelligence.
- *Paradigm:* $\text{SEE} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{RESEARCH} \longrightarrow \text{VERIFY} \longrightarrow \text{ACT}$
- *Event:* Build With Bharat 3.0 (Chitkara University)
- *Core Innovation:* Florence-2 Vision + Official iNSIGHTS DeepSearch Integration + Multilingual Indic Voice.

---

### Slide 2: The Core Problem
**Blind and low-vision individuals face an invisible barrier in physical environments.**
- Over 40 million individuals in India experience severe visual impairment.
- Everyday obstacles aren't just *"What is in front of me?"*, but:
  - *How do I operate this unfamiliar washing machine or microwave?*
  - *What does this circular or scholarship deadline on the college board say?*
  - *Is this medication safe to take, and what is the adult dosage?*
  - *What does this cryptic appliance error code mean?*
- Physical labels, controls, manuals, and notices remain completely inaccessible without sighted assistance.

---

### Slide 3: Why Existing Visual Assistants Fail
**Current visual AI stops at passive description.**
- **Existing Assistants (Seeing AI, Be My Eyes, generic LLMs):**
  $$\text{Camera} \longrightarrow \text{Object Classifier} \longrightarrow \text{"A washing machine"}$$
  *Result:* The user is left stranded without knowing how to turn it on or select a program.
- **SightLine Intelligence:**
  $$\text{Camera} \longrightarrow \text{Vision} \longrightarrow \text{Intent Router} \longrightarrow \text{iNSIGHTS Research} \longrightarrow \text{Evidence} \longrightarrow \text{Voice Action}$$
  *Result:* The user hears: *"This is a Bosch Series 6. Turn the dial to Super 15 and press Start for a quick wash."*

---

### Slide 4: The Mandatory iNSIGHTS Integration (Dedicated Slide)
**Deep, Production-Grade Integration with the Official iNSIGHTS Platform**
- **Platform Verified:** iNSIGHTS by Thore Network (`https://insights-ai.info/`, App ID `6960af55d740f6d891a60e24`).
- **Core Engine:** iNSIGHTS DeepSearch via `Core/InvokeLLM` integration.
- **Why It Matters:**
  - Powers real-time web retrieval of device manuals, health advisories, and document interpretations.
  - Enforces structured JSON schemas (`voice_answer`, `sources`, `key_facts`, `knowledge_cluster`).
  - Strict evidence-first verification: Every claim is cross-referenced with verified URLs and official documentation.
  - Transparent Judge Mode panel proves real-time external intelligence at runtime.

---

### Slide 5: Technical Architecture
**Modern, High-Performance, Modular Stack**
- **Perception:** Microsoft Florence-2-large-ft (0.7B parameters) + PaddleOCR with GPU/CPU acceleration.
- **Intelligence Router:** Deterministic classifier separating direct local perception (*"What color is this?"*) from research inquiries (*"How to use?"*).
- **Knowledge Representation:** Bounded Knowledge Clusters storing model numbers, controls, wash cycles, and safety warnings.
- **Performance Layer:** In-memory LRU/TTL Cache ($< 1\text{ms}$ hits) preventing redundant queries.
- **Multilingual Voice:** Deep Indic translation + Edge-TTS Neural Audio with native Hindi voices (`hi-IN-SwaraNeural`).
- **Safety First:** Medical caution disclaimers, zero permanent frame storage, ephemeral audio.

---

### Slide 6: Live Demo Walkthrough (3 Minutes)
1. **Local Perception:** User points camera $\rightarrow$ Florence-2 detects *"Bosch washing machine"*.
2. **Contextual Inquiry:** User asks: *"Tell me more about it."* $\rightarrow$ Router engages iNSIGHTS DeepSearch.
3. **Evidence Verification:** Judge Panel reveals verified sources (`media3.bosch-home.com`) and operating programs.
4. **Follow-Up Memory:** User asks: *"How do I run a quick wash?"* $\rightarrow$ Assistant leverages existing Knowledge Cluster without re-querying.
5. **Document Intelligence:** Scans a university scholarship notice $\rightarrow$ Extracts deadline (September 20) and required documents.
6. **Hyper-Local Hindi:** User asks: *"Isko Hindi mein samjhao"* $\rightarrow$ Natural Hindi speech output.

---

### Slide 7: Accessibility & User Experience
**Built with and for Visually Impaired Users**
- **High-Contrast Dark Theme:** Optimized for low-vision individuals with yellow focus indicators.
- **Touch Targets:** Large, tactile 68px minimum touch buttons.
- **Hands-Free Operation:** Keyboard shortcuts (`D` to describe, `R` for realtime, `P` for repeat, `Esc` to stop).
- **Audio Queue Management:** Thread-safe interruptible audio preventing auditory overload.
- **Screen Reader Compatibility:** ARIA assertive live status regions.

---

### Slide 8: Scalability & Real-World Impact
**Extending Beyond Prototypes to National Infrastructure**
- **Education & Campuses:** Reading circulars, notices, and exam timetables independently in colleges like Chitkara.
- **Public Transit & Services:** Railway timetables, government office forms, and metro station wayfinding.
- **Home Autonomy:** Operating smart and analog household appliances without sighted family members.
- **Retail & Groceries:** Reading ingredients, expiry dates, and preparation instructions.
- **Healthcare Caution:** Identifying medicine names and precautions with medical disclaimers.

---

### Slide 9: Summary & Competitive Differentiation
| Feature | Traditional Tools | SightLine Intelligence |
| :--- | :--- | :--- |
| **Vision Inference** | Basic Labeling | Florence-2 Multimodal Reasoning |
| **Web Research** | None / Hallucinated | Official iNSIGHTS DeepSearch |
| **Evidence & Sources** | Black box | Transparent Citations & Evidence Panel |
| **Document Understanding**| Raw OCR dump | Deadlines & Actionable Summaries |
| **Conversational Context**| Stateless | Bounded Knowledge Clusters & Memory |
| **Language Support** | English only | Native Hindi Neural Voice & Localization |
| **Accessibility UI** | Standard web | High-contrast, keyboard-driven, screen-reader ready |

**"SightLine turns passive sight into independent, verified action for Bharat."**
