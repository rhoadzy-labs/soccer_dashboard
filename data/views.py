from __future__ import annotations

from typing import Optional

import pandas as pd


def apply_match_filters(
    matches: pd.DataFrame,
    *,
    div_only: bool,
    opp_filter: str,
    ha_val: str,
) -> pd.DataFrame:
    """Apply current filters to matches and return a filtered copy."""

    matches_view = matches.copy()

    if div_only and not matches_view.empty and "division_game" in matches_view:
        matches_view = matches_view.query("division_game == True")

    opp_filter = (opp_filter or "").strip()
    if opp_filter and not matches_view.empty and "opponent" in matches_view:
        matches_view = matches_view[
            matches_view["opponent"].astype(str).str.contains(opp_filter, case=False, na=False)
        ]

    ha_val = (ha_val or "any").lower()
    if ha_val in ("h", "home", "a", "away") and not matches_view.empty and "home_away" in matches_view:
        want = "H" if ha_val.startswith("h") else "A"
        matches_view = matches_view[matches_view["home_away"].astype(str).str.upper() == want]

    return matches_view


def derive_related_views(
    *,
    matches_view: pd.DataFrame,
    events: pd.DataFrame,
    plays_simple: pd.DataFrame,
    goals_allowed: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filter events/plays/goals_allowed to match the currently-filtered matches."""

    if not matches_view.empty and "match_id" in matches_view:
        keep = set(matches_view["match_id"].astype(str))
        events_view = (
            events[events["match_id"].astype(str).isin(keep)] if "match_id" in events.columns else events
        )
        plays_view = (
            plays_simple[plays_simple["match_id"].astype(str).isin(keep)] if not plays_simple.empty else plays_simple
        )
        ga_view = (
            goals_allowed[goals_allowed["match_id"].astype(str).isin(keep)]
            if not goals_allowed.empty
            else goals_allowed
        )
    else:
        events_view, plays_view, ga_view = events, plays_simple, goals_allowed

    return events_view, plays_view, ga_view


def get_match_id(qp: dict) -> Optional[str]:
    """Extract match_id from query params."""

    match_id: Optional[str] = None
    try:
        raw = qp.get("match_id")
        match_id = raw[0] if isinstance(raw, list) else raw
    except Exception:
        pass
    return match_id
