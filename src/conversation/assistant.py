"""SightLine Assistant - Orchestrates Florence-2 Vision, iNSIGHTS Research Pipeline, and Speech.
Build With Bharat 3.0 Production Edition.
"""

import time
import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict, Any

from src.vision.florence import FlorenceVisionEngine
from src.conversation.context import CONTEXT
from src.speech.tts import text_to_speech
from src.speech.audio_manager import AudioQueue
from src.vision.scene_change import compute_hash
from src.config import CONFIG
from src.insights.pipeline import IntelligencePipeline

AUDIO_QUEUE = AudioQueue(max_size=CONFIG.MAX_QUEUE_SIZE)

class SightLineAssistant:
    """Orchestrates vision, context memory, iNSIGHTS research pipeline, and speech."""
    
    def __init__(self):
        self.vision = FlorenceVisionEngine()
        self.pipeline = IntelligencePipeline()
        self.audio_finish_time = 0.0
        
    def initialize(self):
        """Load vision model."""
        self.vision.load()
        
    def process_image(
        self,
        image,
        task: str,
        voice_name: str,
        force: bool = False,
        question: str = ""
    ) -> Tuple[str, Optional[str], str, Dict[str, Any]]:
        """Process an image through the SightLine Intelligence Pipeline.
        
        Returns:
            Tuple of:
            - spoken_response (str): Text formatted for voice/screen reader
            - audio_path (Optional[str]): Path to generated speech MP3
            - status_text (str): Short status message for the banner
            - intelligence_data (Dict[str, Any]): Structured evidence & metrics for Judge Mode
        """
        if self.vision.model is None:
            empty_ui = {
                "route": "LOCAL_VISION",
                "route_reason": "Model initializing",
                "entity": "System",
                "provider": "Local",
                "confidence": "0%",
                "sources_count": 0,
                "sources": [],
                "key_facts": [],
                "summary": "Model is loading into memory.",
                "latency": "0s"
            }
            return "Model is initializing, please wait...", None, "Model Loading...", empty_ui
            
        if not force and time.time() < getattr(self, "audio_finish_time", 0.0):
            last_text, last_audio = CONTEXT.get_last()
            last_res = CONTEXT.get_last_research()
            ui_data = last_res.to_dict() if last_res else {}
            return None, None, "Speaking...", ui_data
            
        if image is None:
            cached_frame = CONTEXT.get_last_frame()
            if cached_frame is not None:
                image = cached_frame

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif image is None:
            # Check if we have previous context for follow-up questions
            if question.strip() and (CONTEXT.active_entity or CONTEXT.last_text or CONTEXT.last_ocr):
                active_ent = CONTEXT.active_entity or (CONTEXT.last_ocr[:30] if CONTEXT.last_ocr else "Observed Scene")
                prev_facts = CONTEXT.get_recent_facts(active_ent)
                lang = "hi" if "Hindi" in voice_name else "en"
                res = self.pipeline.research(
                    query=question.strip(),
                    entity=active_ent,
                    visual_scene=CONTEXT.last_text,
                    ocr_text=CONTEXT.last_ocr,
                    previous_facts=prev_facts,
                    language=lang
                )
                res = self.pipeline.validate(res)
                CONTEXT.store_research(res)
                speech_text = self._handle_language_and_speech(res.answer, voice_name)
                audio_path = self._generate_audio(speech_text, voice_name)
                ui_data = self.pipeline.format_for_ui(res, self.pipeline.detect_intent(question))
                return speech_text, audio_path, f"Follow-up answered for {active_ent}", ui_data

            empty_ui = {"route": "NONE", "route_reason": "No image", "entity": "", "sources_count": 0, "sources": []}
            return "Please provide an image or webcam capture.", None, "No Image Provided", empty_ui

        img_hash = compute_hash(image)
        lang = "hi" if "Hindi" in voice_name else "en"
        
        # Debounce/Duplicate check if not forced
        if not force and CONTEXT.is_duplicate(img_hash, task) and task not in ("Ask Question", "Research", "Intelligence"):
            text, audio = CONTEXT.get_last()
            last_res = CONTEXT.get_last_research()
            ui_data = last_res.to_dict() if last_res else {}
            return text, audio, "Used cached result", ui_data

        t0 = time.time()
        
        # Map modes to operations
        if task == "Read Text":
            ocr_result = self.vision.read_text(image)
            CONTEXT.store_ocr(ocr_result)
            speech_text = self._handle_language_and_speech(ocr_result, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            ui_data = {
                "route": "LOCAL_VISION",
                "route_reason": "Direct text OCR extraction.",
                "entity": "Document / Text",
                "provider": "Florence-2 OCR",
                "confidence": "95%",
                "sources_count": 0,
                "sources": [],
                "key_facts": [ocr_result[:200]],
                "summary": ocr_result,
                "latency": f"{round(time.time() - t0, 2)}s"
            }
            return speech_text, audio_path, "Text Extracted", ui_data

        elif task == "Read Document":
            ocr_result = self.vision.read_text(image)
            CONTEXT.store_ocr(ocr_result)
            speech_text, ui_data, _ = self.pipeline.execute(
                query=question.strip() or "Analyze and summarize this document notice",
                image_or_scene="",
                ocr_text=ocr_result,
                context_memory=CONTEXT,
                explicit_mode="Read Document",
                language=lang
            )
            speech_text = self._handle_language_and_speech(speech_text, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            return speech_text, audio_path, "Document Intelligence Completed", ui_data

        elif task == "Quick Glance":
            scene_desc = self.vision.describe_scene(image, detailed=False)
            speech_text = self._handle_language_and_speech(scene_desc, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            ui_data = {
                "route": "LOCAL_VISION",
                "route_reason": "Fast visual glance requested.",
                "entity": "Scene",
                "provider": "Florence-2 (Caption)",
                "confidence": "94%",
                "sources_count": 0,
                "sources": [],
                "key_facts": [scene_desc],
                "summary": scene_desc,
                "latency": f"{round(time.time() - t0, 2)}s"
            }
            return speech_text, audio_path, "Quick Glance Complete", ui_data

        elif task == "Detailed Scene":
            scene_desc = self.vision.describe_scene(image, detailed=True)
            speech_text = self._handle_language_and_speech(scene_desc, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            ui_data = {
                "route": "LOCAL_VISION",
                "route_reason": "Detailed visual scene description.",
                "entity": "Scene",
                "provider": "Florence-2 (Detailed Caption)",
                "confidence": "95%",
                "sources_count": 0,
                "sources": [],
                "key_facts": [scene_desc],
                "summary": scene_desc,
                "latency": f"{round(time.time() - t0, 2)}s"
            }
            return speech_text, audio_path, "Detailed Scene Described", ui_data

        elif task == "Ask Question":
            if not question or not question.strip():
                speech_text = "Please enter a question to ask about this image."
                ui_data = {"route": "LOCAL_VISION", "route_reason": "Empty question", "sources_count": 0, "sources": []}
                return speech_text, None, "Waiting for question...", ui_data

            # Let router evaluate whether to answer locally or via iNSIGHTS
            local_desc = self.vision.describe_scene(image, detailed=False)
            ocr_text = self.vision.read_text(image)
            CONTEXT.store_ocr(ocr_text)

            decision = self.pipeline.detect_intent(question.strip(), detected_text=ocr_text, scene_description=local_desc)
            if decision.is_research:
                speech_text, ui_data, _ = self.pipeline.execute(
                    query=question.strip(),
                    image_or_scene=local_desc,
                    ocr_text=ocr_text,
                    context_memory=CONTEXT,
                    explicit_mode="Research",
                    language=lang
                )
            else:
                vqa_ans = self.vision.ask_question(image, question.strip())
                speech_text = vqa_ans
                ui_data = {
                    "route": "LOCAL_VISION",
                    "route_reason": decision.reason,
                    "entity": decision.extracted_entity or "Target Object",
                    "provider": "Florence-2 VQA",
                    "confidence": f"{int(decision.confidence * 100)}%",
                    "sources_count": 0,
                    "sources": [],
                    "key_facts": [vqa_ans],
                    "summary": f"Question: {question.strip()}\nAnswer: {vqa_ans}",
                    "latency": f"{round(time.time() - t0, 2)}s"
                }

            speech_text = self._handle_language_and_speech(speech_text, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            return speech_text, audio_path, "Question Answered", ui_data

        else:
            # Flagship Default: "Intelligence" Mode
            # Step 1: Perceive scene with Florence-2
            local_desc = self.vision.describe_scene(image, detailed=True)
            # Step 2: Read any visible text or brand labels with OCR
            ocr_text = self.vision.read_text(image)
            CONTEXT.store_ocr(ocr_text)

            # Step 3: Run full IntelligencePipeline
            effective_query = question.strip() if question.strip() else "What is this, how does it work, and what should I know?"
            speech_text, ui_data, decision = self.pipeline.execute(
                query=effective_query,
                image_or_scene=local_desc,
                ocr_text=ocr_text,
                context_memory=CONTEXT,
                explicit_mode="Intelligence" if not question.strip() else None,
                language=lang
            )

            speech_text = self._handle_language_and_speech(speech_text, voice_name)
            audio_path = self._generate_audio(speech_text, voice_name)
            CONTEXT.update(img_hash, task, speech_text, audio_path)
            status_msg = "iNSIGHTS Research Completed" if decision.is_research else "Visual Intelligence Processed"
            return speech_text, audio_path, status_msg, ui_data

    def _handle_language_and_speech(self, text: str, voice_name: str) -> str:
        """Handle language adaptation (Hindi translation fallback if needed)."""
        if "Hindi" in voice_name:
            # If already containing Devanagari characters, return as is
            if any('\u0900' <= char <= '\u097f' for char in text):
                return text

            translated = None
            try:
                from deep_translator import GoogleTranslator
                translated = GoogleTranslator(source='auto', target='hi').translate(text)
            except Exception:
                pass

            if not translated or "Error 500" in str(translated) or "Server Error" in str(translated):
                try:
                    from deep_translator import MyMemoryTranslator
                    translated = MyMemoryTranslator(source='en-US', target='hi-IN').translate(text)
                except Exception:
                    pass

            if translated and "Error 500" not in str(translated) and "Server Error" not in str(translated):
                return translated

        return text

    def _generate_audio(self, text: str, voice_name: str) -> Optional[str]:
        """Convert text to speech and track audio duration."""
        audio_path = text_to_speech(text, voice_name)
        if audio_path:
            try:
                from pydub import AudioSegment
                duration = AudioSegment.from_file(audio_path).duration_seconds
            except Exception:
                duration = len(text) / 14.0
            self.audio_finish_time = time.time() + duration
            AUDIO_QUEUE.enqueue(text, audio_path)
        return audio_path
