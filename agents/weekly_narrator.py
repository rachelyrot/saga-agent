"""
agents/weekly_narrator.py — Weekly Narrator agent.

Uses client.messages.stream() to stream a rich weekly review narrative,
then parses the full accumulated text as JSON to extract:
  {theme, narrative (markdown), key_insight}

The system prompt (~420 tokens) is cached via cache_control="ephemeral".
"""

import json
import re
from typing import Generator, Optional

from . import WEEKLY_SYSTEM, MODEL, client
from database.queries import (
    get_plans_for_week,
    get_reflections_for_week,
    get_tasks_for_week,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_weekly_context(
    week_start: str,
    week_end: str,
    plans: list,
    reflections: list,
    tasks: list,
) -> str:
    """Assemble a rich text block summarising the week for the agent."""
    lines: list[str] = [
        f"Week: {week_start} to {week_end}",
        "",
        "--- DAILY SUMMARIES ---",
    ]

    # Index by date for easy lookup
    reflections_by_date = {r["date"]: r for r in reflections}
    tasks_by_date: dict[str, list] = {}
    for t in tasks:
        tasks_by_date.setdefault(t["date"], []).append(t)

    for plan in plans:
        date = plan["date"]
        ref = reflections_by_date.get(date, {})
        day_tasks = tasks_by_date.get(date, [])
        total = len(day_tasks)
        completed = sum(1 for t in day_tasks if t.get("completed"))
        pct = ref.get("completion_pct", round(completed / total * 100) if total else 0)

        lines.append(f"\nDate: {date}")
        lines.append(f"  Energy: {plan.get('energy_level', '?')}/5  |  Morning mood: {plan.get('mood_morning', '?')}")
        priorities = plan.get("priorities", [])
        if priorities:
            lines.append(f"  Top priorities: {', '.join(p.get('task', '') for p in priorities[:3])}")
        lines.append(f"  Completion: {pct}%  |  Tasks: {completed}/{total}")

        if ref:
            lines.append(f"  Evening mood: {ref.get('mood_evening', '?')}")
            wins = ref.get("wins", [])
            if wins:
                lines.append(f"  Wins: {'; '.join(wins[:3])}")
            blockers = ref.get("blockers", [])
            if blockers:
                lines.append(f"  Blockers: {'; '.join(blockers[:2])}")
            if ref.get("insight_summary"):
                lines.append(f"  Insight: {ref['insight_summary']}")

    # --- Aggregate stats ---
    all_completions = [
        reflections_by_date[p["date"]].get("completion_pct", 0)
        for p in plans
        if p["date"] in reflections_by_date
    ]
    avg_completion = round(sum(all_completions) / len(all_completions)) if all_completions else 0

    energy_vals = [p.get("energy_level", 0) for p in plans if p.get("energy_level")]
    avg_energy = round(sum(energy_vals) / len(energy_vals), 1) if energy_vals else 0

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("completed"))

    categories: dict[str, int] = {}
    for t in tasks:
        cat = t.get("category", "Work")
        categories[cat] = categories.get(cat, 0) + 1

    lines += [
        "",
        "--- WEEKLY STATS ---",
        f"Active days: {len(plans)}",
        f"Average completion: {avg_completion}%",
        f"Average energy: {avg_energy}/5",
        f"Total tasks: {total_tasks} ({completed_tasks} completed)",
        f"Top category: {max(categories, key=categories.get) if categories else 'N/A'}",
        f"Category breakdown: {json.dumps(categories)}",
    ]

    return "\n".join(lines)


def _extract_json(raw: str) -> dict:
    """Strip markdown fences and extract a JSON object from the streamed text."""
    text = raw.strip()
    # Remove ```json ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Brace-match to find the outermost JSON object
    start = text.find("{")
    if start == -1:
        return {}
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    break
    return {}


def _default_result(theme: str = "Your Week in Review") -> dict:
    return {
        "theme": theme,
        "narrative": "## Your Week\n\nNarrative could not be generated. Please try again.",
        "key_insight": "Review your week's data to identify patterns.",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def stream_weekly_narrative(
    week_start: str,
    week_end: str,
) -> Generator[str, None, None]:
    """
    Stream the weekly narrative text token-by-token.

    Yields each streamed text delta.  After iteration the full accumulated
    text is available via the `accumulated` attribute of the returned
    generator — but because generators don't support attributes, callers
    that need the final parsed result should use `run_weekly_narrator()`
    instead, which collects the stream internally.

    Usage (Streamlit streaming display):
        placeholder = st.empty()
        display = ""
        for chunk in stream_weekly_narrative(ws, we):
            display += chunk
            placeholder.markdown(display + "▌")
        placeholder.markdown(display)
    """
    plans = get_plans_for_week(week_start, week_end)
    reflections = get_reflections_for_week(week_start, week_end)
    tasks = get_tasks_for_week(week_start, week_end)

    context = _build_weekly_context(week_start, week_end, plans, reflections, tasks)

    user_message = (
        f"Please write a weekly review for the week of {week_start} to {week_end}.\n\n"
        f"{context}\n\n"
        "Return ONLY valid JSON matching the schema in your instructions."
    )

    with client.messages.stream(
        model=MODEL,
        max_tokens=1500,
        system=WEEKLY_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def run_weekly_narrator(
    week_start: str,
    week_end: str,
    on_chunk: Optional[callable] = None,
) -> dict:
    """
    Run the Weekly Narrator for the given week and return the parsed result.

    Parameters
    ----------
    week_start : ISO date string (Monday)
    week_end   : ISO date string (Sunday)
    on_chunk   : optional callback(str) called for each streamed token — use
                 this to update a Streamlit placeholder in real time.

    Returns
    -------
    dict with keys: theme, narrative, key_insight
    """
    accumulated = ""

    try:
        for chunk in stream_weekly_narrative(week_start, week_end):
            accumulated += chunk
            if on_chunk:
                on_chunk(accumulated)
    except Exception as exc:
        return {**_default_result(), "_error": str(exc)}

    parsed = _extract_json(accumulated)

    return {
        "theme": parsed.get("theme") or "Your Week in Review",
        "narrative": parsed.get("narrative") or accumulated or _default_result()["narrative"],
        "key_insight": parsed.get("key_insight") or _default_result()["key_insight"],
    }
