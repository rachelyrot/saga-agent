"""
agents/morning_agent.py
Morning Agent — assembles the user's daily plan using Claude.

Public API
----------
run_morning_agent(raw_input, energy_level, mood, date_str, recent_reflections) -> dict
    Call the Claude API and return the parsed plan JSON.
    Raises RuntimeError if the API call fails or the JSON is malformed.
"""

import json
import re
from typing import Optional

from . import client, MODEL, MORNING_SYSTEM


def _build_user_message(
    raw_input: str,
    energy_level: int,
    mood: str,
    date_str: str,
    recent_reflections: Optional[list[dict]] = None,
) -> str:
    """Assemble the human-turn message for the morning agent."""
    lines = [
        f"Date: {date_str}",
        f"Energy level: {energy_level}/5",
        f"Mood: {mood}",
        "",
        "--- Task brain-dump ---",
        raw_input.strip(),
    ]

    if recent_reflections:
        lines += ["", "--- Recent reflections (last 3 days, newest first) ---"]
        for ref in recent_reflections[:3]:
            date_label = ref.get("date", "unknown date")
            summary = ref.get("insight_summary", "No summary available.")
            completion = ref.get("completion_pct", 0)
            lines.append(
                f"  {date_label}: {completion}% completion — {summary}"
            )

    lines += [
        "",
        "Please create my daily plan. Return ONLY valid JSON matching the schema.",
    ]

    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    """
    Extract the first JSON object from the model's response text.
    Handles cases where the model accidentally wraps output in a code fence.
    """
    # Strip markdown code fences if present
    text = text.strip()
    fenced = re.match(r"^```(?:json)?\s*([\s\S]+?)\s*```$", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Try to find the outermost JSON object via brace matching
        start = text.find("{")
        if start == -1:
            raise RuntimeError(
                f"Morning Agent: no JSON object found in response.\n"
                f"Response was: {text[:500]}"
            ) from exc

        depth = 0
        for i, ch in enumerate(text[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

        raise RuntimeError(
            f"Morning Agent: could not parse JSON from response.\n"
            f"Response was: {text[:500]}"
        ) from exc


def run_morning_agent(
    raw_input: str,
    energy_level: int,
    mood: str,
    date_str: str,
    recent_reflections: Optional[list[dict]] = None,
) -> dict:
    """
    Call the Morning Agent and return the parsed plan dict.

    Parameters
    ----------
    raw_input : str
        The user's free-form task brain-dump.
    energy_level : int
        1 (exhausted) … 5 (fully charged).
    mood : str
        Emoji or label describing the user's morning mood.
    date_str : str
        ISO date string for today, e.g. "2026-04-16".
    recent_reflections : list[dict] | None
        Up to 3 reflection dicts from the DB, newest first, for context.

    Returns
    -------
    dict with keys:
        greeting, priorities (list), full_plan (str),
        deferred (list), daily_intention (str), estimated_focus_hours (float)

    Raises
    ------
    RuntimeError
        If the API call fails or the response cannot be parsed as JSON.
    """
    user_message = _build_user_message(
        raw_input, energy_level, mood, date_str, recent_reflections
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=MORNING_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text
    plan = _extract_json(raw_text)

    # Validate required keys — provide defaults for optional fields so the UI
    # never crashes on a slightly malformed response.
    plan.setdefault("greeting", "Good morning!")
    plan.setdefault("priorities", [])
    plan.setdefault("full_plan", "")
    plan.setdefault("deferred", [])
    plan.setdefault("daily_intention", "Make today count.")
    plan.setdefault("estimated_focus_hours", 4.0)

    return plan
