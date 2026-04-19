"""
pages/2_Evening.py — Evening Reflection page for Saga.

Workflow:
  1. Load today's plan from DB (shows prompt if none found).
  2. User sets completion % slider and evening mood.
  3. Phase 1: "Generate Questions" → 3 tailored reflection questions.
  4. User types answers into 3 text areas.
  5. Phase 2: "Synthesise Reflection" → wins, blockers, insight summary, pattern note.
  6. Reflection is saved to the database.
"""

import json
import streamlit as st
from datetime import date

from components.styles import (
    inject_css,
    render_gradient_title,
    render_category_chip,
)
from agents.reflection_agent import generate_questions, synthesize_reflection
from database.schema import init_db
from database.queries import save_reflection, get_plan, get_reflection
from utils.date_helpers import format_date

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Evening — Saga",
    page_icon="🌙",
    layout="wide",
)
init_db()
inject_css()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MOOD_OPTIONS = ["😴", "😤", "😐", "🙂", "😊", "🤩"]
MOOD_LABELS = {
    "😴": "Exhausted",
    "😤": "Frustrated",
    "😐": "Neutral",
    "🙂": "Good",
    "😊": "Happy",
    "🤩": "Energised",
}
TODAY = format_date(date.today())

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(render_gradient_title("Evening Reflection"), unsafe_allow_html=True)
st.markdown(
    f'<p style="color:#9B96B0;margin-top:-0.5rem;">{date.today().strftime("%A, %B %#d, %Y")}</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "reflection_questions" not in st.session_state:
    st.session_state.reflection_questions = None
if "reflection_synthesis" not in st.session_state:
    st.session_state.reflection_synthesis = None
if "reflection_saved" not in st.session_state:
    st.session_state.reflection_saved = False

# ---------------------------------------------------------------------------
# Load today's plan
# ---------------------------------------------------------------------------
today_plan = get_plan(TODAY)
today_reflection = get_reflection(TODAY)

# Pre-populate synthesis from DB if already saved
if today_reflection and st.session_state.reflection_synthesis is None:
    st.session_state.reflection_questions = today_reflection.get("questions", [])
    st.session_state.reflection_synthesis = {
        "wins": today_reflection.get("wins", []),
        "blockers": today_reflection.get("blockers", []),
        "insight_summary": today_reflection.get("insight_summary", ""),
        "pattern_note": None,
    }
    st.session_state.reflection_saved = True

# ---------------------------------------------------------------------------
# No plan warning
# ---------------------------------------------------------------------------
if today_plan is None:
    st.warning(
        "No morning plan found for today. "
        "Head to the **Morning Planning** page first to create one, "
        "or you can still do a free-form reflection below.",
        icon="⚠",
    )
    # Provide a minimal plan stub so reflection can still proceed
    plan_priorities = []
    plan_full_text = ""
else:
    plan_priorities = today_plan.get("priorities", [])
    plan_output_raw = today_plan.get("plan_output", "{}")
    try:
        plan_parsed = json.loads(plan_output_raw)
        plan_full_text = plan_parsed.get("full_plan", "")
    except Exception:
        plan_full_text = plan_output_raw

# ---------------------------------------------------------------------------
# Layout: left = inputs, right = questions + synthesis
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    # Show today's priorities as a summary
    if plan_priorities:
        st.markdown('<p class="saga-section-title">Today\'s Priorities</p>', unsafe_allow_html=True)
        for p in plan_priorities:
            cat_chip = render_category_chip(p.get("category", "Work"))
            task_text = p.get("task", "")
            st.markdown(
                f'<div style="margin-bottom:0.35rem;">{cat_chip} {task_text}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<p class="saga-section-title" style="margin-top:1.5rem;">How much did you get done?</p>', unsafe_allow_html=True)
    completion_pct = st.slider(
        label="Completion %",
        min_value=0,
        max_value=100,
        value=today_reflection.get("completion_pct", 70) if today_reflection else 70,
        step=5,
        format="%d%%",
        label_visibility="visible",
    )

    st.markdown('<p class="saga-section-title">Evening mood</p>', unsafe_allow_html=True)
    mood_evening = st.radio(
        label="Evening Mood",
        options=MOOD_OPTIONS,
        index=3,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.caption(f"Mood: {MOOD_LABELS.get(mood_evening, mood_evening)}")

    generate_questions_btn = st.button(
        "Generate Reflection Questions",
        type="primary",
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# Phase 1 — Generate questions
# ---------------------------------------------------------------------------
if generate_questions_btn:
    with st.spinner("Generating your reflection questions..."):
        try:
            questions = generate_questions(
                plan_output=plan_full_text,
                priorities=plan_priorities,
                completion_pct=completion_pct,
                date_str=TODAY,
            )
            st.session_state.reflection_questions = questions
            st.session_state.reflection_synthesis = None
            st.session_state.reflection_saved = False
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to generate questions: {exc}")

# ---------------------------------------------------------------------------
# Phase 2 — Answer questions + synthesise
# ---------------------------------------------------------------------------
with col_right:
    questions = st.session_state.reflection_questions

    if questions is None:
        st.markdown(
            '<div class="saga-card" style="text-align:center;padding:3rem;">'
            '<span style="font-size:3rem;">🌙</span><br>'
            '<span style="color:#9B96B0;">Set your completion % and mood,<br>'
            'then hit <strong style="color:#9B7FD4;">Generate Reflection Questions</strong></span>'
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="saga-section-title">Reflect on your day</p>', unsafe_allow_html=True)

        answers = []
        for q in questions:
            answer = st.text_area(
                label=q.get("text", f"Question {q.get('id', '?')}"),
                key=f"answer_{q.get('id', q.get('text', '')[:20])}",
                height=100,
            )
            answers.append(answer)

        # Only enable synthesis if all questions have answers
        all_answered = all(a.strip() for a in answers)
        synthesize_btn = st.button(
            "Synthesise Reflection",
            type="primary",
            disabled=not all_answered,
            use_container_width=True,
        )

        if not all_answered:
            st.caption("Answer all 3 questions to unlock synthesis.")

        if synthesize_btn and all_answered:
            with st.spinner("Saga is synthesising your reflection..."):
                try:
                    synthesis = synthesize_reflection(
                        questions=questions,
                        answers=answers,
                        completion_pct=completion_pct,
                        date_str=TODAY,
                        mood_evening=f"{mood_evening} {MOOD_LABELS.get(mood_evening, '')}",
                    )

                    # Save to DB
                    plan_id = today_plan["id"] if today_plan else None
                    save_reflection(
                        date=TODAY,
                        plan_id=plan_id,
                        questions=questions,
                        answers=answers,
                        completion_pct=completion_pct,
                        mood_evening=f"{mood_evening} {MOOD_LABELS.get(mood_evening, '')}",
                        wins=synthesis.get("wins", []),
                        blockers=synthesis.get("blockers", []),
                        insight_summary=synthesis.get("insight_summary", ""),
                    )

                    st.session_state.reflection_synthesis = synthesis
                    st.session_state.reflection_saved = True
                    st.rerun()

                except Exception as exc:
                    st.error(f"Failed to synthesise reflection: {exc}")

        # Show synthesis results
        synthesis = st.session_state.reflection_synthesis
        if synthesis:
            st.markdown("---")
            st.markdown('<p class="saga-section-title">Today\'s Insights</p>', unsafe_allow_html=True)

            wins = synthesis.get("wins", [])
            blockers = synthesis.get("blockers", [])
            insight = synthesis.get("insight_summary", "")
            pattern = synthesis.get("pattern_note")

            if wins:
                st.markdown(
                    '<div class="saga-card-accent">'
                    '<strong style="color:#4ADE80;">Wins</strong><ul style="margin:0.5rem 0 0 1rem;">'
                    + "".join(f"<li>{w}</li>" for w in wins)
                    + "</ul></div>",
                    unsafe_allow_html=True,
                )

            if blockers:
                st.markdown(
                    '<div class="saga-card" style="border-left:4px solid #F87171;">'
                    '<strong style="color:#F87171;">Blockers</strong><ul style="margin:0.5rem 0 0 1rem;">'
                    + "".join(f"<li>{b}</li>" for b in blockers)
                    + "</ul></div>",
                    unsafe_allow_html=True,
                )

            if insight:
                st.markdown(
                    f'<div class="saga-card-accent">'
                    f'<strong style="color:#9B7FD4;">Insight</strong>'
                    f'<p style="margin:0.5rem 0 0;color:#E8E4F0;">{insight}</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            if pattern:
                st.markdown(
                    f'<div class="saga-card">'
                    f'<strong style="color:#FBBF24;">Pattern Note</strong>'
                    f'<p style="margin:0.5rem 0 0;color:#E8E4F0;font-style:italic;">{pattern}</p>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            if st.session_state.reflection_saved:
                st.success("Reflection saved to your Saga journal.", icon="✅")
