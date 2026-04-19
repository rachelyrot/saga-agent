"""
date_helpers.py — Week math and streak calculation utilities for Saga.

Public API
----------
today() -> date
    Return today's date.

week_start(d) -> date
    Return the Monday of the ISO week containing `d`.

week_end(d) -> date
    Return the Sunday of the ISO week containing `d`.

current_week_range() -> tuple[date, date]
    (week_start, week_end) for the current ISO week.

week_range_for_date(d) -> tuple[date, date]
    (week_start, week_end) for the ISO week containing `d`.

dates_in_week(d) -> list[date]
    All 7 dates (Mon–Sun) for the ISO week containing `d`.

past_n_days(n, end_date=None) -> list[date]
    List of the last `n` calendar dates ending on `end_date` (inclusive).
    Defaults to today when `end_date` is None.

format_date(d, fmt="%Y-%m-%d") -> str
    Format a date object as a string.

parse_date(s, fmt="%Y-%m-%d") -> date
    Parse a date string into a date object.

day_label(d) -> str
    Human-readable short label, e.g. "Mon Apr 14".

is_today(d) -> bool
    True if `d` equals today's date.

days_ago(d) -> int
    How many calendar days ago `d` was (negative means future).

calculate_streak(active_dates) -> int
    Given a collection of date objects (or "%Y-%m-%d" strings) on which
    the user was active, return the length of the current consecutive streak
    ending on today (or yesterday if today not yet recorded).

longest_streak(active_dates) -> int
    Return the longest consecutive run in `active_dates`.

completion_rate_for_week(active_dates, reference_date=None) -> float
    Fraction of weekdays (Mon–Fri) in the ISO week of `reference_date`
    that appear in `active_dates`.  Returns 0.0–1.0.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, Union

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
DateLike = Union[date, str]


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _as_date(d: DateLike) -> date:
    """Coerce a date or ISO-format string to a date object."""
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)


# ---------------------------------------------------------------------------
# Basic date utilities
# ---------------------------------------------------------------------------

def today() -> date:
    """Return today's local date."""
    return date.today()


def format_date(d: DateLike, fmt: str = "%Y-%m-%d") -> str:
    """Format a date (or ISO string) using strftime format `fmt`."""
    return _as_date(d).strftime(fmt)


def parse_date(s: str, fmt: str = "%Y-%m-%d") -> date:
    """Parse a date string with the given format into a date object."""
    from datetime import datetime
    return datetime.strptime(s, fmt).date()


def day_label(d: DateLike) -> str:
    """Return a short human-readable label, e.g. 'Mon Apr 14'."""
    return _as_date(d).strftime("%a %b %#d")


def is_today(d: DateLike) -> bool:
    """Return True if `d` is today's date."""
    return _as_date(d) == date.today()


def days_ago(d: DateLike) -> int:
    """
    Return how many calendar days ago `d` was.
    Positive → past, 0 → today, negative → future.
    """
    return (date.today() - _as_date(d)).days


# ---------------------------------------------------------------------------
# Week math
# ---------------------------------------------------------------------------

def week_start(d: DateLike) -> date:
    """Return the Monday of the ISO week containing `d`."""
    d = _as_date(d)
    return d - timedelta(days=d.weekday())  # weekday() == 0 for Monday


def week_end(d: DateLike) -> date:
    """Return the Sunday of the ISO week containing `d`."""
    return week_start(d) + timedelta(days=6)


def current_week_range() -> tuple[date, date]:
    """Return (monday, sunday) for the current ISO week."""
    return week_range_for_date(date.today())


def week_range_for_date(d: DateLike) -> tuple[date, date]:
    """Return (monday, sunday) for the ISO week containing `d`."""
    ws = week_start(d)
    return ws, ws + timedelta(days=6)


def dates_in_week(d: DateLike) -> list[date]:
    """Return all 7 dates (Monday through Sunday) for the ISO week containing `d`."""
    ws = week_start(d)
    return [ws + timedelta(days=i) for i in range(7)]


def past_n_days(n: int, end_date: DateLike | None = None) -> list[date]:
    """
    Return a list of the last `n` calendar dates ending on `end_date`
    (inclusive).  Defaults to today when `end_date` is None.

    Example: past_n_days(3) on 2025-04-16 → [2025-04-14, 2025-04-15, 2025-04-16]
    """
    if n < 1:
        return []
    end = _as_date(end_date) if end_date is not None else date.today()
    start = end - timedelta(days=n - 1)
    return [start + timedelta(days=i) for i in range(n)]


# ---------------------------------------------------------------------------
# Streak calculation
# ---------------------------------------------------------------------------

def calculate_streak(active_dates: Iterable[DateLike]) -> int:
    """
    Calculate the current consecutive daily streak.

    The streak counts backward from today.  If today is not in
    `active_dates` but yesterday is, the streak still counts (the user
    hasn't had a chance to log today yet).  Once a gap is found the
    count stops.

    Returns 0 if there is no recent activity.
    """
    date_set: set[date] = {_as_date(d) for d in active_dates}

    if not date_set:
        return 0

    anchor = date.today()

    # Allow the streak to start from yesterday when today isn't logged yet
    if anchor not in date_set:
        anchor = anchor - timedelta(days=1)

    if anchor not in date_set:
        return 0

    streak = 0
    current = anchor
    while current in date_set:
        streak += 1
        current -= timedelta(days=1)

    return streak


def longest_streak(active_dates: Iterable[DateLike]) -> int:
    """
    Return the length of the longest consecutive daily run in `active_dates`.

    Returns 0 for an empty input.
    """
    date_set: set[date] = {_as_date(d) for d in active_dates}

    if not date_set:
        return 0

    sorted_dates = sorted(date_set)
    best = 1
    current_run = 1

    for i in range(1, len(sorted_dates)):
        gap = (sorted_dates[i] - sorted_dates[i - 1]).days
        if gap == 1:
            current_run += 1
            best = max(best, current_run)
        else:
            current_run = 1

    return best


# ---------------------------------------------------------------------------
# Weekly completion rate
# ---------------------------------------------------------------------------

def completion_rate_for_week(
    active_dates: Iterable[DateLike],
    reference_date: DateLike | None = None,
) -> float:
    """
    Return the fraction of weekdays (Mon–Fri) in the ISO week containing
    `reference_date` that appear in `active_dates`.

    Returns a float in [0.0, 1.0].  Returns 0.0 if reference week has no
    weekdays (shouldn't happen with ISO weeks, but guards against edge cases).
    """
    ref = _as_date(reference_date) if reference_date is not None else date.today()
    date_set: set[date] = {_as_date(d) for d in active_dates}

    ws = week_start(ref)
    weekdays = [ws + timedelta(days=i) for i in range(5)]  # Mon–Fri

    if not weekdays:
        return 0.0

    active_weekdays = sum(1 for d in weekdays if d in date_set)
    return active_weekdays / len(weekdays)
