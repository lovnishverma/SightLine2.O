"""Accessible UI components with dedicated Judge Mode & Evidence Viewer for SightLine Intelligence.
Build With Bharat 3.0 Production Edition.
"""

import gradio as gr
from typing import Dict, Any
from src.ui.styles import CSS
from src.config import CONFIG

def status_html(msg: str) -> str:
    """Wrap a status message in the styled high-contrast status-bar div."""
    return f'<div id="sightline-status" role="status" aria-live="assertive">{msg}</div>'

def render_judge_panel(data: Dict[str, Any] = None) -> str:
    """Render the dedicated iNSIGHTS Intelligence Judge Panel."""
    if not data:
        data = {
            "route": "LOCAL_VISION",
            "route_reason": "Waiting for visual input...",
            "entity": "None",
            "provider": "Local Vision Engine",
            "confidence": "95%",
            "sources_count": 0,
            "sources": [],
            "key_facts": [],
            "latency": "0.0s",
            "summary": "Ready to perceive environment."
        }

    is_research = data.get("route") == "INSIGHTS_RESEARCH"
    status_badge = (
        '<span class="badge-research">● iNSIGHTS DeepSearch Active</span>'
        if is_research
        else '<span class="badge-local">● Local Vision Engine</span>'
    )

    entity = data.get("entity", "Identified Object")
    reason = data.get("route_reason", "Perception query")
    confidence = data.get("confidence", "95%")
    sources_cnt = data.get("sources_count", 0)
    latency = data.get("latency", "0.0s")
    facts = data.get("key_facts", [])

    facts_html = ""
    if facts:
        facts_items = "".join(f"<li style='margin-bottom: 4px;'>{f}</li>" for f in facts[:4])
        facts_html = f"""
        <div style="margin-top: 10px; background: #1e293b; padding: 10px; border-radius: 8px;">
            <strong style="color: #38bdf8; font-size: 0.9em; text-transform: uppercase;">Verified Knowledge Context:</strong>
            <ul style="margin: 6px 0 0 18px; padding: 0; color: #f8fafc; font-size: 0.95em;">
                {facts_html}
            </ul>
        </div>
        """

    sources_html = ""
    sources = data.get("sources", [])
    if sources:
        sources_rows = ""
        for s in sources:
            title = s.get("title", "Reference")
            url = s.get("url", "#")
            stype = s.get("type", "Official")
            link = f'<a href="{url}" target="_blank" class="source-url">{url}</a>' if url.startswith("http") else '<span style="color: #94a3b8;">Physical OCR Scan</span>'
            sources_rows += f"""
            <div class="source-item">
                <div style="display: flex; justify-content: space-between;">
                    <span class="source-title">{title}</span>
                    <span style="font-size: 0.8em; color: #38bdf8; background: #0f172a; padding: 2px 6px; border-radius: 4px;">{stype}</span>
                </div>
                <div>{link}</div>
            </div>
            """
        sources_html = f"""
        <div style="margin-top: 12px;">
            <strong style="color: #38bdf8; font-size: 0.9em; text-transform: uppercase;">Verified Sources & Citations:</strong>
            <div style="margin-top: 6px;">
                {sources_rows}
            </div>
        </div>
        """

    return f"""
    <div class="judge-panel">
        <div class="judge-header">
            <div>
                <span style="font-weight: 800; font-size: 1.1em; color: #f8fafc; letter-spacing: 0.05em;">iNSIGHTS INTELLIGENCE</span>
                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 2px;">Chitkara University Build With Bharat 3.0</div>
            </div>
            <div>{status_badge}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Detected Entity</div>
                <div class="metric-val">{entity}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Confidence</div>
                <div class="metric-val">{confidence}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sources Found</div>
                <div class="metric-val">{sources_cnt}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Route Latency</div>
                <div class="metric-val">{latency}</div>
            </div>
        </div>

        <div style="font-size: 0.9em; color: #cbd5e1; margin-bottom: 8px;">
            <strong style="color: #94a3b8;">Intelligence Routing Rationale:</strong> {reason}
        </div>

        {facts_html}
        {sources_html}
    </div>
    """

def build_ui(assistant) -> gr.Blocks:
    """Construct the complete Gradio interface for SightLine Intelligence."""
    auto_start_js = """
    function() {
        setInterval(function() {
            let clickTarget = function(btn) {
                let text = (btn.textContent || btn.innerText || '').toLowerCase().trim();
                if (text === 'click to access webcam' || text === 'record') {
                    btn.click();
                }
            };
            document.querySelectorAll('*').forEach(function(el) {
                if (el.shadowRoot) {
                    el.shadowRoot.querySelectorAll('button').forEach(clickTarget);
                }
            });
            document.querySelectorAll('button').forEach(clickTarget);
        }, 1000);
    }
    """

    with gr.Blocks(title=f"{CONFIG.APP_NAME} v{CONFIG.APP_VERSION}", js=auto_start_js, css=CSS) as demo:
        gr.HTML('<div class="sr-only" aria-live="assertive" id="aria-live-region" role="status"></div>')
        
        status_bar = gr.HTML(status_html("Ready — Select mode or press D to describe"))

        gr.HTML(f"""
        <div class="sightline-header" style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 10px 0 16px 0; border-bottom: 2px solid #334155; padding-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="color: #38bdf8;">
                    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
                <div>
                    <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; display: inline-block; color: #f8fafc;">{CONFIG.APP_NAME}</h1>
                    <span style="background: #0284c7; color: #ffffff; padding: 2px 8px; border-radius: 6px; font-size: 0.8em; font-weight: 700; margin-left: 8px;">v{CONFIG.APP_VERSION}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.9em; font-weight: 700; color: #38bdf8; background: #0f172a; padding: 6px 12px; border-radius: 8px; border: 1px solid #38bdf8;">
                    Build With Bharat 3.0 • Chitkara University
                </span>
            </div>
        </div>
        """)
        
        rt_state = gr.State(True)

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    describe_btn = gr.Button("🔍 Describe / Research (D)", variant="primary", elem_id="btn-describe")
                    realtime_btn = gr.Button("⏸ Stop Realtime (R)", variant="secondary", elem_id="btn-realtime")
                
                with gr.Row():
                    task_radio = gr.Radio(
                        choices=[
                            "Intelligence",
                            "Quick Glance",
                            "Detailed Scene",
                            "Research",
                            "Read Document",
                            "Ask Question"
                        ],
                        value="Intelligence",
                        label="Mode (Accessibility & Intelligence Control)"
                    )
            
            with gr.Column(scale=1):
                with gr.Row():
                    repeat_btn = gr.Button("🔊 Repeat (P)", elem_id="btn-repeat")
                    stop_btn = gr.Button("⏹ Stop (Esc)", elem_id="btn-stop")
                
                voice_dropdown = gr.Dropdown(
                    choices=["English (US) - Aria", "Hindi - Swara"],
                    value="English (US) - Aria",
                    label="Spoken Output Voice"
                )

        question_box = gr.Textbox(
            label="Inquire / Ask a Question",
            placeholder="e.g. 'How do I operate this?', 'What is the scholarship deadline?', 'Where are my keys?'",
            lines=1
        )

        # 1-Click Follow-Up Action Chips for quick demonstrations
        with gr.Row():
            gr.Markdown("**Quick Intelligence Inquiries:**", elem_classes=["text-muted"])
            chip_use = gr.Button("⚙️ How to Use?", size="sm")
            chip_safety = gr.Button("🛡️ Is this Safe?", size="sm")
            chip_manual = gr.Button("📖 Find Manual", size="sm")
            chip_hindi = gr.Button("🇮🇳 Explain in Hindi", size="sm")

        with gr.Row():
            with gr.Column(scale=1):
                webcam = gr.Image(label="Live Camera Feed", type="numpy", sources=["webcam"], streaming=True)
                with gr.Accordion("Upload Image / Document", open=False):
                    upload = gr.Image(label="Upload Image File", type="numpy", sources=["upload"])

            with gr.Column(scale=1):
                caption_box = gr.Textbox(
                    label="Synthesized Auditory Description",
                    lines=8,
                    interactive=False
                )
                audio_player = gr.Audio(label="Spoken Audio Output", type="filepath", autoplay=True)

        # Dedicated Judge Mode Panel
        judge_panel = gr.HTML(render_judge_panel())

        components = {
            "webcam": webcam,
            "upload": upload,
            "task_radio": task_radio,
            "voice_dropdown": voice_dropdown,
            "question_box": question_box,
            "describe_btn": describe_btn,
            "realtime_btn": realtime_btn,
            "caption_box": caption_box,
            "audio_player": audio_player,
            "status_bar": status_bar,
            "judge_panel": judge_panel,
            "rt_state": rt_state,
            "repeat_btn": repeat_btn,
            "stop_btn": stop_btn,
            "chip_use": chip_use,
            "chip_safety": chip_safety,
            "chip_manual": chip_manual,
            "chip_hindi": chip_hindi,
        }
        
        from src.ui.events import wire_events
        wire_events(demo, components, assistant)
        
        return demo
