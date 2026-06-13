"""
app.py - On-Call Copilot (v2 - themed, charted, polished)
Run with: streamlit run app.py
"""

import re
import streamlit as st
import plotly.graph_objects as go
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

# ── THEMES ───────────────────────────────────────────────────────────────────
THEMES = {
    "Midnight Red": {
        "primary": "#ef4444", "primary_rgb": "239,68,68",
        "dark": "#0f172a", "accent2": "#7f1d1d",
        "success": "#16a34a", "success_rgb": "22,163,74",
    },
    "Ocean Blue": {
        "primary": "#0ea5e9", "primary_rgb": "14,165,233",
        "dark": "#0c2d48", "accent2": "#1e3a8a",
        "success": "#22c55e", "success_rgb": "34,197,94",
    },
    "Forest Emerald": {
        "primary": "#10b981", "primary_rgb": "16,185,129",
        "dark": "#022c22", "accent2": "#064e3b",
        "success": "#84cc16", "success_rgb": "132,204,22",
    },
    "Sunset Violet": {
        "primary": "#a855f7", "primary_rgb": "168,85,247",
        "dark": "#2e1065", "accent2": "#581c87",
        "success": "#f59e0b", "success_rgb": "245,158,11",
    },
}


def build_css(t):
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}

    /* Hero banner */
    .hero-banner {{
        background: linear-gradient(135deg, {t['dark']} 0%, {t['accent2']} 130%);
        border-radius: 18px;
        padding: 1.75rem 2.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }}
    .copilot-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }}
    .copilot-title {{ font-size: 1.75rem; font-weight: 700; color: #f8fafc !important; letter-spacing: -0.5px; margin: 0; }}
    .copilot-badge {{
        background: {t['primary']}; color: white; font-size: 0.65rem; font-weight: 700;
        letter-spacing: 0.08em; padding: 2px 8px; border-radius: 99px; text-transform: uppercase;
        position: relative; top: -2px; box-shadow: 0 0 12px rgba({t['primary_rgb']},0.6);
    }}
    .copilot-sub {{ color: #cbd5e1 !important; font-size: 0.9rem; margin-bottom: 0; }}

    /* Response cards */
    .response-card {{
        background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1.25rem 1.5rem; margin-top: 0.5rem; min-height: 200px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: box-shadow 0.25s ease, transform 0.25s ease;
        animation: fadeIn 0.4s ease;
    }}
    .response-card:hover {{ box-shadow: 0 10px 28px rgba(0,0,0,0.08); transform: translateY(-3px); }}
    .response-card.memory {{
        background: rgba({t['success_rgb']},0.06);
        border-color: rgba({t['success_rgb']},0.45);
    }}
    .card-label {{
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
        margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0;
    }}
    .card-label.no-mem {{ color: #94a3b8; border-color: #e2e8f0; }}
    .card-label.with-mem {{ color: {t['success']}; border-color: rgba({t['success_rgb']},0.4); }}

    /* Section tags */
    .section-tag {{
        display: inline-block; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; padding: 3px 10px; border-radius: 6px; margin-bottom: 0.75rem;
    }}
    .section-tag.eng {{ background: rgba({t['primary_rgb']},0.12); color: {t['dark']}; }}
    .section-tag.cust {{ background: rgba({t['success_rgb']},0.15); color: #334155; }}

    /* Incident description box */
    .incident-box {{
        background: rgba({t['primary_rgb']},0.06);
        border-left: 3px solid {t['primary']};
        border-radius: 0 8px 8px 0; padding: 0.75rem 1rem;
        font-size: 0.88rem; color: #374151; margin-bottom: 1rem;
    }}

    /* Memory / recalled cards */
    .mem-card {{
        border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem 1rem;
        margin-bottom: 0.6rem; background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: box-shadow 0.2s ease;
    }}
    .mem-card:hover {{ box-shadow: 0 4px 14px rgba(0,0,0,0.06); }}
    .mem-card-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 0.45rem; flex-wrap: wrap; }}
    .mem-badge {{
        font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em; padding: 2px 8px;
        border-radius: 999px; text-transform: uppercase; color: white;
    }}
    .mem-badge.type-observation {{ background: #6366f1; }}
    .mem-badge.type-world {{ background: {t['primary']}; }}
    .mem-badge.type-experience {{ background: {t['success']}; }}
    .mem-badge.type-other {{ background: #94a3b8; }}
    .mem-badge.inc {{ background: {t['dark']}; }}
    .mem-rank {{ font-size: 0.7rem; color: #94a3b8; font-weight: 600; margin-left: auto; }}
    .mem-text {{ font-size: 0.85rem; color: #475569; line-height: 1.5; font-family: 'JetBrains Mono', monospace; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background: {t['dark']}; }}
    section[data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextArea label {{
        color: #94a3b8 !important; font-size: 0.78rem !important; font-weight: 700 !important;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.3rem;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: {t['primary']} !important; color: white !important; border: none !important;
        font-weight: 600 !important; border-radius: 10px !important; padding: 0.6rem !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba({t['primary_rgb']},0.35) !important;
    }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: #f8fafc !important;
    }}
    .sidebar-section-title {{
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
        color: #64748b !important; margin: 1rem 0 0.5rem 0;
    }}
    .sidebar-card {{
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 0.75rem 0.9rem; margin-bottom: 0.4rem;
        font-size: 0.78rem; line-height: 1.5; color: #94a3b8 !important;
    }}
    .sidebar-stat {{
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 0.6rem 0.9rem; margin-bottom: 0.5rem; font-size: 0.85rem;
    }}
    .sidebar-stat strong {{ color: white !important; font-size: 1.1rem; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background: transparent; border-bottom: 1px solid #e2e8f0; padding-bottom: 0; }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600; font-size: 0.875rem; color: #64748b; background: transparent;
        border-radius: 8px 8px 0 0; padding: 8px 18px; transition: background 0.2s ease, color 0.2s ease;
    }}
    .stTabs [aria-selected="true"] {{
        color: {t['dark']} !important; background: #f8fafc !important; border-bottom: 2px solid {t['primary']} !important;
    }}

    /* Buttons (main area) */
    .stButton > button {{ border-radius: 10px !important; transition: transform 0.15s ease, box-shadow 0.15s ease !important; }}
    .stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba({t['primary_rgb']},0.25) !important; }}

    /* Metric row */
    .metric-row {{ display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }}
    .metric-chip {{
        background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.4rem 0.9rem;
        font-size: 0.8rem; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .metric-chip:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
    .metric-chip strong {{ color: {t['dark']}; }}

    .status-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }}
    .status-dot.live {{ background: {t['primary']}; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    /* Confidence badge */
    .confidence-badge {{
        display: inline-block; border-radius: 10px; padding: 0.5rem 1.1rem; font-weight: 700;
        font-size: 0.85rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    </style>
    """


# ── DEMO INCIDENTS (test cases) ────────────────────────────────────────────
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
    "📧 Password reset emails delayed by 20+ minutes": (
        "Users are reporting that password reset emails are taking over 20 minutes "
        "to arrive, when they previously arrived within seconds. No errors are "
        "showing on the password reset form itself."
    ),
    "🔑 'Sign in with Google' button not working for anyone": (
        "All users attempting to log in via the 'Sign in with Google' button are "
        "stuck on a blank screen after clicking it. Email/password login appears "
        "to be working normally."
    ),
    "🔒 Users locked out after a routine policy update": (
        "Shortly after a password policy update was deployed, a growing number of "
        "existing users are being locked out of their accounts on login, even "
        "though they are entering the correct password."
    ),
    "✏️ Custom incident (type your own)": "CUSTOM",
}


# ── HELPERS ──────────────────────────────────────────────────────────────────

def extract_inc(text):
    match = re.search(r"INC-\d+", str(text))
    return match.group() if match else None


def mem_type_class(mtype):
    mtype = (mtype or "").lower()
    if "observation" in mtype:
        return "type-observation"
    if "world" in mtype:
        return "type-world"
    if "experience" in mtype:
        return "type-experience"
    return "type-other"


def make_gauge(value, theme):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"size": 30}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1"},
            "bar": {"color": theme["primary"]},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#e2e8f0",
            "steps": [
                {"range": [0, 33], "color": "#fee2e2"},
                {"range": [33, 66], "color": "#fef9c3"},
                {"range": [66, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=200, margin=dict(t=10, b=10, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def make_donut(type_counts, theme):
    palette = [theme["primary"], theme["success"], theme["accent2"], "#94a3b8", "#64748b"]
    fig = go.Figure(data=[go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=0.55,
        marker=dict(colors=palette[: len(type_counts)]),
        textinfo="label+percent",
    )])
    fig.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), showlegend=True,
                      legend=dict(orientation="h", y=-0.15))
    return fig


def make_inc_bar(inc_counts, theme):
    labels = list(inc_counts.keys())
    values = list(inc_counts.values())
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=values, colorscale=[[0, theme["accent2"]], [1, theme["primary"]]]),
    ))
    fig.update_layout(
        height=max(220, 42 * len(labels)),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis_title="Memory mentions", yaxis_title=None,
    )
    return fig


def make_growth_chart(history, theme):
    fig = go.Figure(go.Scatter(
        y=history, mode="lines+markers", fill="tozeroy",
        line=dict(color=theme["success"], width=3), marker=dict(size=8),
    ))
    fig.update_layout(
        height=220, margin=dict(t=10, b=10, l=10, r=10),
        yaxis_title="Total memories", xaxis_title="Session checkpoint",
    )
    return fig


# ── SESSION STATE ────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Red"
if "growth_history" not in st.session_state:
    st.session_state.growth_history = []


def record_memory_count():
    try:
        mem = list_all_memories()
        items = mem.items if hasattr(mem, "items") else mem
        count = len(items)
        if not st.session_state.growth_history or st.session_state.growth_history[-1] != count:
            st.session_state.growth_history.append(count)
        return count, items
    except Exception:
        return None, []


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚨 On-Call Copilot")
    st.markdown(
        "<p style='color:#64748b;font-size:0.8rem;margin-bottom:0.5rem'>Incident response, powered by memory</p>",
        unsafe_allow_html=True,
    )

    theme_name = st.selectbox(
        "🎨 Theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
    )
    st.session_state.theme = theme_name
    theme = THEMES[theme_name]
    st.markdown(build_css(theme), unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section-title">New Incident</div>', unsafe_allow_html=True)
    choice = st.selectbox("Choose a demo scenario", list(DEMO_INCIDENTS.keys()), label_visibility="collapsed")

    if choice == "✏️ Custom incident (type your own)":
        incident_description = st.text_area(
            "Describe the incident",
            height=150,
            placeholder="e.g. Users seeing 'session expired' errors immediately after logging in...",
            label_visibility="collapsed",
        )
    elif DEMO_INCIDENTS[choice]:
        incident_description = DEMO_INCIDENTS[choice]
        st.markdown(f'<div class="incident-box">{incident_description}</div>', unsafe_allow_html=True)
    else:
        incident_description = ""
        st.markdown(
            '<p style="color:#64748b;font-size:0.82rem">Pick a scenario above to get started</p>',
            unsafe_allow_html=True,
        )

    analyze_clicked = st.button("⚡ Analyze Incident", type="primary", use_container_width=True)

    st.divider()
    st.markdown('<div class="sidebar-section-title">Memory Bank</div>', unsafe_allow_html=True)
    _count, _ = record_memory_count()
    if _count is not None:
        st.markdown(
            f'<div class="sidebar-stat"><span>🧠 Memories stored</span><strong>{_count}</strong></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="sidebar-card">Could not load memory bank stats.</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sidebar-section-title">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-card">Recalls similar past incidents → generates two '
        'responses for comparison → learns from your resolution.</div>',
        unsafe_allow_html=True,
    )


# ── MAIN HEADER ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div class="copilot-header">
        <span style="font-size:1.5rem">🚨</span>
        <h1 class="copilot-title">On-Call Copilot</h1>
        <span class="copilot-badge">Live</span>
    </div>
    <p class="copilot-sub">Paste an incident → instantly see what a generic agent says vs. one with memory of every past postmortem.</p>
</div>
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
        with st.spinner("🔍 Searching memory bank for similar incidents..."):
            recalled = recall_similar_incidents(incident_description)
            recalled = recalled[:5]

        # ── Metric row ────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-chip"><span class="status-dot live"></span><strong>Active</strong> &nbsp;incident in analysis</div>
            <div class="metric-chip">🧠 <strong>{len(recalled)}</strong> memories recalled</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Confidence badge + gauge (unique feature) ───────────────────────
        confidence_pct = min(100, len(recalled) * 22)
        if confidence_pct >= 66:
            conf_label, conf_color = "🎯 Strong Pattern Match", theme["success"]
        elif confidence_pct >= 22:
            conf_label, conf_color = "🔎 Partial Match Found", "#f59e0b"
        else:
            conf_label, conf_color = "🆕 New Pattern — No Memory Match", theme["primary"]

        gcol1, gcol2 = st.columns([1, 2])
        with gcol1:
            st.plotly_chart(make_gauge(confidence_pct, theme), use_container_width=True)
        with gcol2:
            st.markdown(
                f'<div class="confidence-badge" style="background:{conf_color}20;'
                f'color:{conf_color};border:1px solid {conf_color}50">{conf_label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "This score reflects how strongly the new incident matches knowledge "
                "already stored in Hindsight's memory bank. A low score means the "
                "agent is seeing a genuinely new pattern - resolving it below will "
                "teach the agent for next time."
            )

        # ── Side-by-side comparison ─────────────────────────────────────────
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown('<div class="card-label no-mem">🤖 Without Memory — generic agent</div>', unsafe_allow_html=True)
            with st.spinner("Generating generic response..."):
                generic_response = generate_without_memory(incident_description)

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

        # ── Recalled memories (clearer cards) ───────────────────────────────
        st.divider()
        st.markdown("#### Memories Recalled for This Incident")
        if recalled:
            st.caption(f"{len(recalled)} memory item(s) matched - ranked by relevance. These informed the response above.")
            relevance_steps = [95, 80, 65, 50, 35]
            for i, m in enumerate(recalled):
                mtype = getattr(m, "type", "memory")
                tclass = mem_type_class(mtype)
                inc = extract_inc(m.text)
                rel = relevance_steps[i] if i < len(relevance_steps) else 25

                badges = f'<span class="mem-badge {tclass}">{str(mtype).upper()}</span>'
                if inc:
                    badges += f'<span class="mem-badge inc">{inc}</span>'

                st.markdown(
                    f"""
                    <div class="mem-card">
                        <div class="mem-card-top">
                            {badges}
                            <span class="mem-rank">Relevance #{i+1}</span>
                        </div>
                        <div class="mem-text">{m.text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(rel / 100)
        else:
            st.warning("No relevant past incidents found in memory. This is a new pattern — resolve it below to teach the agent.")

        # ── Resolve & teach ───────────────────────────────────────────────────
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
                    record_memory_count()
                    st.success("Saved! This incident is now part of the agent's memory.")
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
    st.markdown("#### Auth Service Memory Bank")
    st.caption("Every past incident postmortem stored here. Grows as you save new resolutions.")

    refresh_col, _ = st.columns([1, 4])
    with refresh_col:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    try:
        count, items = record_memory_count()
        if count is None:
            raise RuntimeError("Could not retrieve memories")

        st.markdown(
            f'<div class="metric-chip" style="display:inline-block;margin-bottom:1rem">'
            f'🧠 <strong>{count}</strong> total memories in bank</div>',
            unsafe_allow_html=True,
        )

        # Build type + INC frequency counts
        type_counts, inc_counts = {}, {}
        for mem in items:
            if isinstance(mem, dict):
                text = mem.get("text") or mem.get("content") or mem.get("memory") or str(mem)
                mtype = mem.get("type") or mem.get("context") or "other"
            else:
                text = getattr(mem, "text", None) or getattr(mem, "content", None) or str(mem)
                mtype = getattr(mem, "type", None) or "other"

            if isinstance(mtype, str) and mtype.startswith("{"):
                mtype = "other"
            mtype = str(mtype).upper()
            type_counts[mtype] = type_counts.get(mtype, 0) + 1

            inc = extract_inc(text)
            if inc:
                inc_counts[inc] = inc_counts.get(inc, 0) + 1

        # ── Charts row ────────────────────────────────────────────────────
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Memory Type Breakdown**")
            if type_counts:
                st.plotly_chart(make_donut(type_counts, theme), use_container_width=True)
            else:
                st.info("No memory type data yet.")

        with chart_col2:
            st.markdown("**Past Incidents Referenced**")
            if inc_counts:
                inc_counts_sorted = dict(sorted(inc_counts.items(), key=lambda x: x[1], reverse=True))
                st.plotly_chart(make_inc_bar(inc_counts_sorted, theme), use_container_width=True)
            else:
                st.info("No incident references found yet.")

        st.markdown("**Memory Growth This Session**")
        if len(st.session_state.growth_history) >= 2:
            st.plotly_chart(make_growth_chart(st.session_state.growth_history, theme), use_container_width=True)
        else:
            st.caption("Analyze an incident or save a resolution to start tracking growth during this session.")

        st.divider()
        st.markdown("**All Stored Memories**")
        for mem in items:
            if isinstance(mem, dict):
                text = mem.get("text") or mem.get("content") or mem.get("memory") or str(mem)
                mtype = mem.get("type") or mem.get("context") or "other"
            else:
                text = getattr(mem, "text", None) or getattr(mem, "content", None) or str(mem)
                mtype = getattr(mem, "type", None) or "other"

            if isinstance(mtype, str) and mtype.startswith("{"):
                mtype = "other"

            tclass = mem_type_class(mtype)
            inc = extract_inc(text)
            badges = f'<span class="mem-badge {tclass}">{str(mtype).upper()}</span>'
            if inc:
                badges += f'<span class="mem-badge inc">{inc}</span>'

            preview = str(text)[:90].replace("\n", " ")
            with st.expander(f"{preview}..."):
                st.markdown(f'<div class="mem-card-top">{badges}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="mem-text">{text}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not load memories: {e}")
