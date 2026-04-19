"""
app.py — Saga entry point.

Responsibilities:
  1. Initialise the database (creates saga.db tables if they don't exist).
  2. Seed demo data when the DB is empty (so Streamlit Cloud always shows
     a compelling demo on a cold start).
  3. Render the sidebar with: Saga logo, live streak counter, today's date,
     and navigation links to the three pages.
  4. Show a welcome / home screen on the root URL.

Navigation is handled by Streamlit's built-in multi-page mechanism
(pages/ directory).  This file renders the sidebar and home screen.
"""

import streamlit as st

# ---- DB bootstrap (must happen before any page renders) ----
from database.schema import init_db
from utils.demo_data import db_is_empty, seed_demo_data
from utils.date_helpers import today, format_date, calculate_streak
from database.queries import get_active_dates
from components.styles import inject_css, render_gradient_title, COLORS

# Initialise tables
init_db()

# Seed demo data on cold start
if db_is_empty():
    seed_demo_data()

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Saga — Personal AI",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # Logo / brand
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 1.25rem 0 1rem 0;
        ">
            <div style="
                font-size: 2.5rem;
                font-weight: 900;
                background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -1px;
            ">Saga</div>
            <div style="
                font-size: 0.75rem;
                color: {COLORS['text_muted']};
                margin-top: -0.25rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            ">Personal AI Agent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Streak counter
    active_dates = get_active_dates(30)
    streak = calculate_streak(active_dates)

    streak_color = (
        COLORS["success"] if streak >= 5
        else COLORS["warning"] if streak >= 2
        else COLORS["text_muted"]
    )

    st.markdown(
        f"""
        <div style="
            background: {COLORS['card_bg']};
            border: 1px solid {COLORS['card_border']};
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <div style="font-size:0.7rem; color:{COLORS['text_muted']}; text-transform:uppercase; letter-spacing:0.06em;">Current Streak</div>
                <div style="font-size:1.6rem; font-weight:700; color:{streak_color}; line-height:1.2;">{streak} day{'s' if streak != 1 else ''}</div>
            </div>
            <div style="font-size:2rem;">{'*' if streak >= 3 else '~'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Today's date
    st.markdown(
        f"""
        <div style="
            font-size: 0.8rem;
            color: {COLORS['text_muted']};
            padding: 0.25rem 0 0.75rem 0;
            text-align: center;
        ">
            {format_date(today(), '%A, %B %#d, %Y') if hasattr(today(), 'strftime') else str(today())}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Navigation
    st.page_link("app.py", label="Home", icon=None)
    st.page_link("pages/1_Morning.py", label="Morning Plan")
    st.page_link("pages/2_Evening.py", label="Evening Reflection")
    st.page_link("pages/3_Weekly.py", label="Weekly Review")

    st.divider()

    # Stats summary
    total_active = len(active_dates)
    st.markdown(
        f"""
        <div style="font-size:0.75rem; color:{COLORS['text_muted']}; padding-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; padding:0.2rem 0;">
                <span>Logged days (30d)</span>
                <span style="color:{COLORS['text']}; font-weight:600;">{total_active}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Home / landing screen
# ---------------------------------------------------------------------------

st.markdown(render_gradient_title("Welcome to Saga"), unsafe_allow_html=True)

st.markdown(
    f"""
    <p style="color:{COLORS['text_muted']}; font-size:1.1rem; max-width:640px; margin-bottom:2rem;">
    Your personal AI agent for daily planning, evening reflection, and weekly insight.
    Powered by Claude.
    </p>
    """,
    unsafe_allow_html=True,
)

# Quick-action cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="saga-card" style="text-align:center; padding: 1.75rem 1rem;">
            <div style="font-size:2.25rem; margin-bottom:0.75rem;">AM</div>
            <div style="font-size:1.05rem; font-weight:600; color:{COLORS['text']};">Morning Plan</div>
            <div style="font-size:0.8rem; color:{COLORS['text_muted']}; margin-top:0.4rem;">
                Brain-dump your tasks.<br>Let Saga prioritise your day.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="saga-card" style="text-align:center; padding: 1.75rem 1rem;">
            <div style="font-size:2.25rem; margin-bottom:0.75rem;">PM</div>
            <div style="font-size:1.05rem; font-weight:600; color:{COLORS['text']};">Evening Reflection</div>
            <div style="font-size:0.8rem; color:{COLORS['text_muted']}; margin-top:0.4rem;">
                Review what happened.<br>Surface wins and patterns.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="saga-card" style="text-align:center; padding: 1.75rem 1rem;">
            <div style="font-size:2.25rem; margin-bottom:0.75rem;">WK</div>
            <div style="font-size:1.05rem; font-weight:600; color:{COLORS['text']};">Weekly Review</div>
            <div style="font-size:0.8rem; color:{COLORS['text_muted']}; margin-top:0.4rem;">
                See the shape of your week.<br>Read your AI-written narrative.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- How to get started ----
st.markdown("<br>", unsafe_allow_html=True)
_primary_light = COLORS["primary_light"]
st.markdown(
    f"<h3 style='color:{_primary_light};'>Get Started</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <ol style="color:{COLORS['text']}; line-height:2rem;">
        <li>Open <strong>Morning Plan</strong> each morning — paste your task list and get a prioritised plan.</li>
        <li>Open <strong>Evening Reflection</strong> at day's end — answer 3 targeted questions for an insight summary.</li>
        <li>Open <strong>Weekly Review</strong> on Friday or Monday — read your AI-generated narrative and review charts.</li>
    </ol>
    """,
    unsafe_allow_html=True,
)

# ---- Demo data notice ----
if total_active > 0 and streak == 0:
    st.info(
        "Demo data is loaded so you can explore all features. "
        "Start using the app and your real data will replace it."
    )
