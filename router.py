from __future__ import annotations

from pages.home import HomeHandlers, render_home


def route(*, ctx, handlers: HomeHandlers) -> None:
    """Route between drilldown and home.

    Behavior should remain identical to the inline router previously in app.py.
    """

    if ctx.match_id:
        # Keep existing drilldown renderer + signature (lives in app.py for now).
        # The caller passes the function in as handlers via closure.
        handlers.render_game_drilldown(
            ctx.match_id,
            ctx.matches_view,
            ctx.players,
            ctx.events_view,
            ctx.plays_view,
            ctx.summaries,
        )
        return

    render_home(
        title="Milton Varsity Boys Soccer Team 2025",
        matches=ctx.matches,
        players=ctx.players,
        events=ctx.events,
        plays_simple=ctx.plays_simple,
        summaries=ctx.summaries,
        goals_allowed=ctx.goals_allowed,
        matches_view=ctx.matches_view,
        events_view=ctx.events_view,
        plays_view=ctx.plays_view,
        ga_view=ctx.ga_view,
        our_rank=ctx.our_rank,
        compact=ctx.compact,
        handlers=handlers,
    )
