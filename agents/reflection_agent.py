"""
agents/reflection_agent.py
Two-phase Reflection Agent.

Phase 1 — generate_questions():
    Given today's plan context + completion %, returns 3 tailored questions as JSON.

Phase 2 — synthesize_reflection():
    Given those questions + the user's free-text answers, returns wins, blockers,
    insight_summary, and pattern_note as JSON.

Both phases share the same REFLECTION_SYSTEM cached block.
"""

import json
import re
from typing import Optional

from . import client, MODEL, REFLECTION_SYSTEM


# ---------------------------------------------------------------------------
# Internal JSON extractor (same pattern as morning_agent)
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """Extract the first JSON object from model response text."""
    text = text.strip()
    fenced = re.match(r"^```(?:json)?\s*([\s\S]+?)\s*```$", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(
                f"Reflection Agent: no JSON object found.\nResponse: {text[:500]}"
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
            f"Reflection Agent: could not parse JSON.\nResponse: {text[:500]}"
        ) from exc


# ---------------------------------------------------------------------------
# Phase 1 — Question generation
# ---------------------------------------------------------------------------

def generate_questions(
    plan_output: str,
    priorities: list[dict],
    completion_pct: int,
    date_str: str,
) -> list[dict]:
    """
    Phase 1: given the day's plan context and completion %, generate 3 reflection
    questions tailored to what actually happened.

    Parameters
    ----------
    plan_output : str
        The full_plan markdown text from this morning's plan.
    priorities : list[dict]
        The priorities list from this morning's plan.
    completion_pct : int
        0–100 estimate of how much the user got done today.
    date_str : str
        ISO date string, e.g. "2026-04-16".

    Returns
    -------
    list[dict]
        A list of 3 dicts, each with keys ``id`` (int) and ``text`` (str).
    """
    # Summarise priorities for the prompt
    task_lines = []
    for p in priorities:
        task_lines.append(f"  - [{p.get('category','Work')}] {p.get('task','')}")
    tasks_summary = "\n".join(task_lines) if task_lines else "  (no priorities recorded)"

    user_message = (
        f"PHASE 1 — QUESTION GENERATION\n\n"
        f"Date: {date_str}\n"
        f"Completion estimate: {completion_pct}%\n\n"
        f"Today's priorities:\n{tasks_summary}\n\n"
        f"Plan summary:\n{plan_output[:800]}\n\n"
        f"Generate 3 specific reflection questions for this day. "
        f"Return ONLY valid JSON matching the schema."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=REFLECTION_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text
    data = _extract_json(raw_text)

    questions = data.get("questions", [])

    # Normalise — ensure each item has id and text
    result = []
    for i, q in enumerate(questions[:3]):
        if isinstance(q, dict):
            result.append({
                "id": q.get("id", i + 1),
                "text": q.get("text", str(q)),
            })
        else:
            result.append({"id": i + 1, "text": str(q)})

    # Pad to exactly 3 if the model returned fewer
    defaults = [
        "What went well today that you want to remember?",
        "What got in the way, and why?",
        "What would you do differently tomorrow?",
    ]
    while len(result) < 3:
        idx = len(result)
        result.append({"id": idx + 1, "text": defaults[idx]})

    return result


# ---------------------------------------------------------------------------
# Phase 2 — Synthesis
# ---------------------------------------------------------------------------

def synthesize_reflection(
    questions: list[dict],
    answers: list[str],
    completion_pct: int,
    date_str: str,
    mood_evening: Optional[str] = None,
) -> dict:
    """
    Phase 2: given the reflection questions and the user's answers, synthesise
    wins, blockers, an insight summary, and a pattern note.

    Parameters
    ----------
    questions : list[dict]
        The 3 questions from Phase 1 (id + text).
    answers : list[str]
        The user's text answers, positionally aligned with questions.
    completion_pct : int
        0–100.
    date_str : str
        ISO date string.
    mood_evening : str | None
        Optional evening mood emoji/label.

    Returns
    -------
    dict with keys:
        wins (list[str]), blockers (list[str]),
        insight_summary (str), pattern_note (str | None)
    """
    qa_lines = []
    for i, q in enumerate(questions):
        answer = answers[i] if i < len(answers) else "(no answer)"
        qa_lines.append(f"Q{i+1}: {q.get('text', '')}")
        qa_lines.append(f"A{i+1}: {answer}")
        qa_lines.append("")
    qa_block = "\n".join(qa_lines)

    mood_line = f"\nEvening mood: {mood_evening}" if mood_evening else ""

    user_message = (
        f"PHASE 2 — SYNTHESIS\n\n"
        f"Date: {date_str}\n"
        f"Completion: {completion_pct}%"
        f"{mood_line}\n\n"
        f"Questions and answers:\n{qa_block}\n"
        f"Synthesise these answers into wins, blockers, insight_summary, and pattern_note. "
        f"Return ONLY valid JSON matching the schema."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=768,
        system=REFLECTION_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text
    data = _extract_json(raw_text)

    # Normalise
    data.setdefault("wins", [])
    data.setdefault("blockers", [])
    data.setdefault("insight_summary", "Reflection complete.")
    data.setdefault("pattern_note", None)

    return data
