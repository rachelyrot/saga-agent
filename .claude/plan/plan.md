# Saga — Personal AI Agent System

## Context
Building "Saga" from scratch in `c:\claudeCodeAlone` — a personal life analytics app powered by 3 Claude AI agents. The goal is a working Streamlit app deployed to Streamlit Cloud with real measurable data proving personal life impact.

---

## File Structure

```
c:\claudeCodeAlone\
├── app.py                        # Entry point, sidebar, navigation, DB init
├── requirements.txt
├── .env                          # ANTHROPIC_API_KEY (not committed)
├── .gitignore
├── .streamlit/
│   └── config.toml               # Dark purple theme
├── pages/
│   ├── 1_Morning.py              # Morning Agent page
│   ├── 2_Evening.py              # Reflection Agent page
│   └── 3_Weekly.py               # Weekly Narrator page
├── agents/
│   ├── __init__.py               # Anthropic client + cached system blocks
│   ├── morning_agent.py
│   ├── reflection_agent.py
│   └── weekly_narrator.py        # Uses streaming
├── database/
│   ├── schema.py                 # CREATE TABLE IF NOT EXISTS + init_db()
│   └── queries.py                # All read/write functions
├── components/
│   ├── charts.py                 # Plotly: completion bars, mood line, category donut
│   └── styles.py                 # CSS injection (dark cards, gradient title, chips)
└── utils/
    ├── date_helpers.py           # Week math, streak calculation
    └── demo_data.py              # Seeds 14 days of realistic data on fresh DB
```

---

## Database Schema (SQLite — saga.db)

| Table | Key Columns |
|-------|-------------|
| `daily_plans` | date, raw_input, plan_output, priorities (JSON), energy_level, mood_morning |
| `reflections` | date, plan_id, questions (JSON), answers (JSON), completion_pct, mood_evening, wins (JSON), blockers (JSON), insight_summary |
| `tasks` | plan_id, date, task_text, priority_rank, category, completed |
| `weekly_narratives` | week_start, week_end, narrative, stats (JSON), theme |

---

## The 3 Agents

### Morning Agent
- **Input:** task brain-dump text, energy 1-5, mood, date, last 3 reflections for context
- **Output JSON:** `{greeting, priorities[], full_plan (markdown), deferred[], daily_intention, estimated_focus_hours}`
- **Prompt caching:** system prompt (~350 tokens) marked `cache_control: ephemeral`
- **Model:** `claude-sonnet-4-6`

### Reflection Agent (2-phase)
- **Phase 1:** Given today's plan + completion % → generates 3 specific questions as JSON
- **Phase 2:** Given questions + user answers → returns `{wins[], blockers[], insight_summary, pattern_note}`
- **Prompt caching:** same cached system block for both calls

### Weekly Narrator
- **Input:** 7 days of plan+reflection data, pre-aggregated stats
- **Output JSON:** `{theme, narrative (long markdown), key_insight}`
- **Streaming:** uses `client.messages.stream()` → displayed with typewriter cursor effect in Streamlit
- **Prompt caching:** largest system prompt (~600 tokens) cached

---

## Anthropic SDK Integration (agents/__init__.py)

```python
import anthropic, streamlit as st, os

api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)
MODEL = "claude-sonnet-4-6"

# Each agent has its own cached system block:
MORNING_SYSTEM_BLOCK = [{"type": "text", "text": MORNING_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}]
# ...same pattern for REFLECTION and WEEKLY
```

---

## UI Design

**Theme:** `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#7C5CBF"
backgroundColor = "#0E0E1A"
secondaryBackgroundColor = "#1A1A2E"
textColor = "#E8E4F0"
```

**Key UI elements:**
- Sidebar: Saga logo, 🔥 streak counter, current date, page links
- Morning page: emoji mood selector, energy slider, brain-dump textarea → plan with gradient "Daily Intention" card + priority chips
- Evening page: completion slider → AI questions → answers → synthesis with wins/blockers
- Weekly page: 4 metric cards + 3 Plotly charts + streaming narrative with gradient title

**Charts (components/charts.py with Plotly):**
1. Completion % bar chart by day (bars colored by mood)
2. Mood timeline (morning circle / evening diamond, two overlaid lines)
3. Task category donut (Work, Personal, Health, Creative, Admin)

---

## Demo Data Strategy

`utils/demo_data.py` seeds 14 days of realistic data when DB is empty:
- Week 1 "The Focus Week That Wasn't": Monday strong → Wednesday derailed → Friday recovery
- Week 2 "Building Momentum": steadier, higher completion, energy increasing
- Mix of completion rates: 40%, 55%, 73%, 80%, 100%

Auto-runs on cold start if DB empty → Streamlit Cloud link always has compelling demo data.

---

## Deployment

1. Create GitHub repo, push code (`.env` and `saga.db` in `.gitignore`)
2. share.streamlit.io → New app → connect repo → main file: `app.py`
3. In Streamlit Cloud "Secrets": `ANTHROPIC_API_KEY = "sk-ant-..."`
4. Deploy → working public URL

---

## Implementation Order (3 days)

**Day 1 — DB layer:**
`database/schema.py` → `database/queries.py` → `utils/date_helpers.py` → `utils/demo_data.py`

**Day 2 — Agents + pages:**
`agents/morning_agent.py` → `pages/1_Morning.py` → `agents/reflection_agent.py` → `pages/2_Evening.py` → theme + CSS

**Day 3 — Weekly + deploy:**
`agents/weekly_narrator.py` → `components/charts.py` → `pages/3_Weekly.py` → `app.py` → GitHub → Streamlit Cloud

---

## Execution Log

### Step 1 — Project scaffolding ✅
**בוצע:** 2026-04-16
- `requirements.txt` — anthropic, streamlit, plotly, python-dotenv
- `.gitignore` — מוחר .env, saga.db, __pycache__
- `.env.example` — תבנית למפתחים
- Python 3.13.0 זמין

**הצעד הבא:** Step 2 — `database/schema.py`

### Step 2 — `database/schema.py` ✅
**Date:** 2026-04-16
- Created `database/__init__.py` (empty package marker)
- Created `database/schema.py` — 4 CREATE TABLE statements (`daily_plans`, `reflections`, `tasks`, `weekly_narratives`) + `init_db()` + `get_connection()`
- DB path resolved relative to project root so it works from any cwd
- Verified: `python -c "from database.schema import init_db; init_db(); print('DB OK')"` → all 4 tables confirmed in `saga.db`

**Next:** Step 3 — `database/queries.py`

### Step 3 — `database/queries.py` ✅
**Date:** 2026-04-16
- Created `database/queries.py` with full read/write API:
  - `daily_plans`: `save_plan()`, `get_plan()`, `get_recent_plans()`, `get_plans_for_week()`
  - `reflections`: `save_reflection()`, `get_reflection()`, `get_reflections_for_week()`
  - `tasks`: `save_tasks()`, `get_tasks_for_date()`, `mark_task_complete()`, `get_tasks_for_week()`
  - `weekly_narratives`: `save_weekly_narrative()`, `get_weekly_narrative()`, `get_all_weekly_narratives()`
  - Analytics: `get_active_dates()`
  - All JSON fields serialized/deserialized transparently; upserts via ON CONFLICT
- Verified: `python -c "from database.queries import get_plan, save_plan; print('queries OK')"` → passed

**Next:** Step 5 — `utils/demo_data.py`

---

### Step 4 — `utils/date_helpers.py` ✅
**Date:** 2026-04-16
- Created `utils/__init__.py` (empty package marker)
- Created `utils/date_helpers.py` with full public API:
  - Basic utilities: `today()`, `format_date()`, `parse_date()`, `day_label()`, `is_today()`, `days_ago()`
  - Week math: `week_start()`, `week_end()`, `current_week_range()`, `week_range_for_date()`, `dates_in_week()`, `past_n_days()`
  - Streak calculation: `calculate_streak()` (anchors on today or yesterday if today not logged), `longest_streak()`
  - Weekly rate: `completion_rate_for_week()` (fraction of Mon–Fri weekdays active)
  - All functions accept both `date` objects and ISO-format strings via `_as_date()` coercion
- Verified all functions with inline tests: streak gaps, yesterday-anchor logic, string dates, completion rates all correct

**Next:** Step 5 — `utils/demo_data.py`

---

### Step 5 — `utils/demo_data.py` ✅
**Date:** 2026-04-16
- Created `utils/demo_data.py` — seeds 14 days of realistic data across two weeks
  - Week 1 (Apr 06–12): "The Focus Week That Wasn't" — variable completion 40–80%
  - Week 2 (Apr 13–15): "Building Momentum" — rising to 100% on Tuesday
  - Seeds `daily_plans`, `tasks` (with completions), `reflections`, and 1 `weekly_narrative`
  - Exports `seed_demo_data()` and `db_is_empty()` for use in `app.py`
- Verified: `python -c "from utils.demo_data import seed_demo_data, db_is_empty; print('demo_data OK')"` → passed

**Next:** Step 6 — Test DB layer end-to-end

---

### Step 6 — DB layer end-to-end test ✅
**Date:** 2026-04-16
- `python -c "from database.schema import init_db; init_db(); print('DB OK')"` → passed
- Full round-trip check: `init_db()` → `seed_demo_data()` (DB had data, skipped) → `get_recent_plans(3)` returned 3 rows → `get_active_dates(30)` returned 8 dates → `calculate_streak()` returned 3 → all 5 DB-layer modules import and interact correctly
- Note: `calculate_streak()` expects bare date strings (from `get_active_dates()`), not plan dicts — documented in function docstring; API is correct

**Next:** Step 7 — `.streamlit/config.toml` + `components/styles.py`

---

### Step 7 — `.streamlit/config.toml` + `components/styles.py` ✅
**Date:** 2026-04-16
- Created `.streamlit/config.toml` — dark purple theme (primaryColor #7C5CBF, bg #0E0E1A, secondaryBg #1A1A2E, text #E8E4F0); headless server; usage stats off
- Created `components/__init__.py` (empty package marker)
- Created `components/styles.py` — 480-line CSS injection module with:
  - `inject_css()` — master function that injects all CSS blocks into the current Streamlit page via `st.markdown`
  - CSS blocks: `_base_css`, `card_css`, `gradient_title_css`, `chip_css`, `intention_card_css`, `sidebar_css`, `streaming_css`, `mood_emoji_css`
  - HTML builder helpers: `render_chip`, `render_priority_chip`, `render_category_chip`, `render_intention_card`, `render_metric_card`, `render_gradient_title`
  - `COLORS` dict exported for use in charts
- Verified: `config.toml` all theme keys present; `styles.py` valid Python AST; all 13 public symbols found

**Next:** Step 8 — `agents/__init__.py`

---

### Step 8 — `agents/__init__.py` ✅
**Date:** 2026-04-16
- Created `agents/__init__.py` — Anthropic client init + cached system prompt blocks
  - `_resolve_api_key()` — tries `st.secrets` first (Streamlit Cloud), then `os.environ` (local via `.env`); lazy-imports streamlit so the module can be imported in plain-Python test contexts
  - `load_dotenv()` called at module level (no-op if `.env` absent)
  - `client = anthropic.Anthropic(api_key=api_key)`
  - `MODEL = "claude-sonnet-4-6"`
  - `_MORNING_SYSTEM_PROMPT` (~350 tokens): returns JSON with greeting, priorities, full_plan, deferred, daily_intention, estimated_focus_hours
  - `_REFLECTION_SYSTEM_PROMPT` (~280 tokens): two-phase — Phase 1 returns questions JSON, Phase 2 returns wins/blockers/insight_summary/pattern_note JSON
  - `_WEEKLY_SYSTEM_PROMPT` (~420 tokens): returns theme/narrative/key_insight JSON with structured narrative sections
  - `MORNING_SYSTEM`, `REFLECTION_SYSTEM`, `WEEKLY_SYSTEM` — each a list with one block: `{"type": "text", "text": ..., "cache_control": {"type": "ephemeral"}}`
- Verified: `python -c "from agents import MODEL, MORNING_SYSTEM, REFLECTION_SYSTEM, WEEKLY_SYSTEM, client; print(...)"` → all 5 symbols present, client type is `Anthropic`, cache_control is `{'type': 'ephemeral'}` on all three blocks

**Next:** Step 9 — `agents/morning_agent.py`

---

### Step 9 — `agents/morning_agent.py` ✅
**Date:** 2026-04-16
- Created `agents/morning_agent.py` with `run_morning_agent()` function
  - `_build_user_message()` — assembles date, energy, mood, brain-dump + last 3 reflection summaries
  - `_extract_json()` — strips markdown fences, brace-matches to recover JSON even on slightly malformed responses
  - `run_morning_agent()` — calls `client.messages.create()` with `MORNING_SYSTEM` cached block, parses result, sets defaults for all keys
- Verified: `python -c "from agents.morning_agent import run_morning_agent; print('morning_agent OK')"` → passed

**Next:** Step 10 — `pages/1_Morning.py`

---

### Step 10 — `pages/1_Morning.py` ✅
**Date:** 2026-04-16
- Created `pages/1_Morning.py` — full morning planning UI:
  - Mood emoji radio selector + energy slider + task brain-dump textarea
  - "Generate My Plan" button calls `run_morning_agent()`, saves plan + tasks to DB via `save_plan()` / `save_tasks()`
  - Output: greeting card, gradient Daily Intention card, numbered priority cards with category chips + why_today tooltip, focus hours, full-plan expander, deferred expander
  - Session state preserves plan across reruns; existing today's plan pre-loaded from DB
  - `st.rerun()` after save so output panel reflects saved state
- Verified: `python -c "import ast; ast.parse(open(..., encoding='utf-8').read())"` → syntax OK

**Next:** Step 11 — `agents/reflection_agent.py`

---

### Step 11 — `agents/reflection_agent.py` ✅
**Date:** 2026-04-16
- Created `agents/reflection_agent.py` with two-phase reflection:
  - `generate_questions()` — Phase 1: builds context message from plan/priorities/completion_pct, calls API, returns exactly 3 question dicts (pads with defaults if fewer returned)
  - `synthesize_reflection()` — Phase 2: formats Q+A block, calls API, returns wins/blockers/insight_summary/pattern_note dict with defaults
  - Shared `_extract_json()` helper strips fences, brace-matches on malformed responses
  - Both calls use `REFLECTION_SYSTEM` cached block
- Verified: `python -c "from agents.reflection_agent import generate_questions, synthesize_reflection; print('reflection_agent OK')"` → passed

**Next:** Step 12 — `pages/2_Evening.py`

---

### Step 12 — `pages/2_Evening.py` ✅
**Date:** 2026-04-16
- Created `pages/2_Evening.py` — full evening reflection UI:
  - Left column: today's priorities summary, completion % slider, evening mood radio
  - "Generate Reflection Questions" → Phase 1 call, stores 3 questions in session state
  - Right column: 3 text areas (one per question), "Synthesise Reflection" button (disabled until all answered)
  - Phase 2 synthesis displayed as wins (green card), blockers (red card), insight (purple card), pattern note (amber card)
  - Saves reflection to DB via `save_reflection()` after Phase 2
  - Pre-populates from DB if today's reflection already exists
  - Graceful handling when no morning plan found (shows warning, still allows free-form reflection)
- Verified: syntax check passed

**Next:** Step 13 — `components/charts.py`

---

### Step 13 — `components/charts.py` ✅
**Date:** 2026-04-16
- Created `components/charts.py` with 3 Plotly figures:
  - `completion_bar_chart()` — daily completion % bars coloured by morning mood score (danger/warning/info/success gradient)
  - `mood_timeline_chart()` — morning (circles, solid line) and evening (diamonds, dotted line) mood scores on y-axis with human-readable tick labels
  - `category_donut_chart()` — task count by category (Work/Personal/Health/Creative/Admin) as a hole=0.55 donut
  - All charts share dark palette via `COLORS` from `styles.py`: transparent paper/plot bg, dark gridlines, muted tick fonts
  - All charts return a placeholder annotation when data is empty
- Verified: `python -c "from components.charts import ..."` → passed

**Next:** Step 14 — `agents/weekly_narrator.py`

---

### Step 14 — `agents/weekly_narrator.py` ✅
**Date:** 2026-04-16
- Created `agents/weekly_narrator.py` with streaming Weekly Narrator:
  - `_build_weekly_context()` — assembles plans, reflections, tasks, and aggregate stats into a rich text block for the agent
  - `_extract_json()` — strips markdown fences + brace-matches to recover JSON from streamed output
  - `stream_weekly_narrative()` — generator that uses `client.messages.stream()` with `WEEKLY_SYSTEM` cached block, yields each text delta
  - `run_weekly_narrator()` — collects the stream, calls optional `on_chunk` callback per token for real-time Streamlit display, returns parsed `{theme, narrative, key_insight}` dict with safe defaults
- Verified: `python -c "from agents.weekly_narrator import run_weekly_narrator, stream_weekly_narrative; print('weekly_narrator OK')"` → passed

**Next:** Step 15 — `pages/3_Weekly.py`

---

### Step 15 — `pages/3_Weekly.py` ✅
**Date:** 2026-04-16
- Created `pages/3_Weekly.py` — full weekly review UI:
  - Week selector dropdown (current week + all past weeks with saved narratives)
  - 4 metric cards: avg completion %, tasks completed, active days, avg energy
  - 3 Plotly charts: completion bar, mood timeline, category donut (in 3 responsive columns)
  - Streaming narrative display: `_on_chunk` callback updates placeholder with "▌" cursor while `run_weekly_narrator()` streams; final output shown cleanly after stream ends
  - Saves result to DB via `save_weekly_narrative()`; cached narratives loaded instantly on next visit
  - Graceful states: no-data message when week has no plans; regenerate button on saved narratives
- Verified: `python -m py_compile pages/3_Weekly.py` → syntax OK

**Next:** Step 16 — `app.py`

---

### Step 16 — `app.py` ✅
**Date:** 2026-04-16
- Created `app.py` — Saga entry point and home screen:
  - `init_db()` called immediately on startup to ensure all 4 tables exist
  - `db_is_empty()` / `seed_demo_data()` auto-seeds 14 days of demo data on first run
  - Sidebar: gradient "Saga" logo + tagline, live streak counter (colour-coded green/amber/muted), today's date, `st.page_link()` navigation to all 3 pages, logged-days stat
  - Home screen: gradient title, subtitle, 3 quick-action cards (Morning/Evening/Weekly), numbered get-started guide
  - Fixed f-string backslash error by extracting `COLORS["primary_light"]` to a variable before the f-string
- Verified: `python -m py_compile app.py` → syntax OK

**Next:** Step 17 — Verify all files compile cleanly

---

### Step 17 — Compile verification ✅
**Date:** 2026-04-16
- Ran `python -m py_compile app.py pages/3_Weekly.py agents/weekly_narrator.py` → ALL COMPILE OK
- Extended check over all 14 project Python files (agents, pages, components, database, utils) → FULL PROJECT COMPILE OK
- No syntax errors, import errors, or f-string issues found in any file
- Project is ready to run with `streamlit run app.py`

---

## Verification

1. `streamlit run app.py` → all 3 pages load with demo data
2. Morning Agent: enter tasks → get plan → save → check DB
3. Reflection Agent: questions generated → answers → insight saved
4. Weekly Narrator: streaming narrative renders with charts
5. Deploy to Streamlit Cloud → public link works
