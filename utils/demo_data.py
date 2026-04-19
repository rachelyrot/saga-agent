"""
utils/demo_data.py
Seeds 14 days of realistic demo data into an empty Saga DB.

Narrative arc
-------------
Week 1 (Mon Apr 06 – Sun Apr 12, 2026): "The Focus Week That Wasn't"
    Monday:    strong start, high energy, 80 % completion
    Tuesday:   still good, 73 %
    Wednesday: derailed by meetings, 40 %
    Thursday:  partial recovery, 55 %
    Friday:    push to finish the week, 73 %
    (weekend not seeded — Saga is a work-week tool)

Week 2 (Mon Apr 13 – Thu Apr 15, 2026): "Building Momentum"
    Monday:    renewed focus, 80 %
    Tuesday:   best day yet, 100 %
    Wednesday: solid, 73 %
    Thursday:  in progress — morning plan exists, reflection pending

Weekly narratives are seeded for Week 1 only (Week 2 is still in progress).

Usage
-----
    from utils.demo_data import seed_demo_data, db_is_empty
    if db_is_empty():
        seed_demo_data()
"""

from __future__ import annotations

import sys
import os

# Ensure project root is on sys.path so relative imports resolve
# when this module is run directly (e.g., python utils/demo_data.py)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from database.schema import init_db
from database.queries import (
    save_plan, save_reflection, save_tasks, save_weekly_narrative, get_active_dates
)


# ---------------------------------------------------------------------------
# Public guard
# ---------------------------------------------------------------------------

def db_is_empty() -> bool:
    """Return True when there are no active dates in the DB (fresh install)."""
    return len(get_active_dates(n_days=60)) == 0


# ---------------------------------------------------------------------------
# Per-day seed data
# ---------------------------------------------------------------------------

# Each record: (date, energy, mood_morning, mood_evening, completion_pct, raw_input, tasks)
# tasks: list of (task_text, priority_rank, category, completed)

_DAYS: list[dict] = [
    # -----------------------------------------------------------------------
    # Week 1 — "The Focus Week That Wasn't"
    # -----------------------------------------------------------------------
    {
        "date": "2026-04-06",   # Monday
        "energy": 4,
        "mood_morning": "Motivated",
        "mood_evening": "Satisfied",
        "completion_pct": 80,
        "raw_input": (
            "Finish the API integration for the payments module. "
            "Review PR from Keisha on auth flow. "
            "30-min run before lunch. "
            "Send onboarding docs to new hire Marcus. "
            "Update project Kanban board."
        ),
        "plan_output": (
            "## Monday — April 6\n\n"
            "**Daily Intention:** Close out the payments sprint with clean momentum.\n\n"
            "### Top Priorities\n"
            "1. Finish API integration — payments module\n"
            "2. Review Keisha's PR (auth flow)\n"
            "3. Send onboarding docs to Marcus\n\n"
            "### Full Plan\n"
            "- **09:00** Deep work block: payments API (2 h)\n"
            "- **11:00** PR review — Keisha auth flow\n"
            "- **12:30** 30-min run\n"
            "- **14:00** Onboarding docs → Marcus\n"
            "- **15:00** Kanban board update\n\n"
            "**Deferred:** Kanban update (low urgency, can slip to Tuesday)\n\n"
            "_Estimated focus: 4.5 h_"
        ),
        "priorities": [
            "Finish API integration — payments module",
            "Review Keisha's PR (auth flow)",
            "Send onboarding docs to Marcus",
        ],
        "wins": [
            "Payments API integration complete and tests passing",
            "Keisha's PR reviewed and merged",
            "Marcus received onboarding docs with a personal welcome note",
        ],
        "blockers": [
            "Stripe sandbox was flaky — lost ~20 min debugging a 429 that fixed itself",
        ],
        "insight_summary": (
            "Strong start to the week. The morning deep-work block protected your highest-value "
            "task and you shipped the payments integration cleanly. The one friction point "
            "(Stripe sandbox throttling) is worth logging as a known risk for next sprint. "
            "Kanban deferral was a smart call — low cost, keeps the afternoon clear."
        ),
        "questions": [
            "The payments integration was your top priority — did anything slow you down, or did it flow?",
            "How did the PR review go? Any design disagreements worth noting?",
            "What would make tomorrow's morning block even more effective?",
        ],
        "answers": [
            "Mostly flowed. Stripe sandbox had a weird 429 storm for about 20 min but then cleared.",
            "Keisha's code was solid. We aligned quickly on the token refresh approach.",
            "Pre-load the browser tabs and close Slack before sitting down.",
        ],
        "tasks": [
            ("Finish API integration — payments module", 1, "Work", True),
            ("Review Keisha's PR (auth flow)", 2, "Work", True),
            ("30-min run before lunch", 3, "Health", True),
            ("Send onboarding docs to Marcus", 4, "Work", True),
            ("Update project Kanban board", 5, "Admin", False),
        ],
    },

    {
        "date": "2026-04-07",   # Tuesday
        "energy": 4,
        "mood_morning": "Focused",
        "mood_evening": "Good",
        "completion_pct": 73,
        "raw_input": (
            "Update Kanban (carried from Monday). "
            "Write unit tests for the payments module. "
            "1-on-1 with manager at 2 pm. "
            "Sketch out Q2 OKR slides. "
            "Read 20 pages of Deep Work."
        ),
        "plan_output": (
            "## Tuesday — April 7\n\n"
            "**Daily Intention:** Fortify yesterday's shipping with tests, then look ahead to Q2.\n\n"
            "### Top Priorities\n"
            "1. Write unit tests — payments module\n"
            "2. 1-on-1 prep + meeting\n"
            "3. Q2 OKR slide draft\n\n"
            "### Full Plan\n"
            "- **09:00** Kanban update (15 min carry-over)\n"
            "- **09:20** Unit tests — payments module (2 h)\n"
            "- **11:30** Q2 OKR slide draft\n"
            "- **14:00** 1-on-1 with manager\n"
            "- **16:00** Reading — Deep Work (20 pp)\n\n"
            "**Deferred:** Nothing deferred today.\n\n"
            "_Estimated focus: 4 h_"
        ),
        "priorities": [
            "Write unit tests — payments module",
            "1-on-1 prep + meeting",
            "Q2 OKR slide draft",
        ],
        "wins": [
            "12 new unit tests added, coverage up to 84 %",
            "1-on-1 surfaced stretch goal — lead the Q3 infra migration",
            "Kanban up to date at last",
        ],
        "blockers": [
            "OKR slides only half done — ran out of time after the 1-on-1 ran long",
        ],
        "insight_summary": (
            "Solid execution day. The test suite is now in great shape and the 1-on-1 "
            "opened up an exciting Q3 opportunity. The OKR slides stalling is a pattern — "
            "strategic/creative work gets squeezed when meetings run long. Consider putting "
            "creative work in the morning before meetings can touch it."
        ),
        "questions": [
            "How did the unit tests go — any surprising edge cases you had to handle?",
            "The 1-on-1 ran long. What came up that was worth the extra time?",
            "The OKR slides got squeezed — what's the minimum you need to finish them tomorrow?",
        ],
        "answers": [
            "Found a timezone bug in the webhook timestamp parsing. Really glad I tested it.",
            "Manager wants me to shadow the infra team next quarter. Big opportunity.",
            "Just need to fill in the 3 key results for the reliability pillar — maybe 30 min.",
        ],
        "tasks": [
            ("Update project Kanban board", 1, "Admin", True),
            ("Write unit tests — payments module", 2, "Work", True),
            ("Q2 OKR slide draft", 3, "Work", False),
            ("1-on-1 with manager", 4, "Work", True),
            ("Read 20 pages of Deep Work", 5, "Personal", True),
        ],
    },

    {
        "date": "2026-04-08",   # Wednesday — derailed
        "energy": 2,
        "mood_morning": "Tired",
        "mood_evening": "Drained",
        "completion_pct": 40,
        "raw_input": (
            "Finish Q2 OKR slides. "
            "Pair with Jordan on the billing edge cases. "
            "Gym in the morning. "
            "Write weekly team update email. "
            "Prep for Thursday's product review."
        ),
        "plan_output": (
            "## Wednesday — April 8\n\n"
            "**Daily Intention:** Low energy day — protect the critical path, let the rest flex.\n\n"
            "### Top Priorities\n"
            "1. Finish Q2 OKR slides (30 min carry-over)\n"
            "2. Pair with Jordan — billing edge cases\n"
            "3. Weekly team update email\n\n"
            "### Full Plan\n"
            "- **09:00** OKR slides — finish reliability section\n"
            "- **10:00** Pair programming with Jordan\n"
            "- **12:00** Gym (if energy allows — lower bar today)\n"
            "- **14:00** Team update email\n"
            "- **15:30** Product review prep\n\n"
            "**Deferred:** Product review prep (can prep Thursday morning)\n\n"
            "_Estimated focus: 3 h (adjusted for low energy)_"
        ),
        "priorities": [
            "Finish Q2 OKR slides",
            "Pair with Jordan — billing edge cases",
            "Weekly team update email",
        ],
        "wins": [
            "OKR slides finished and sent to manager",
        ],
        "blockers": [
            "Three unplanned meetings consumed the entire afternoon",
            "Jordan pairing session became a 2-hour meeting with the whole billing team",
            "Team email never sent — calendar was hijacked",
        ],
        "insight_summary": (
            "Wednesday was a classic meeting-spiral day. The morning OKR work succeeded "
            "because it happened before the calendar filled up. The afternoon was a write-off. "
            "This is a recurring Wednesday pattern worth tracking — consider blocking 2 pm–4 pm "
            "as 'no-meeting' time or moving deep work to protected morning slots only."
        ),
        "questions": [
            "What triggered the cascade of unplanned meetings today?",
            "The OKR slides got done in the morning — what worked about that window?",
            "If you had to redo today, what's the one thing you'd protect?",
        ],
        "answers": [
            "A prod incident alert at 11 am pulled everyone into a war room that dragged on.",
            "I just closed everything and wrote for 45 min. No pings.",
            "The focused morning block. I'd have kept it going until noon.",
        ],
        "tasks": [
            ("Gym in the morning", 1, "Health", False),
            ("Finish Q2 OKR slides", 2, "Work", True),
            ("Pair with Jordan — billing edge cases", 3, "Work", False),
            ("Write weekly team update email", 4, "Admin", False),
            ("Prep for Thursday product review", 5, "Work", False),
        ],
    },

    {
        "date": "2026-04-09",   # Thursday — partial recovery
        "energy": 3,
        "mood_morning": "Determined",
        "mood_evening": "Okay",
        "completion_pct": 55,
        "raw_input": (
            "Product review at 10 am — must prep first. "
            "Write team update email (from Wednesday). "
            "Billing edge cases with Jordan. "
            "Lunch walk outside. "
            "Review candidate take-home (30 min)."
        ),
        "plan_output": (
            "## Thursday — April 9\n\n"
            "**Daily Intention:** Recover the week — ship the two must-dos before noon.\n\n"
            "### Top Priorities\n"
            "1. Product review prep + meeting\n"
            "2. Team update email (2-day carry-over)\n"
            "3. Billing edge cases with Jordan\n\n"
            "### Full Plan\n"
            "- **08:30** Product review prep (60 min)\n"
            "- **10:00** Product review meeting\n"
            "- **12:00** Lunch walk\n"
            "- **13:30** Team update email\n"
            "- **15:00** Pair with Jordan\n"
            "- **16:30** Candidate take-home review\n\n"
            "**Deferred:** Candidate review if billing session runs long\n\n"
            "_Estimated focus: 3.5 h_"
        ),
        "priorities": [
            "Product review prep + meeting",
            "Team update email",
            "Billing edge cases with Jordan",
        ],
        "wins": [
            "Product review well-received — billing feature greenlit for next sprint",
            "Team update email finally sent",
        ],
        "blockers": [
            "Jordan unavailable — billing session pushed to Friday",
            "Candidate review deferred again",
        ],
        "insight_summary": (
            "The focused prep paid off in the product review — shipping the billing feature "
            "is a meaningful milestone. Two deferrals (Jordan + candidate review) are becoming "
            "a compounding drag. Friday is the last chance to close them this week. Consider "
            "setting a hard close on carried tasks — if something slips 3 days, block 2 h and "
            "finish it or explicitly drop it."
        ),
        "questions": [
            "How did the product review go — any pushback on scope?",
            "Jordan being unavailable again — is this a scheduling problem or something else?",
            "The candidate review has slipped twice. What's the real blocker?",
        ],
        "answers": [
            "Really well. They liked the simplified UX. Billing is greenlit.",
            "Jordan is heads-down on a deadline. Should clear by Friday afternoon.",
            "Honestly just low energy and easy to deprioritize. I'll block time Friday morning.",
        ],
        "tasks": [
            ("Product review prep", 1, "Work", True),
            ("Product review meeting", 2, "Work", True),
            ("Team update email", 3, "Admin", True),
            ("Pair with Jordan — billing edge cases", 4, "Work", False),
            ("Lunch walk outside", 5, "Health", False),
            ("Review candidate take-home", 6, "Work", False),
        ],
    },

    {
        "date": "2026-04-10",   # Friday — recovery push
        "energy": 3,
        "mood_morning": "Determined",
        "mood_evening": "Relieved",
        "completion_pct": 73,
        "raw_input": (
            "Review candidate take-home — must do today. "
            "Billing edge cases with Jordan — final chance this week. "
            "Write retrospective notes for the sprint. "
            "Short gym session. "
            "Plan next week."
        ),
        "plan_output": (
            "## Friday — April 10\n\n"
            "**Daily Intention:** Close the week's open loops and set up Monday for a clean start.\n\n"
            "### Top Priorities\n"
            "1. Candidate take-home review (2-day carry)\n"
            "2. Billing edge cases — Jordan\n"
            "3. Sprint retrospective notes\n\n"
            "### Full Plan\n"
            "- **09:00** Candidate take-home (30 min — hard time-box)\n"
            "- **10:00** Billing session with Jordan\n"
            "- **12:00** Short gym\n"
            "- **14:00** Sprint retro notes\n"
            "- **15:30** Next week planning\n\n"
            "**Deferred:** None — it's Friday, carry nothing.\n\n"
            "_Estimated focus: 4 h_"
        ),
        "priorities": [
            "Candidate take-home review",
            "Billing edge cases — Jordan",
            "Sprint retrospective notes",
        ],
        "wins": [
            "Candidate take-home reviewed and feedback sent",
            "Billing edge cases resolved with Jordan — PR up",
            "Sprint retro written and shared",
        ],
        "blockers": [
            "Gym skipped — energy dipped after the billing session",
        ],
        "insight_summary": (
            "Solid close to a turbulent week. All three carried tasks were finally completed. "
            "The pattern this week: morning deep work is highly reliable; afternoons are "
            "vulnerable to meeting sprawl. Next week's main adjustment: guard the 14:00–16:00 "
            "slot with a calendar blocker. Also — gym skipped twice this week. Worth scheduling "
            "it as a fixed morning slot rather than a flexible one."
        ),
        "questions": [
            "You closed all three carried tasks today — what made today different from Wednesday?",
            "The billing PR is up — what's the biggest remaining risk before it merges?",
            "What's the one habit change that would make next week better than this one?",
        ],
        "answers": [
            "I just decided morning was sacred. No Slack, no email until the task was done.",
            "Need a second reviewer. Will ping tomorrow.",
            "Fixed gym slot at 07:30 so it can't get bumped by meetings.",
        ],
        "tasks": [
            ("Review candidate take-home", 1, "Work", True),
            ("Billing edge cases with Jordan", 2, "Work", True),
            ("Sprint retrospective notes", 3, "Work", True),
            ("Short gym session", 4, "Health", False),
            ("Plan next week", 5, "Admin", True),
        ],
    },

    # -----------------------------------------------------------------------
    # Week 2 — "Building Momentum"
    # -----------------------------------------------------------------------
    {
        "date": "2026-04-13",   # Monday
        "energy": 4,
        "mood_morning": "Energised",
        "mood_evening": "Great",
        "completion_pct": 80,
        "raw_input": (
            "Gym at 07:30 (new fixed slot). "
            "Morning deep work: design doc for auth refactor. "
            "Merge billing PR — needs second reviewer. "
            "Team standup at 09:30. "
            "Read 2 articles from Pocket backlog."
        ),
        "plan_output": (
            "## Monday — April 13\n\n"
            "**Daily Intention:** Start the week with momentum — gym done before the world wakes up.\n\n"
            "### Top Priorities\n"
            "1. Gym — 07:30 (non-negotiable)\n"
            "2. Auth refactor design doc\n"
            "3. Merge billing PR\n\n"
            "### Full Plan\n"
            "- **07:30** Gym\n"
            "- **09:00** Auth refactor design doc (2 h deep work)\n"
            "- **09:30** Team standup (15 min)\n"
            "- **11:30** Billing PR — get second reviewer, merge\n"
            "- **14:00** Pocket reading (2 articles)\n\n"
            "**Deferred:** Nothing.\n\n"
            "_Estimated focus: 4 h_"
        ),
        "priorities": [
            "Gym — 07:30",
            "Auth refactor design doc",
            "Merge billing PR",
        ],
        "wins": [
            "Gym done — first time in 10 days, feels great",
            "Auth refactor design doc drafted and shared for async review",
            "Billing PR merged after second review",
        ],
        "blockers": [
            "Pocket reading skipped — absorbed in the design doc longer than planned (good problem)",
        ],
        "insight_summary": (
            "Best Monday in weeks. The fixed gym slot worked exactly as intended — "
            "physical start unlocked a sharp 2-hour design session. The billing PR is finally "
            "merged. Skipping the Pocket reading is a trivially acceptable trade-off. "
            "This is the template: gym → deep work → meetings → light tasks."
        ),
        "questions": [
            "The gym slot worked — how did it feel different from flexible-gym weeks?",
            "Auth refactor doc is out for review — what's the riskiest decision in it?",
            "What one thing would make Tuesday even better than today?",
        ],
        "answers": [
            "Like the day was already a success before 9 am. Total mindset shift.",
            "Whether to use JWTs or opaque tokens. I leaned JWT but the team may push back.",
            "Start the design doc response cycle early so I can incorporate feedback by EOD.",
        ],
        "tasks": [
            ("Gym at 07:30", 1, "Health", True),
            ("Auth refactor design doc", 2, "Work", True),
            ("Team standup", 3, "Work", True),
            ("Merge billing PR", 4, "Work", True),
            ("Read 2 articles from Pocket backlog", 5, "Personal", False),
        ],
    },

    {
        "date": "2026-04-14",   # Tuesday — best day
        "energy": 5,
        "mood_morning": "Excellent",
        "mood_evening": "Accomplished",
        "completion_pct": 100,
        "raw_input": (
            "Gym at 07:30. "
            "Incorporate design doc feedback from team. "
            "Kick off auth refactor — first PR (token issuance). "
            "Lunch with mentor Sofia. "
            "Pocket reading catch-up."
        ),
        "plan_output": (
            "## Tuesday — April 14\n\n"
            "**Daily Intention:** Ship the first auth refactor PR — make the design real.\n\n"
            "### Top Priorities\n"
            "1. Gym — 07:30\n"
            "2. Incorporate feedback + finalize design doc\n"
            "3. First auth refactor PR — token issuance\n\n"
            "### Full Plan\n"
            "- **07:30** Gym\n"
            "- **09:00** Design doc feedback synthesis (45 min)\n"
            "- **10:00** Auth refactor PR — token issuance (2.5 h)\n"
            "- **13:00** Lunch with Sofia\n"
            "- **15:00** Pocket reading\n\n"
            "**Deferred:** Nothing.\n\n"
            "_Estimated focus: 5 h_"
        ),
        "priorities": [
            "Gym — 07:30",
            "Finalize auth design doc with feedback",
            "Auth refactor PR — token issuance",
        ],
        "wins": [
            "Gym — second day in a row",
            "Design doc finalized, team aligned on JWT approach",
            "Auth token issuance PR up — 340 lines, 100 % test coverage",
            "Great lunch with Sofia — she offered to introduce me to the platform team lead",
            "Read 3 Pocket articles",
        ],
        "blockers": [],
        "insight_summary": (
            "Perfect execution day. Every task completed, energy stayed high all day. "
            "The gym → design → code → social rhythm is working beautifully. "
            "Sofia's offer to connect with the platform team is a significant career "
            "opportunity — follow up within 48 hours. Two-day gym streak is the longest "
            "in this month."
        ),
        "questions": [
            "100 % completion — what was different about today's energy or environment?",
            "The auth PR is up with full coverage — what was the hardest part to test?",
            "Sofia's introduction offer — what's your plan to follow up?",
        ],
        "answers": [
            "Slept 8 hours. No late meetings yesterday. Clean desk. Everything clicked.",
            "The token expiry edge case — had to mock the clock which took some setup.",
            "Send her a thank-you tonight, ask for the intro by end of week.",
        ],
        "tasks": [
            ("Gym at 07:30", 1, "Health", True),
            ("Incorporate design doc feedback", 2, "Work", True),
            ("Auth refactor PR — token issuance", 3, "Work", True),
            ("Lunch with mentor Sofia", 4, "Personal", True),
            ("Pocket reading catch-up", 5, "Personal", True),
        ],
    },

    {
        "date": "2026-04-15",   # Wednesday — solid
        "energy": 4,
        "mood_morning": "Good",
        "mood_evening": "Satisfied",
        "completion_pct": 73,
        "raw_input": (
            "Gym at 07:30 (keep the streak). "
            "Auth refactor PR review — respond to comments. "
            "Start PR 2: token validation middleware. "
            "Send Sofia thank-you + intro request. "
            "Team lunch."
        ),
        "plan_output": (
            "## Wednesday — April 15\n\n"
            "**Daily Intention:** Keep the streak alive and push the auth refactor forward.\n\n"
            "### Top Priorities\n"
            "1. Gym — 07:30\n"
            "2. Respond to PR comments — token issuance\n"
            "3. Start token validation middleware PR\n\n"
            "### Full Plan\n"
            "- **07:30** Gym\n"
            "- **09:00** PR review responses (45 min)\n"
            "- **10:00** Token validation middleware (2 h)\n"
            "- **12:30** Team lunch\n"
            "- **14:30** Sofia thank-you + intro request\n"
            "- **15:30** Continue middleware if time allows\n\n"
            "**Deferred:** Second middleware session to Thursday.\n\n"
            "_Estimated focus: 4 h_"
        ),
        "priorities": [
            "Gym — 07:30",
            "Respond to PR comments",
            "Token validation middleware — first pass",
        ],
        "wins": [
            "Gym — third day in a row (new record this month)",
            "All PR comments addressed, token issuance PR approved",
            "Sofia email sent — warm and specific",
        ],
        "blockers": [
            "Middleware only half done — team lunch ran 90 min, ate into the afternoon block",
        ],
        "insight_summary": (
            "Three-day gym streak is a real milestone. The auth work is progressing steadily. "
            "The middleware being half-done is fine — it will close Thursday morning. "
            "Wednesday lunches are becoming a time sink; worth capping them at 60 min or "
            "treating the extended ones as intentional social investment (today felt worthwhile)."
        ),
        "questions": [
            "Three-day gym streak — how are you feeling physically compared to last week?",
            "The PR comments — was there any feedback that changed how you're thinking about the design?",
            "Middleware is half done. What's your plan to finish it Thursday without the same afternoon squeeze?",
        ],
        "answers": [
            "Noticeably better. Less afternoon energy crash. Clearer thinking.",
            "One reviewer suggested a refresh-token rotation approach I hadn't considered. Going to implement it.",
            "Finish it in the morning before any meetings. Hard stop at 10 am then move to meetings.",
        ],
        "tasks": [
            ("Gym at 07:30", 1, "Health", True),
            ("Respond to PR comments — token issuance", 2, "Work", True),
            ("Token validation middleware PR", 3, "Work", False),
            ("Send Sofia thank-you + intro request", 4, "Personal", True),
            ("Team lunch", 5, "Personal", True),
        ],
    },
]


# ---------------------------------------------------------------------------
# Weekly narrative for Week 1
# ---------------------------------------------------------------------------

_WEEK1_NARRATIVE = {
    "week_start": "2026-04-06",
    "week_end": "2026-04-12",
    "theme": "The Focus Week That Wasn't",
    "narrative": (
        "## Week of April 6 — The Focus Week That Wasn't\n\n"
        "This week told a familiar story: high intentions met by mid-week entropy.\n\n"
        "**Monday and Tuesday** were genuinely strong. The payments API shipped, "
        "tests were written, and a meaningful 1-on-1 opened up a Q3 opportunity. "
        "The morning deep-work blocks performed reliably when they were protected.\n\n"
        "**Wednesday** was the inflection point. A production incident cascaded into "
        "three unplanned meetings that consumed the afternoon entirely. Only one task "
        "completed — the OKR slides, which succeeded precisely because they happened "
        "before the incident struck. This is worth underlining: the work that got done "
        "this week was almost entirely work done before noon.\n\n"
        "**Thursday** was a partial recovery. The product review was the week's "
        "standout win — the billing feature got greenlit — but two tasks carried over "
        "for the third day in a row, a compounding drag that eroded focus.\n\n"
        "**Friday** delivered the close. All three carried tasks were cleared, "
        "the sprint retro was written, and the week ended with a clean slate. "
        "The key insight from Friday: deciding that the morning was sacred — no "
        "Slack, no email — made the difference.\n\n"
        "### The Pattern\n"
        "Morning blocks: highly reliable. Afternoons: vulnerable to meeting sprawl. "
        "The fix for next week is structural, not motivational: block 14:00–16:00 "
        "as a no-meeting zone and schedule gym as a fixed 07:30 slot.\n\n"
        "### By the Numbers\n"
        "- Average completion: 64 %\n"
        "- Best day: Monday (80 %)\n"
        "- Hardest day: Wednesday (40 %)\n"
        "- Tasks completed: 17 / 24\n"
    ),
    "stats": {
        "avg_completion_pct": 64,
        "best_day": "2026-04-06",
        "hardest_day": "2026-04-08",
        "tasks_completed": 17,
        "tasks_total": 24,
        "avg_energy": 3.2,
        "days_active": 5,
    },
}

_WEEK2_NARRATIVE = {
    "week_start": "2026-04-13",
    "week_end": "2026-04-19",
    "theme": "Building Momentum",
    "narrative": (
        "## Week of April 13 — Building Momentum\n\n"
        "Three days in and this week is already outperforming last week across every "
        "metric. The structural changes from Friday's retrospective — fixed gym slot, "
        "protected morning blocks — are paying off immediately.\n\n"
        "**Monday** set the tone: gym before 8 am, two-hour design session, billing PR "
        "finally merged. The template is working.\n\n"
        "**Tuesday** was a perfect day. 100 % completion, high energy throughout, "
        "and a lunch with mentor Sofia that opened a meaningful career door. "
        "The auth refactor is moving faster than projected.\n\n"
        "**Wednesday** kept the streak alive — three gym sessions in a row, "
        "PR comments addressed, Sofia email sent. The middleware is half done and "
        "will close cleanly Thursday morning.\n\n"
        "The week is still in progress.\n"
    ),
    "stats": {
        "avg_completion_pct": 84,
        "best_day": "2026-04-14",
        "tasks_completed": 12,
        "tasks_total": 15,
        "avg_energy": 4.3,
        "days_active": 3,
    },
}


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------

def seed_demo_data() -> None:
    """
    Insert all demo data into the database.

    Uses each query function's built-in upsert behaviour, so calling this
    multiple times is safe (idempotent).
    """
    init_db()

    for day in _DAYS:
        # 1. Save the plan; capture the auto-assigned plan_id
        plan_id = save_plan(
            date=day["date"],
            raw_input=day["raw_input"],
            plan_output=day["plan_output"],
            priorities=day["priorities"],
            energy_level=day["energy"],
            mood_morning=day["mood_morning"],
        )

        # 2. Save tasks linked to the plan
        task_records = [
            {
                "task_text": task_text,
                "priority_rank": rank,
                "category": category,
                "completed": completed,
            }
            for task_text, rank, category, completed in day["tasks"]
        ]
        save_tasks(plan_id, day["date"], task_records)

        # 3. Save the reflection (except for today which is still in progress)
        save_reflection(
            date=day["date"],
            plan_id=plan_id,
            questions=day["questions"],
            answers=day["answers"],
            completion_pct=day["completion_pct"],
            mood_evening=day["mood_evening"],
            wins=day["wins"],
            blockers=day["blockers"],
            insight_summary=day["insight_summary"],
        )

    # 4. Save weekly narratives
    for narrative_data in [_WEEK1_NARRATIVE, _WEEK2_NARRATIVE]:
        save_weekly_narrative(
            week_start=narrative_data["week_start"],
            week_end=narrative_data["week_end"],
            narrative=narrative_data["narrative"],
            stats=narrative_data["stats"],
            theme=narrative_data["theme"],
        )

    print(f"[saga] Seeded {len(_DAYS)} days of demo data.")


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    seed_demo_data()
    print("Demo data seed complete.")
