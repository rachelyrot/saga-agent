"""
pages/3_Weekly.py — Weekly Review page.

Shows:
  - 4 metric cards (avg completion, total tasks, active days, avg energy)
  - 3 Plotly charts (completion bars, mood timeline, category donut)
  - Streaming weekly narrative from the Weekly Narrator agent

The user selects which week to review (defaults to the current / most-recent
week that has data).  Cached narratives are loaded instantly; new ones are
streamed live.
"""

import streamlit as st

from components.styles import (
    inject_css,
    render_gradient_title,
    render_metric_card,
    COLORS,
)
from components.charts import (
    completion_bar_chart,
    mood_timeline_chart,
    category_donut_chart,
)
from database.queries import (
    get_plans_for_week,
    get_reflections_for_week,
    get_tasks_for_week,
    get_weekly_narrative,
    save_weekly_narrative,
    get_all_weekly_narratives,
)
from utils.date_helpers import (
    current_week_range,
    week_range_for_date,
    dates_in_week,
    format_date,
    parse_date,
)
from agents.weekly_narrator import run_weekly_narrator

# ---------------------------------------------------------------------------
# Page config & CSS
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Saga — Weekly Review", page_icon="📅", layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOOD_SCORE = {
    "Energised": 5, "Happy": 4, "Neutral": 3, "Tired": 2, "Stressed": 1,
    "energised": 5, "happy": 4, "neutral": 3, "tired": 2, "stressed": 1,
    "Great": 5, "Good": 4, "Okay": 3, "Low": 2, "Rough": 1,
    "great": 5, "good": 4, "okay": 3, "low": 2, "rough": 1,
}


def _compute_stats(plans: list, reflections: list, tasks: list) -> dict:
    """Return aggregate stats dict for the given week's data."""
    ref_by_date = {r["date"]: r for r in reflections}
    completions = [
        ref_by_date[p["date"]].get("completion_pct", 0)
        for p in plans
        if p["date"] in ref_by_date
    ]
    avg_completion = round(sum(completions) / len(completions)) if completions else 0

    energy_vals = [p.get("energy_level", 0) for p in plans if p.get("energy_level")]
    avg_energy = round(sum(energy_vals) / len(energy_vals), 1) if energy_vals else 0

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("completed"))

    return {
        "avg_completion": avg_completion,
        "avg_energy": avg_energy,
        "active_days": len(plans),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
    }


def _week_label(week_start, week_end) -> str:
    from datetime import date as date_type
    ws = week_start if isinstance(week_start, date_type) else parse_date(str(week_start))
    we = week_end if isinstance(week_end, date_type) else parse_date(str(week_end))
    return f"{ws.strftime('%b %d')} – {we.strftime('%b %d, %Y')}"


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

st.markdown(render_gradient_title("Weekly Review"), unsafe_allow_html=True)

# --- Week selector ---
# Gather all known weeks from existing narratives + current week
all_narratives = get_all_weekly_narratives()
current_ws, current_we = current_week_range()

known_weeks: list[tuple[str, str]] = [(current_ws, current_we)]
for n in all_narratives:
    pair = (n["week_start"], n["week_end"])
    if pair not in known_weeks:
        known_weeks.append(pair)

week_labels = [_week_label(ws, we) for ws, we in known_weeks]
selected_idx = st.selectbox(
    "Select week",
    range(len(week_labels)),
    format_func=lambda i: week_labels[i],
    index=0,
)

week_start, week_end = known_weeks[selected_idx]

# Load data for the selected week
plans = get_plans_for_week(week_start, week_end)
reflections = get_reflections_for_week(week_start, week_end)
tasks = get_tasks_for_week(week_start, week_end)

# -------------------------------------------------------------------------
# Metric cards
# -------------------------------------------------------------------------
stats = _compute_stats(plans, reflections, tasks)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        render_metric_card(f"{stats['avg_completion']}%", "Avg Completion"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        render_metric_card(str(stats["completed_tasks"]), "Tasks Completed"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        render_metric_card(str(stats["active_days"]), "Active Days"),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        render_metric_card(f"{stats['avg_energy']}/5", "Avg Energy"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# Charts
# -------------------------------------------------------------------------
if plans:
    chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])
    with chart_col1:
        st.subheader("Daily Completion")
        st.plotly_chart(
            completion_bar_chart(plans, reflections),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with chart_col2:
        st.subheader("Mood Timeline")
        st.plotly_chart(
            mood_timeline_chart(plans, reflections),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with chart_col3:
        st.subheader("Task Categories")
        st.plotly_chart(
            category_donut_chart(tasks),
            use_container_width=True,
            config={"displayModeBar": False},
        )
else:
    st.info(
        f"No data yet for the week of {_week_label(week_start, week_end)}. "
        "Complete some morning plans and evening reflections first."
    )

st.divider()

# -------------------------------------------------------------------------
# Narrative section
# -------------------------------------------------------------------------
st.subheader("Weekly Narrative")

# Check if a saved narrative already exists
existing = get_weekly_narrative(week_start)

if existing:
    # Display saved narrative
    theme = existing.get("theme", "Weekly Review")
    narrative = existing.get("narrative", "")
    key_insight = existing.get("key_insight", "")

    st.markdown(
        f'<h3 style="color:{COLORS["accent"]}; margin-bottom:0.25rem;">{theme}</h3>',
        unsafe_allow_html=True,
    )
    st.markdown(narrative)

    if key_insight:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(124,92,191,0.25), rgba(192,132,252,0.15));
                border-left: 4px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 1rem 1.25rem;
                margin-top: 1rem;
            ">
            <strong style="color:{COLORS['accent']}">Key Insight</strong><br>
            <span style="color:{COLORS['text']}">{key_insight}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Offer to regenerate
    if plans and st.button("Regenerate Narrative", key="regen_btn"):
        st.session_state["run_narrator"] = True
        st.rerun()

elif plans:
    # Offer to generate
    if st.button("Generate Weekly Narrative", type="primary", key="gen_btn"):
        st.session_state["run_narrator"] = True
        st.rerun()
else:
    st.write("Add some daily plans and reflections to unlock your weekly narrative.")

# -------------------------------------------------------------------------
# Streaming narrative generation
# -------------------------------------------------------------------------
if st.session_state.get("run_narrator"):
    st.session_state["run_narrator"] = False  # reset flag immediately

    with st.spinner("Generating your weekly narrative…"):
        placeholder = st.empty()
        display_text = ""

        def _on_chunk(accumulated: str) -> None:
            """Update the placeholder with a streaming cursor."""
            placeholder.markdown(accumulated + " ▌")

        result = run_weekly_narrator(week_start, week_end, on_chunk=_on_chunk)

    # Final display (no cursor)
    placeholder.empty()

    if "_error" in result:
        st.error(f"Could not generate narrative: {result['_error']}")
    else:
        theme = result["theme"]
        narrative = result["narrative"]
        key_insight = result["key_insight"]

        # Save to DB
        save_weekly_narrative(
            week_start=week_start,
            week_end=week_end,
            narrative=narrative,
            stats=stats,
            theme=theme,
        )

        st.markdown(
            f'<h3 style="color:{COLORS["accent"]}; margin-bottom:0.25rem;">{theme}</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(narrative)

        if key_insight:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(124,92,191,0.25), rgba(192,132,252,0.15));
                    border-left: 4px solid {COLORS['accent']};
                    border-radius: 8px;
                    padding: 1rem 1.25rem;
                    margin-top: 1rem;
                ">
                <strong style="color:{COLORS['accent']}">Key Insight</strong><br>
                <span style="color:{COLORS['text']}">{key_insight}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.success("Narrative saved.")
        st.rerun()  # Reload page so the cached version is displayed next time
