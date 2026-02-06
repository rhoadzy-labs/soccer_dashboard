import streamlit as st


def render_home_tab_leaders(
    events_view,
    players,
    *,
    compact: bool,
    render_points_leaderboard,
) -> None:
    # Refactor-only extraction: preserve behavior by delegating to existing renderer.
    render_points_leaderboard(events_view, players, top_n=5, compact=compact)
