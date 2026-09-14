"""CSS stylesheet for SightLine Intelligence.
Built for high-contrast accessibility, large touch targets, and clear judge observability.
"""

CSS = """
/* Base Accessible Variables */
:root {
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-muted: #94a3b8;
    --border: #334155;
    --border-accent: #38bdf8;
    --radius: 12px;
    --focus-ring: #facc15;
}

/* High Contrast & Focus States */
.gr-button {
    min-height: 68px !important;
    font-size: 1.15em !important;
    border-radius: var(--radius) !important;
    font-weight: 800 !important;
    border: 3px solid transparent !important;
    transition: all 0.15s ease-in-out;
}

.gr-button:focus, .gr-button:hover {
    border: 3px solid var(--focus-ring) !important;
    outline: 2px solid var(--focus-ring) !important;
    transform: scale(1.01);
}

.gr-button-primary {
    background: #0284c7 !important;
    color: #ffffff !important;
    border: 3px solid #38bdf8 !important;
}

.gr-button-secondary {
    background: #1e293b !important;
    color: #f8fafc !important;
    border: 2px solid #475569 !important;
}

/* Accessible Audio Player */
.gr-audio {
    border-radius: var(--radius) !important;
    border: 2px solid var(--border) !important;
}

/* Status Banner */
#sightline-status {
    background: #020617;
    color: #22c55e;
    padding: 16px 20px;
    border-radius: var(--radius);
    font-size: 1.3em;
    font-weight: 800;
    text-align: center;
    border: 3px solid #22c55e;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25);
    margin-bottom: 12px;
}

/* Dedicated Judge Mode & Evidence Panel */
.judge-panel {
    background: #0f172a;
    border: 2px solid #38bdf8;
    border-radius: var(--radius);
    padding: 18px;
    margin-top: 14px;
    box-shadow: 0 4px 16px rgba(56, 189, 248, 0.15);
}

.judge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #334155;
    padding-bottom: 12px;
    margin-bottom: 14px;
}

.badge-research {
    background: #0369a1;
    color: #38bdf8;
    padding: 6px 12px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 0.9em;
    border: 1px solid #38bdf8;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-local {
    background: #064e3b;
    color: #34d399;
    padding: 6px 12px;
    border-radius: 9999px;
    font-weight: 800;
    font-size: 0.9em;
    border: 1px solid #34d399;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
    margin-bottom: 14px;
}

.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
}

.metric-label {
    font-size: 0.75em;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.metric-val {
    font-size: 1.25em;
    font-weight: 800;
    color: #f8fafc;
    margin-top: 4px;
}

.source-item {
    background: #1e293b;
    border-left: 4px solid #38bdf8;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

.source-title {
    font-weight: 700;
    color: #f8fafc;
}

.source-url {
    color: #38bdf8;
    font-size: 0.85em;
    text-decoration: underline;
    word-break: break-all;
}

/* Screen Reader Only Utility */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}
"""
