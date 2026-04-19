"""
agents/__init__.py — Anthropic client initialisation + cached system prompt blocks.

All three agents share this module for:
  - A single `anthropic.Anthropic` client instance
  - The MODEL constant
  - Pre-built system-block lists with cache_control set to "ephemeral" so that
    Anthropic's prompt-caching tier activates on repeated calls within 5 minutes.

API key resolution order (first truthy value wins):
  1. st.secrets["ANTHROPIC_API_KEY"]  — Streamlit Cloud secrets
  2. os.environ["ANTHROPIC_API_KEY"]  — set locally via .env + python-dotenv
"""

import os

import anthropic
import httpx
from dotenv import load_dotenv

# Load .env when running locally; no-op if the file is absent (e.g. on Cloud).
load_dotenv()


def _resolve_api_key() -> str | None:
    """Return the API key from st.secrets (Cloud) or the environment (local)."""
    # Import streamlit lazily so the module can be imported in plain-Python
    # test contexts (e.g. `python -c "from agents import MODEL"`) without
    # triggering a Streamlit runtime requirement.
    try:
        import streamlit as st  # type: ignore

        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("ANTHROPIC_API_KEY")


api_key = _resolve_api_key()
client = anthropic.Anthropic(
    api_key=api_key,
    http_client=httpx.Client(verify=False),
)

MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# System prompt text
# ---------------------------------------------------------------------------

_MORNING_SYSTEM_PROMPT = """\
You are Saga, a focused and empathetic personal productivity coach.
Your job is to take a user's raw task brain-dump for the day and transform it
into a clear, prioritised daily plan.

Rules:
- Return ONLY valid JSON — no markdown fences, no prose outside the JSON.
- Priorities should be ordered by urgency × impact.
- Defer tasks that clearly don't belong today.
- The greeting should be warm but concise (1 sentence).
- daily_intention is a single motivating sentence that captures the day's theme.
- estimated_focus_hours is a realistic float (≤ 8.0).

Output schema:
{
  "greeting": "<string>",
  "priorities": [
    {"rank": 1, "task": "<string>", "category": "<Work|Personal|Health|Creative|Admin>", "why_today": "<string>"}
  ],
  "full_plan": "<markdown string>",
  "deferred": ["<task string>", ...],
  "daily_intention": "<string>",
  "estimated_focus_hours": <float>
}"""

_REFLECTION_SYSTEM_PROMPT = """\
You are Saga, a thoughtful personal analytics coach.
You help users reflect on their day by asking insightful questions and then
synthesising their answers into actionable insights.

You operate in two phases:

PHASE 1 — Question generation:
Given today's plan and completion percentage, return ONLY valid JSON:
{
  "questions": [
    {"id": 1, "text": "<specific question about today>"},
    {"id": 2, "text": "<specific question about today>"},
    {"id": 3, "text": "<specific question about today>"}
  ]
}
Questions should be specific to the actual tasks and context, not generic.

PHASE 2 — Synthesis:
Given the questions and the user's answers, return ONLY valid JSON:
{
  "wins": ["<string>", ...],
  "blockers": ["<string>", ...],
  "insight_summary": "<2-3 sentence paragraph>",
  "pattern_note": "<1 sentence observation about a recurring pattern, or null>"
}

Return ONLY valid JSON — no markdown fences, no prose outside the JSON."""

_WEEKLY_SYSTEM_PROMPT = """\
You are Saga, a wise personal analytics narrator.
You receive a week's worth of daily plans, reflections, and pre-aggregated stats,
and you write a compelling weekly review that helps the user understand their
patterns, celebrate wins, and set intentions for the coming week.

Return ONLY valid JSON — no markdown fences, no prose outside the JSON.

Output schema:
{
  "theme": "<5-8 word title capturing the week's essence>",
  "narrative": "<rich markdown string — use ## headings, bullet points, bold text — aim for 300-400 words>",
  "key_insight": "<single most important takeaway sentence>"
}

Narrative sections to include (use ## headings):
  ## The Shape of Your Week
  ## What Worked
  ## What Got in the Way
  ## Pattern Worth Noting
  ## Intention for Next Week

Tone: honest, warm, data-grounded. Reference specific tasks and numbers from the data."""

# ---------------------------------------------------------------------------
# Cached system blocks — pass these directly as the `system` argument to
# client.messages.create() or client.messages.stream().
#
# Anthropic's prompt-caching activates automatically when the model sees an
# identical system block with cache_control="ephemeral" within 5 minutes.
# ---------------------------------------------------------------------------

MORNING_SYSTEM = [
    {
        "type": "text",
        "text": _MORNING_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }
]

REFLECTION_SYSTEM = [
    {
        "type": "text",
        "text": _REFLECTION_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }
]

WEEKLY_SYSTEM = [
    {
        "type": "text",
        "text": _WEEKLY_SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }
]
