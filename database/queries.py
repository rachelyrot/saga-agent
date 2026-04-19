"""
database/queries.py
All read/write functions for Saga's 4 tables.
"""

import json
from typing import Optional
from .schema import get_connection


# ---------------------------------------------------------------------------
# daily_plans
# ---------------------------------------------------------------------------

def save_plan(date: str, raw_input: str, plan_output: str, priorities: list,
              energy_level: int, mood_morning: str) -> int:
    sql = """
        INSERT INTO daily_plans (date, raw_input, plan_output, priorities, energy_level, mood_morning)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            raw_input    = excluded.raw_input,
            plan_output  = excluded.plan_output,
            priorities   = excluded.priorities,
            energy_level = excluded.energy_level,
            mood_morning = excluded.mood_morning
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (date, raw_input, plan_output,
                                 json.dumps(priorities), energy_level, mood_morning))
        conn.commit()
        return cur.lastrowid


def get_plan(date: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM daily_plans WHERE date = ?", (date,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["priorities"] = json.loads(d["priorities"])
    return d


def get_recent_plans(n: int = 3) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_plans ORDER BY date DESC LIMIT ?", (n,)
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["priorities"] = json.loads(d["priorities"])
        result.append(d)
    return result


def get_plans_for_week(week_start: str, week_end: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_plans WHERE date BETWEEN ? AND ? ORDER BY date",
            (week_start, week_end),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["priorities"] = json.loads(d["priorities"])
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# reflections
# ---------------------------------------------------------------------------

def save_reflection(date: str, plan_id: Optional[int], questions: list, answers: list,
                    completion_pct: int, mood_evening: str, wins: list,
                    blockers: list, insight_summary: str) -> int:
    sql = """
        INSERT INTO reflections
            (date, plan_id, questions, answers, completion_pct, mood_evening,
             wins, blockers, insight_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            plan_id        = excluded.plan_id,
            questions      = excluded.questions,
            answers        = excluded.answers,
            completion_pct = excluded.completion_pct,
            mood_evening   = excluded.mood_evening,
            wins           = excluded.wins,
            blockers       = excluded.blockers,
            insight_summary = excluded.insight_summary
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (
            date, plan_id,
            json.dumps(questions), json.dumps(answers),
            completion_pct, mood_evening,
            json.dumps(wins), json.dumps(blockers),
            insight_summary,
        ))
        conn.commit()
        return cur.lastrowid


def get_reflection(date: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM reflections WHERE date = ?", (date,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    for key in ("questions", "answers", "wins", "blockers"):
        d[key] = json.loads(d[key])
    return d


def get_reflections_for_week(week_start: str, week_end: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM reflections WHERE date BETWEEN ? AND ? ORDER BY date",
            (week_start, week_end),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        for key in ("questions", "answers", "wins", "blockers"):
            d[key] = json.loads(d[key])
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# tasks
# ---------------------------------------------------------------------------

def save_tasks(plan_id: int, date: str, tasks: list[dict]) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE plan_id = ?", (plan_id,))
        conn.executemany(
            """INSERT INTO tasks (plan_id, date, task_text, priority_rank, category, completed)
               VALUES (:plan_id, :date, :task_text, :priority_rank, :category, :completed)""",
            [
                {
                    "plan_id": plan_id,
                    "date": date,
                    "task_text": t.get("task_text", ""),
                    "priority_rank": t.get("priority_rank", 0),
                    "category": t.get("category", "Work"),
                    "completed": int(t.get("completed", False)),
                }
                for t in tasks
            ],
        )
        conn.commit()


def get_tasks_for_date(date: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE date = ? ORDER BY priority_rank", (date,)
        ).fetchall()
    return [dict(r) for r in rows]


def mark_task_complete(task_id: int, completed: bool = True) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), task_id))
        conn.commit()


def get_tasks_for_week(week_start: str, week_end: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE date BETWEEN ? AND ? ORDER BY date, priority_rank",
            (week_start, week_end),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# weekly_narratives
# ---------------------------------------------------------------------------

def save_weekly_narrative(week_start: str, week_end: str, narrative: str,
                          stats: dict, theme: str) -> int:
    sql = """
        INSERT INTO weekly_narratives (week_start, week_end, narrative, stats, theme)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(week_start) DO UPDATE SET
            week_end  = excluded.week_end,
            narrative = excluded.narrative,
            stats     = excluded.stats,
            theme     = excluded.theme
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (week_start, week_end, narrative, json.dumps(stats), theme))
        conn.commit()
        return cur.lastrowid


def get_weekly_narrative(week_start: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM weekly_narratives WHERE week_start = ?", (week_start,)
        ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["stats"] = json.loads(d["stats"])
    return d


def get_all_weekly_narratives() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM weekly_narratives ORDER BY week_start DESC"
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["stats"] = json.loads(d["stats"])
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------

def get_active_dates(n_days: int = 30) -> list[str]:
    """Return dates that have both a plan and a reflection, most recent first."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT p.date FROM daily_plans p
               INNER JOIN reflections r ON p.date = r.date
               ORDER BY p.date DESC LIMIT ?""",
            (n_days,),
        ).fetchall()
    return [r["date"] for r in rows]
