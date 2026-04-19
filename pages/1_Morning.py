"""
pages/1_Morning.py — Morning Planning page for Saga.

Workflow:
  1. User selects mood emoji, energy slider, types their task brain-dump.
  2. "Generate My Plan" calls the Morning Agent.
  3. Results are displayed: greeting, Daily Intention card, priority chips,
     full markdown plan, deferred tasks.
  4. Plan + tasks are saved to the database.
"""

import streamlit as st
from datetime import date

from components.styles import (
    inject_css,
    render_intention_card,
    render_category_chip,
    render_gradient_title,
)
from agents.morning_agent import run_morning_agent
from database.schema import init_db
from database.queries import save_plan, save_tasks, get_plan, get_recent_plans
from utils.date_helpers import format_date

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Morning — Saga",
    page_icon="☀",
    layout="wide",
)
init_db()
inject_css()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MOOD_OPTIONS = ["😴", "😐", "🙂", "😊", "🤩"]
MOOD_LABELS = {
    "😴": "Tired",
    "😐": "Neutral",
    "🙂": "Good",
    "😊": "Happy",
    "🤩": "Energised",
}
TODAY = format_date(date.today())

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(render_gradient_title("Morning Planning"), unsafe_allow_html=True)
st.markdown(
    f'<p style="color:#9B96B0;margin-top:-0.5rem;">{date.today().strftime("%A, %B %#d, %Y")}</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Check if plan already exists for today
# ---------------------------------------------------------------------------
existing_plan = get_plan(TODAY)

# ---------------------------------------------------------------------------
# Session state for plan output
# ---------------------------------------------------------------------------
if "morning_plan" not in st.session_state:
    st.session_state.morning_plan = None
if "morning_saved" not in st.session_state:
    st.session_state.morning_saved = False

# If a plan was saved today, pre-populate session state from DB
if existing_plan and st.session_state.morning_plan is None:
    import json as _json
    try:
        plan_output = _json.loads(existing_plan["plan_output"])
    except Exception:
        plan_output = {"full_plan": existing_plan["plan_output"]}
    st.session_state.morning_plan = plan_output
    st.session_state.morning_saved = True

# ---------------------------------------------------------------------------
# Input form (left column) | Output (right column)
# ---------------------------------------------------------------------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<p class="saga-section-title">How are you feeling?</p>', unsafe_allow_html=True)

    # Mood selector — use Streamlit radio rendered as large emoji buttons
    mood_emoji = st.radio(
        label="Mood",
        options=MOOD_OPTIONS,
        index=2,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.caption(f"Mood: {MOOD_LABELS.get(mood_emoji, mood_emoji)}")

    st.markdown('<p class="saga-section-title">Energy level</p>', unsafe_allow_html=True)
    energy = st.slider(
        label="Energy (1 = exhausted, 5 = fully charged)",
        min_value=1,
        max_value=5,
        value=3,
        label_visibility="visible",
    )

    st.markdown('<p class="saga-section-title">Brain-dump your tasks</p>', unsafe_allow_html=True)
    brain_dump = st.text_area(
        label="What's on your plate today? (free-form — Saga will organise it)",
        placeholder=(
            "e.g.  Finish slide deck for 2pm client call\n"
            "       Review PR from Alice\n"
            "       Book dentist appointment\n"
            "       Prep for tomorrow's team standup\n"
            "       Go for a run"
        ),
        height=200,
        label_visibility="visible",
    )

    generate_btn = st.button(
        "Generate My Plan",
        type="primary",
        disabled=not brain_dump.strip(),
        use_container_width=True,
    )

    if existing_plan and not generate_btn:
        st.info("A plan already exists for today. Generating again will overwrite it.", icon="ℹ")

# ---------------------------------------------------------------------------
# Agent call
# ---------------------------------------------------------------------------
if generate_btn and brain_dump.strip():
    with col_output:
        with st.spinner("Saga is building your plan..."):
            try:
                recent_refs = get_recent_plans(3)
                # get_recent_plans returns plan dicts; fetch reflections for context
                from database.queries import get_reflection
                context_refs = []
                for p in recent_refs:
                    ref = get_reflection(p["date"])
                    if ref:
                        context_refs.append(ref)

                plan = run_morning_agent(
                    raw_input=brain_dump,
                    energy_level=energy,
                    mood=f"{mood_emoji} {MOOD_LABELS.get(mood_emoji, '')}",
                    date_str=TODAY,
                    recent_reflections=context_refs,
                )

                # Save to database
                import json as _json
                plan_id = save_plan(
                    date=TODAY,
                    raw_input=brain_dump,
                    plan_output=_json.dumps(plan),
                    priorities=plan.get("priorities", []),
                    energy_level=energy,
                    mood_morning=f"{mood_emoji} {MOOD_LABELS.get(mood_emoji, '')}",
                )

                # Save individual tasks
                tasks = [
                    {
                        "task_text": p.get("task", ""),
                        "priority_rank": p.get("rank", i + 1),
                        "category": p.get("category", "Work"),
                        "completed": False,
                    }
                    for i, p in enumerate(plan.get("priorities", []))
                ]
                if tasks:
                    save_tasks(plan_id=plan_id, date=TODAY, tasks=tasks)

                st.session_state.morning_plan = plan
                st.session_state.morning_saved = True
                st.rerun()

            except Exception as exc:
                st.error(f"Failed to generate plan: {exc}")

# ---------------------------------------------------------------------------
# Display plan output
# ---------------------------------------------------------------------------
with col_output:
    plan = st.session_state.morning_plan

    if plan is None:
        st.markdown(
            '<div class="saga-card" style="text-align:center;padding:3rem;">'
            '<span style="font-size:3rem;">☀️</span><br>'
            '<span style="color:#9B96B0;">Fill in your morning check-in and hit<br>'
            '<strong style="color:#9B7FD4;">Generate My Plan</strong></span>'
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # Greeting
        greeting = plan.get("greeting", "Good morning!")
        st.markdown(
            f'<div class="saga-card-accent">'
            f'<span style="font-size:1.1rem;">{greeting}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # Daily Intention card
        intention = plan.get("daily_intention", "Make today count.")
        st.markdown(render_intention_card(intention), unsafe_allow_html=True)

        # Priority chips + tasks
        priorities = plan.get("priorities", [])
        if priorities:
            st.markdown('<p class="saga-section-title">Today\'s Priorities</p>', unsafe_allow_html=True)
            for p in priorities:
                rank = p.get("rank", "")
                task_text = p.get("task", "Unnamed task")
                category = p.get("category", "Work")
                why = p.get("why_today", "")
                cat_chip = render_category_chip(category)

                st.markdown(
                    f'<div class="saga-card" style="padding:0.75rem 1rem;margin-bottom:0.5rem;">'
                    f'<span style="color:#9B7FD4;font-weight:700;margin-right:0.5rem;">#{rank}</span>'
                    f"{cat_chip} "
                    f'<strong>{task_text}</strong>'
                    + (f'<br><span style="font-size:0.82rem;color:#9B96B0;margin-top:0.25rem;display:block;">{why}</span>' if why else "")
                    + "</div>",
                    unsafe_allow_html=True,
                )

        # Focus hours
        focus_hrs = plan.get("estimated_focus_hours", 0)
        if focus_hrs:
            st.markdown(
                f'<p style="color:#9B96B0;font-size:0.88rem;">Estimated focus time: '
                f'<strong style="color:#9B7FD4;">{focus_hrs:.1f} hours</strong></p>',
                unsafe_allow_html=True,
            )

        # Full plan markdown
        full_plan = plan.get("full_plan", "")
        if full_plan:
            with st.expander("Full plan details", expanded=False):
                st.markdown(full_plan)

        # Deferred tasks
        deferred = plan.get("deferred", [])
        if deferred:
            with st.expander(f"Deferred ({len(deferred)} tasks)", expanded=False):
                for item in deferred:
                    st.markdown(f"- {item}")

        if st.session_state.morning_saved:
            st.success("Plan saved to your Saga journal.", icon="✅")
