"""Event listeners and interactive workflows for SightLine Intelligence.
Build With Bharat 3.0 Production Edition.
"""

import gradio as gr
from src.ui.components import status_html, render_judge_panel
from src.config import CONFIG

def wire_events(demo, components, assistant):
    c = components

    def handle_describe(webcam_img, upload_img, task, voice, question):
        from src.conversation.context import CONTEXT
        is_webcam = webcam_img is not None
        img = webcam_img if is_webcam else upload_img
        if img is None:
            img = CONTEXT.get_last_frame()
        
        # If no image is provided, allow follow-up questions if previous context exists
        if img is None and not question.strip():
            empty_panel = render_judge_panel({"route": "NONE", "route_reason": "Waiting for visual input", "sources_count": 0, "sources": []})
            return gr.update(), gr.update(), status_html("Please provide an image or webcam capture."), empty_panel

        import numpy as np
        import cv2
        # Un-mirror webcam feed if directly provided
        if is_webcam and isinstance(img, np.ndarray):
            img = cv2.flip(img, 1)

        text, audio, status, ui_data = assistant.process_image(
            image=img,
            task=task,
            voice_name=voice,
            force=True,
            question=question
        )

        panel_html = render_judge_panel(ui_data)
        return text or gr.update(), audio or gr.update(), status_html(status), panel_html

    # Main describe button and question box submission
    c["describe_btn"].click(
        handle_describe,
        inputs=[c["webcam"], c["upload"], c["task_radio"], c["voice_dropdown"], c["question_box"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"]]
    )

    c["question_box"].submit(
        handle_describe,
        inputs=[c["webcam"], c["upload"], c["task_radio"], c["voice_dropdown"], c["question_box"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"]]
    )

    # Realtime stream toggle
    def toggle_rt(is_active):
        new_state = not is_active
        btn_text = "⏸ Stop Realtime (R)" if new_state else "▶️ Start Realtime (R)"
        status_msg = "Realtime Active" if new_state else "Realtime Paused"
        return new_state, gr.update(value=btn_text), status_html(status_msg)

    c["realtime_btn"].click(
        toggle_rt,
        inputs=[c["rt_state"]],
        outputs=[c["rt_state"], c["realtime_btn"], c["status_bar"]]
    )

    # Realtime webcam stream handler
    def handle_rt_stream(image, task, voice, question, is_active):
        if not is_active:
            return gr.update(), gr.update(), status_html("Realtime Paused"), gr.update()
        if image is None:
            return gr.update(), gr.update(), status_html("Camera Active — Looking..."), gr.update()

        import numpy as np
        import cv2
        if isinstance(image, np.ndarray):
            image = cv2.flip(image, 1)

        from src.conversation.context import CONTEXT
        CONTEXT.store_frame(image)

        text, audio, status, ui_data = assistant.process_image(
            image=image,
            task=task,
            voice_name=voice,
            force=False,
            question=question
        )
        panel_html = render_judge_panel(ui_data) if ui_data else gr.update()
        return text or gr.update(), audio or gr.update(), status_html(status), panel_html

    c["webcam"].stream(
        handle_rt_stream,
        inputs=[c["webcam"], c["task_radio"], c["voice_dropdown"], c["question_box"], c["rt_state"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"]],
        stream_every=CONFIG.CAPTURE_INTERVAL
    )

    # Quick Intelligence Action Chips
    def trigger_quick_action(q_text, default_task, voice, webcam_img, upload_img, custom_voice=None):
        v = custom_voice or voice
        text, audio, status, panel = handle_describe(webcam_img, upload_img, default_task, v, q_text)
        return text, audio, status, panel, gr.update(value=q_text), (gr.update(value=v) if custom_voice else gr.update())

    c["chip_use"].click(
        lambda w, u, v: trigger_quick_action("How do I operate and use this?", "Intelligence", v, w, u),
        inputs=[c["webcam"], c["upload"], c["voice_dropdown"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"], c["question_box"], c["voice_dropdown"]]
    )

    c["chip_safety"].click(
        lambda w, u, v: trigger_quick_action("Is this safe to use? What safety precautions and warnings apply?", "Intelligence", v, w, u),
        inputs=[c["webcam"], c["upload"], c["voice_dropdown"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"], c["question_box"], c["voice_dropdown"]]
    )

    c["chip_manual"].click(
        lambda w, u, v: trigger_quick_action("Find the user manual, quick start guide, and program specifications", "Intelligence", v, w, u),
        inputs=[c["webcam"], c["upload"], c["voice_dropdown"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"], c["question_box"], c["voice_dropdown"]]
    )

    c["chip_hindi"].click(
        lambda w, u, v: trigger_quick_action("इसको हिंदी में समझाएं और उपयोग करने का तरीका बताएं", "Intelligence", v, w, u, custom_voice="Hindi - Swara"),
        inputs=[c["webcam"], c["upload"], c["voice_dropdown"]],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"], c["judge_panel"], c["question_box"], c["voice_dropdown"]]
    )

    # Repeat & Stop controls
    def repeat_audio():
        from src.conversation.context import CONTEXT
        last_text, last_audio = CONTEXT.get_last()
        return last_text or gr.update(), last_audio or gr.update(), status_html("Repeating last announcement")

    c["repeat_btn"].click(
        repeat_audio,
        inputs=[],
        outputs=[c["caption_box"], c["audio_player"], c["status_bar"]]
    )

    def stop_playback():
        from src.conversation.assistant import AUDIO_QUEUE
        AUDIO_QUEUE.clear()
        return None, status_html("Speech interrupted and audio queue cleared.")

    c["stop_btn"].click(
        stop_playback,
        inputs=[],
        outputs=[c["audio_player"], c["status_bar"]]
    )
