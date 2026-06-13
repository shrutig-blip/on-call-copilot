"""
app.py - On-Call Copilot (Improved UI)
Run with: streamlit run app.py
"""

import streamlit as st
from agent import (
    recall_similar_incidents,
    generate_without_memory,
    generate_with_memory,
    save_resolution,
    list_all_memories,
)

st.set_page_config(
    page_title="On-Call Copilot",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Header */
.copilot-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}
.copilot-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin: 0;
}
.copilot-badge {
    background: #ef4444;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 99px;
    text-transform: uppercase;
    position: relative;
    top: -2px;
}
.copilot-sub {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* Comparison cards */
.response-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.5rem;
    min-height: 200px;
}
.response-card.memory {
    background: #f0fdf4;
    border-color: #86efac;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e2e8f0;
}
.card-label.no-mem { color: #94a3b8; border-color: #e2e8f0; }
.card-label.with-mem { color: #16a34a; border-color: #86efac; }

/* Section headers */
.section-tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 6px;
    margin-bottom: 0.75rem;
}
.section-tag.eng { background: #dbeafe; color: #1d4ed8; }
.section-tag.cust { background: #fef3c7; color: #b45309; }

/* Memory pill */
.memory-pill {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: #475569;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Incident description box */
.incident-box {
    background: #fff7ed;
    border-left: 3px solid #f97316;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.88rem;
    color: #374151;
    margin-bottom: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextArea label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #ef4444 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.6rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #dc2626 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.875rem;
    color: #64748b;
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    color: #0f172a !important;
    background: #f8fafc !important;
    border-bottom: 2px solid #ef4444 !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 500;
    font-size: 0.875rem;
}

/* Status indicators */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}
.status-dot.live { background: #ef4444; animation: pulse 1.5s infinite; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Metric row */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-chip {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.4rem 0.9rem;
    font-size: 0.8rem;
    color: #475569;
}
.metric-chip strong { color: #0f172a; }
</style>
""", unsafe_allow_html=True)

# ── DEMO INCIDENTS ───────────────────────────────────────────────────────────
DEMO_INCIDENTS = {
    "Pick a scenario...": "",
    "🔥 500 errors during flash sale traffic spike": (
        "Auth Service is returning HTTP 500 errors for ~12% of login requests. "
        "Logs show 'connection pool exhausted, timeout waiting for connection'. "
        "Traffic is currently 6x normal due to a flash sale promotion that started "
        "20 minutes ago."
    ),
    "🏢 Office Wi-Fi users getting 'too many attempts' errors": (
        "Multiple users from the same corporate office report 'Too many login "
        "attempts, try again later' even though it's their first login attempt "
        "today. Users on home networks are not affected."
    ),
    "🔐 2FA codes rejected as invalid for some users": (
        "Several users report that their two-factor authentication codes from "
        "Google Authenticator are being rejected as 'Invalid code', even though "
        "the codes are freshly generated and correct."
    ),
    "✏️ Custom incident (type your own)": "CUSTOM",
}

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚨 On-Call Copilot")
    st.markdown("<p style='color:#64748b;font-size:0.8rem;margin-bottom:1.5rem'>Incident response, powered by memory</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### New Incident")
    choice = st.selectbox("Choose a demo scenario", list(DEMO_INCIDENTS.keys()), label_visibility="collapsed")

    if choice == "✏️ Custom incident (type your own)":
        incident_description = st.text_area(
            "Describe the incident",
            height=160,
            placeholder="e.g. Users seeing 'session expired' errors immediately after logging in...",
        )
    elif DEMO_INCIDENTS[choice]:
        incident_description = DEMO_INCIDENTS[choice]
        st.markdown(f'<div class="incident-box">{incident_description}</div>', unsafe_allow_html=True)
    else:
        incident_description = ""
        st.markdown('<p style="color:#64748b;font-size:0.82rem">← Pick a scenario above to get started</p>', unsafe_allow_html=True)

    st.markdown("")
    analyze_clicked = st.button("⚡ Analyze Incident", type="primary", use_container_width=True)
    st.divider()

    st.markdown("""
    <p style="color:#475569;font-size:0.75rem;line-height:1.6">
    <strong style="color:#94a3b8">How it works</strong><br>
    Recalls similar past incidents → generates two responses for comparison → 
    learns from your resolution.
    </p>
    """, unsafe_allow_html=True)

# ── MAIN HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="copilot-header">
    <span style="font-size:1.5rem">🚨</span>
    <h1 class="copilot-title">On-Call Copilot</h1>
    <span class="copilot-badge">Live</span>
</div>
<p class="copilot-sub">Paste an incident → instantly see what a generic agent says vs. one with memory of every past postmortem.</p>
""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["⚡ Incident Analysis", "🧠 Memory Browser"])

with tab1:
    if not incident_description or choice == "Pick a scenario...":
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#94a3b8;">
            <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
            <div style="font-weight:600;color:#64748b;margin-bottom:0.5rem">No incident selected</div>
            <div style="font-size:0.875rem">Pick a demo scenario in the sidebar or write your own, then click <strong>Analyze Incident</strong>.</div>
        </div>
        """, unsafe_allow_html=True)

    elif analyze_clicked:
        # ── Recall memories ──────────────────────────────────────────────────
        with st.spinner("🔍 Searching memory bank for similar incidents..."):
            recalled = recall_similar_incidents(incident_description)
            recalled = recalled[:5]

        # Metric row
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-chip"><span class="status-dot live"></span><strong>Active</strong> &nbsp;incident in analysis</div>
            <div class="metric-chip">🧠 <strong>{len(recalled)}</strong> memories recalled</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Side-by-side comparison ──────────────────────────────────────────
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown('<div class="card-label no-mem">🤖 Without Memory — generic agent</div>', unsafe_allow_html=True)
            with st.spinner("Generating generic response..."):
                generic_response = generate_without_memory(incident_description)

            # Parse and display sections cleanly
            if "ENGINEER NOTES:" in generic_response and "CUSTOMER MESSAGE:" in generic_response:
                parts = generic_response.split("CUSTOMER MESSAGE:")
                eng_part = parts[0].replace("ENGINEER NOTES:", "").strip()
                cust_part = parts[1].strip()

                st.markdown('<span class="section-tag eng">🔧 Engineer Notes</span>', unsafe_allow_html=True)
                st.markdown(eng_part)
                st.markdown('<span class="section-tag cust">📢 Customer Message</span>', unsafe_allow_html=True)
                st.info(cust_part)
            else:
                st.markdown(generic_response)

        with col2:
            st.markdown('<div class="card-label with-mem">✅ With Hindsight Memory — pattern-aware agent</div>', unsafe_allow_html=True)
            with st.spinner("Generating memory-informed response..."):
                memory_response = generate_with_memory(incident_description, recalled)

            if "ENGINEER NOTES:" in memory_response and "CUSTOMER MESSAGE:" in memory_response:
                parts = memory_response.split("CUSTOMER MESSAGE:")
                eng_part = parts[0].replace("ENGINEER NOTES:", "").strip()
                cust_part = parts[1].strip()

                st.markdown('<span class="section-tag eng">🔧 Engineer Notes</span>', unsafe_allow_html=True)
                st.markdown(eng_part)
                st.markdown('<span class="section-tag cust">📢 Customer Message</span>', unsafe_allow_html=True)
                st.success(cust_part)
            else:
                st.markdown(memory_response)

        # ── Recalled memories ────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 🧠 Memories Recalled for This Incident")
        if recalled:
            st.caption(f"{len(recalled)} past incident(s) matched — these informed the memory-aware response above.")
            for i, m in enumerate(recalled):
                with st.expander(f"Memory {i+1} — {m.text[:90]}..."):
                    st.code(m.text, language=None)
        else:
            st.warning("No relevant past incidents found in memory. This is a new pattern — resolve it below to teach the agent.")

        # ── Save resolution ───────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 💾 Resolve & Teach the Agent")
        st.caption("Save the root cause and fix to memory. Next time a similar incident occurs, the agent will recall this postmortem.")

        resolution_summary = st.text_area(
            "Root cause and fix",
            height=110,
            placeholder="e.g. Root cause: connection pool set too low (10). Fix: increased to 50 and added monitoring. Customer message that worked: ...",
            label_visibility="collapsed",
        )
        save_col, _ = st.columns([1, 3])
        with save_col:
            if st.button("💾 Save to Memory", use_container_width=True):
                if resolution_summary.strip():
                    save_resolution(incident_description, resolution_summary)
                    st.success("✅ Saved! This incident is now part of the agent's memory.")
                else:
                    st.warning("Describe the resolution before saving.")

    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#94a3b8;">
            <div style="font-size:2.5rem;margin-bottom:1rem">⚡</div>
            <div style="font-weight:600;color:#64748b;margin-bottom:0.5rem">Ready to analyze</div>
            <div style="font-size:0.875rem">Click <strong>Analyze Incident</strong> in the sidebar to run the agent.</div>
        </div>
        """, unsafe_allow_html=True)

# ── MEMORY BROWSER TAB ───────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🧠 Auth Service Memory Bank")
    st.caption("Every past incident postmortem stored here. Grows as you save new resolutions.")

    refresh_col, _ = st.columns([1, 4])
    with refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    try:
        import re as _re
        memories = list_all_memories()
        # Handle both list responses and object responses
        if hasattr(memories, "items") and callable(memories.items):
            # it's a dict-like object
            items = list(memories.items())
        elif hasattr(memories, "items"):
            items = memories.items
        elif isinstance(memories, list):
            items = memories
        else:
            items = list(memories)

        st.markdown(f'<div class="metric-chip" style="display:inline-block;margin-bottom:1rem">🧠 <strong>{len(items)}</strong> total memories in bank</div>', unsafe_allow_html=True)

        for i, mem in enumerate(items):
            # Handle dict, object with attributes, or raw string
            if isinstance(mem, dict):
                text = mem.get("text") or mem.get("content") or mem.get("memory") or str(mem)
                mtype = mem.get("type") or mem.get("context") or "postmortem"
            else:
                text = getattr(mem, "text", None) or getattr(mem, "content", None) or str(mem)
                mtype = getattr(mem, "type", None) or getattr(mem, "context", "postmortem")

            # Clean up mtype if it's still a raw dict string
            if isinstance(mtype, str) and mtype.startswith("{"):
                mtype = "postmortem"

            # Extract INC number from text
            inc_label = ""
            if "INC-" in str(text):
                match = _re.search(r"INC-\d+", str(text))
                if match:
                    inc_label = f" · {match.group()}"

            preview = str(text)[:95].replace("\n", " ")
            with st.expander(f"[{str(mtype).upper()}{inc_label}]  {preview}..."):
                st.markdown(f"```\n{text}\n```")

    except Exception as e:
        st.error(f"Could not load memories: {e}")
        with st.expander("Debug info"):
            st.code(str(e))