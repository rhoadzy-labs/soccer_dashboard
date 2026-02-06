def render_home_tab_goals_allowed(
    ga_view,
    matches_view,
    players,
    *,
    compact: bool,
    render_goals_allowed_analysis,
) -> None:
    # Refactor-only extraction: preserve behavior by delegating to existing renderer.
    render_goals_allowed_analysis(ga_view, matches_view, players, compact=compact)
