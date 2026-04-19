"""
components/charts.py — Three Plotly charts for the Weekly page.

Charts
------
1. completion_bar_chart(plans, reflections) -> go.Figure
   Daily completion % as bars coloured by morning mood.

2. mood_timeline_chart(plans, reflections) -> go.Figure
   Morning mood (circles) and evening mood (diamonds) as two overlaid lines.

3. category_donut_chart(tasks) -> go.Figure
   Task count by category as a donut chart.

All charts use the Saga dark colour palette for visual consistency.
"""

from __future__ import annotations

from typing import Optional
import plotly.graph_objects as go
import plotly.express as px

from .styles import COLORS

# ---------------------------------------------------------------------------
# Shared layout defaults
# ---------------------------------------------------------------------------

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="sans-serif", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(26,26,46,0.8)",
        bordercolor=COLORS["card_border"],
        borderwidth=1,
        font=dict(color=COLORS["text"]),
    ),
)

# Mood → numeric mapping (for the timeline chart)
_MOOD_SCORE = {
    # Morning moods
    "😴": 1,
    "😐": 2,
    "🙂": 3,
    "😊": 4,
    "🤩": 5,
    # Evening moods (may also use 😤)
    "😤": 1.5,
}

_MOOD_LABEL = {
    1: "Tired",
    1.5: "Frustrated",
    2: "Neutral",
    3: "Good",
    4: "Happy",
    5: "Energised",
}

# Category → colour
_CAT_COLORS = {
    "Work": COLORS["info"],
    "Personal": COLORS["accent"],
    "Health": COLORS["success"],
    "Creative": COLORS["warning"],
    "Admin": "#9CA3AF",
}


def _mood_to_score(mood_str: str) -> float:
    """Extract the first emoji from a mood string and map it to a numeric score."""
    if not mood_str:
        return 3.0
    # Try each key
    for emoji, score in _MOOD_SCORE.items():
        if emoji in mood_str:
            return score
    return 3.0  # default neutral


def _short_date(date_str: str) -> str:
    """Turn '2026-04-14' into 'Mon 14'."""
    try:
        from datetime import date
        d = date.fromisoformat(date_str)
        return d.strftime("%a %#d")
    except Exception:
        return date_str[-5:]


# ---------------------------------------------------------------------------
# Chart 1 — Daily completion bar chart
# ---------------------------------------------------------------------------

def completion_bar_chart(
    plans: list[dict],
    reflections: list[dict],
) -> go.Figure:
    """
    Bar chart of daily completion % coloured by morning mood score.

    Parameters
    ----------
    plans : list[dict]
        Daily plan rows from the DB (must have 'date' and 'mood_morning').
    reflections : list[dict]
        Reflection rows from the DB (must have 'date' and 'completion_pct').

    Returns
    -------
    go.Figure
    """
    # Build a date-keyed lookup
    ref_map = {r["date"]: r for r in reflections}
    plan_map = {p["date"]: p for p in plans}

    # Merge on dates that have both a plan and a reflection
    dates = sorted(set(ref_map.keys()) & set(plan_map.keys()))

    if not dates:
        # Return empty chart with placeholder text
        fig = go.Figure()
        fig.add_annotation(
            text="No data yet — complete your first Morning + Evening session!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["text_muted"], size=14),
        )
        fig.update_layout(title="Daily Completion", **_LAYOUT_DEFAULTS)
        return fig

    labels = [_short_date(d) for d in dates]
    completions = [ref_map[d].get("completion_pct", 0) for d in dates]
    mood_scores = [_mood_to_score(plan_map[d].get("mood_morning", "")) for d in dates]

    # Map mood score to colour (gradient from danger → success)
    def _score_to_color(score: float) -> str:
        score = max(1.0, min(5.0, score))
        # 1 = danger, 3 = warning, 5 = success
        if score <= 2:
            return COLORS["danger"]
        elif score <= 3:
            return COLORS["warning"]
        elif score <= 4:
            return COLORS["info"]
        else:
            return COLORS["success"]

    bar_colors = [_score_to_color(s) for s in mood_scores]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=completions,
            marker_color=bar_colors,
            marker_line_color=COLORS["card_border"],
            marker_line_width=1,
            text=[f"{c}%" for c in completions],
            textposition="outside",
            textfont=dict(color=COLORS["text"], size=11),
            hovertemplate="<b>%{x}</b><br>Completion: %{y}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="Daily Completion", font=dict(color=COLORS["text"], size=15)),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=COLORS["text_muted"]),
            linecolor=COLORS["card_border"],
        ),
        yaxis=dict(
            range=[0, 115],
            showgrid=True,
            gridcolor=COLORS["card_border"],
            ticksuffix="%",
            tickfont=dict(color=COLORS["text_muted"]),
            linecolor=COLORS["card_border"],
        ),
        **_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 2 — Mood timeline
# ---------------------------------------------------------------------------

def mood_timeline_chart(
    plans: list[dict],
    reflections: list[dict],
) -> go.Figure:
    """
    Dual-line chart: morning mood (circles) and evening mood (diamonds).

    Parameters
    ----------
    plans : list[dict]
        Must have 'date' and 'mood_morning'.
    reflections : list[dict]
        Must have 'date' and 'mood_evening'.

    Returns
    -------
    go.Figure
    """
    plan_map = {p["date"]: p for p in plans}
    ref_map = {r["date"]: r for r in reflections}

    all_dates = sorted(set(plan_map.keys()) | set(ref_map.keys()))

    if not all_dates:
        fig = go.Figure()
        fig.add_annotation(
            text="No mood data yet.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["text_muted"], size=14),
        )
        fig.update_layout(title="Mood Timeline", **_LAYOUT_DEFAULTS)
        return fig

    labels = [_short_date(d) for d in all_dates]

    morning_scores = [
        _mood_to_score(plan_map[d].get("mood_morning", "")) if d in plan_map else None
        for d in all_dates
    ]
    evening_scores = [
        _mood_to_score(ref_map[d].get("mood_evening", "")) if d in ref_map else None
        for d in all_dates
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=morning_scores,
            mode="lines+markers",
            name="Morning",
            line=dict(color=COLORS["primary_light"], width=2),
            marker=dict(
                symbol="circle",
                size=9,
                color=COLORS["primary_light"],
                line=dict(color=COLORS["bg"], width=1.5),
            ),
            hovertemplate="<b>%{x}</b><br>Morning mood: %{y:.0f}/5<extra></extra>",
            connectgaps=True,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=evening_scores,
            mode="lines+markers",
            name="Evening",
            line=dict(color=COLORS["accent"], width=2, dash="dot"),
            marker=dict(
                symbol="diamond",
                size=9,
                color=COLORS["accent"],
                line=dict(color=COLORS["bg"], width=1.5),
            ),
            hovertemplate="<b>%{x}</b><br>Evening mood: %{y:.0f}/5<extra></extra>",
            connectgaps=True,
        )
    )

    fig.update_layout(
        title=dict(text="Mood Timeline", font=dict(color=COLORS["text"], size=15)),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=COLORS["text_muted"]),
            linecolor=COLORS["card_border"],
        ),
        yaxis=dict(
            range=[0.5, 5.5],
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["Tired", "Neutral", "Good", "Happy", "Energised"],
            showgrid=True,
            gridcolor=COLORS["card_border"],
            tickfont=dict(color=COLORS["text_muted"]),
            linecolor=COLORS["card_border"],
        ),
        **_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 3 — Category donut
# ---------------------------------------------------------------------------

def category_donut_chart(tasks: list[dict]) -> go.Figure:
    """
    Donut chart of task count by category.

    Parameters
    ----------
    tasks : list[dict]
        Task rows from the DB (must have 'category').

    Returns
    -------
    go.Figure
    """
    if not tasks:
        fig = go.Figure()
        fig.add_annotation(
            text="No task data yet.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=COLORS["text_muted"], size=14),
        )
        fig.update_layout(title="Tasks by Category", **_LAYOUT_DEFAULTS)
        return fig

    # Count by category
    counts: dict[str, int] = {}
    for t in tasks:
        cat = t.get("category", "Work")
        counts[cat] = counts.get(cat, 0) + 1

    categories = list(counts.keys())
    values = [counts[c] for c in categories]
    colors = [_CAT_COLORS.get(c, COLORS["primary"]) for c in categories]

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=categories,
            values=values,
            hole=0.55,
            marker=dict(
                colors=colors,
                line=dict(color=COLORS["bg"], width=2),
            ),
            textfont=dict(color=COLORS["text"], size=12),
            hovertemplate="<b>%{label}</b><br>%{value} tasks (%{percent})<extra></extra>",
            showlegend=True,
        )
    )

    fig.update_layout(
        title=dict(text="Tasks by Category", font=dict(color=COLORS["text"], size=15)),
        **_LAYOUT_DEFAULTS,
    )
    return fig
