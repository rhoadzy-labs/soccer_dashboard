"""Home page (internal routing).

This module intentionally wires existing functions from app.py into a page-level
renderer, without changing behavior.

Over time we'll move individual renderers and helpers out of app.py into modules
under pages/, ui/, and ai/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class HomeHandlers:
    team_kpis: Callable[..., None]
    render_games_table: Callable[..., None]
    render_points_leaderboard: Callable[..., None]
    render_goals_allowed_analysis: Callable[..., None]
    render_set_piece_analysis_from_plays: Callable[..., None]

    build_comparison_trend_frame: Callable[..., pd.DataFrame]
    build_individual_game_trends: Callable[..., pd.DataFrame]

    generate_ai_team_analysis: Callable[..., str]
    ai_user_error_message: Callable[..., str]
    render_ai_debug: Callable[..., None]


def render_home(
    *,
    title: str,
    matches: pd.DataFrame,
    players: pd.DataFrame,
    events: pd.DataFrame,
    plays_simple: pd.DataFrame,
    summaries: pd.DataFrame,
    goals_allowed: pd.DataFrame,
    matches_view: pd.DataFrame,
    events_view: pd.DataFrame,
    plays_view: pd.DataFrame,
    ga_view: pd.DataFrame,
    our_rank: Optional[int],
    compact: bool,
    handlers: HomeHandlers,
) -> None:
    st.header(title)

    # Data health panel
    with st.expander("Data Health", expanded=False):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Matches", len(matches))
        c2.metric("Players", len(players))
        c3.metric("Events", len(events))
        c4.metric("Plays", len(plays_simple))
        c5.metric("Summaries", len(summaries))
        c6.metric("Goals Allowed", len(goals_allowed))
        st.caption("Sheets cached for up to 5 minutes. Use Refresh in sidebar to reload.")
        if "cache_cleared_at" in st.session_state:
            st.caption(f"Last manual refresh: {st.session_state['cache_cleared_at']}")
        if st.button("Refresh now"):
            st.cache_data.clear()
            st.rerun()

    handlers.team_kpis(matches_view, d2_rank=our_rank, compact=compact)

    tab_labels = ["Games", "Trends", "Leaders", "Goals Allowed", "Set Pieces"]
    if "main_tab_radio" not in st.session_state:
        st.session_state["main_tab_radio"] = tab_labels[0]

    selected_tab = st.radio(
        "Main tabs",
        tab_labels,
        horizontal=True,
        key="main_tab_radio",
        label_visibility="collapsed",
    )

    if selected_tab == "Games":
        handlers.render_games_table(matches_view, compact=compact)

        st.divider()
        st.subheader("AI Assistant")
        st.caption("Ask questions about team performance and season trends")

        if "ai_chat_history" not in st.session_state:
            st.session_state.ai_chat_history = []

        chat_container = st.container()
        with chat_container:
            for message in st.session_state.ai_chat_history:
                if message["role"] == "user":
                    st.markdown(
                        f"""
                    <div class='ai-chat-message ai-chat-user'>
                        <strong>You:</strong> {message['content']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                    <div class='ai-chat-message ai-chat-assistant'>
                        <strong>AI:</strong> {message['content']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        handlers.render_ai_debug()

        c1, c2 = st.columns([4, 1])
        with c1:
            user_input = st.text_input(
                "Ask a question about the team:",
                placeholder="e.g., 'Summarize our season performance'",
                key="ai_chat_input_games",
            )
        with c2:
            send_button = st.button("Send", type="primary")

        st.markdown("**Quick Actions:**")
        q2, q3 = st.columns(2)
        with q2:
            if st.button("Season Summary", help="Get a comprehensive overview of your season"):
                user_input = (
                    "Provide a comprehensive summary of our season performance including strengths, "
                    "weaknesses, and key insights"
                )
                send_button = True
        with q3:
            if st.button("Performance Trends", help="Analyze trends and identify improvement areas"):
                user_input = "Analyze our performance trends and identify areas for improvement"
                send_button = True

        if send_button and user_input and user_input.strip():
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

            with st.spinner("AI is analyzing..."):
                ai_response = handlers.generate_ai_team_analysis(
                    user_input,
                    matches_view,
                    players,
                    events_view,
                    plays_view,
                    ga_view,
                )

            if ai_response:
                st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_response})
            else:
                st.session_state.ai_chat_history.append(
                    {
                        "role": "assistant",
                        "content": (
                            handlers.ai_user_error_message(
                                "I'm sorry, I couldn't generate a response. "
                                "Please make sure you have a Gemini API key configured and try again."
                            )
                        ),
                    }
                )

            st.rerun()

        if st.button("Clear Chat History"):
            st.session_state.ai_chat_history = []
            st.rerun()

    elif selected_tab == "Trends":
        if matches_view.empty:
            st.info("No games yet to build trends.")
        else:
            import altair as alt

            comparison_df = handlers.build_comparison_trend_frame(matches_view)
            individual_df = handlers.build_individual_game_trends(matches_view)

            st.subheader("All Games vs Last 3 Games Comparison")
            st.dataframe(comparison_df.round(2), use_container_width=True, hide_index=True, height=200)

            label_axis = alt.Axis(labelAngle=-45) if compact else alt.Axis()
            h = 220

            comparison_melted = comparison_df.melt(
                id_vars=["Metric"],
                value_vars=["All Games", "Last 3 Games"],
                var_name="Period",
                value_name="Value",
            )

            comparison_chart = (
                alt.Chart(comparison_melted)
                .mark_bar()
                .encode(
                    x=alt.X("Metric:N", title="Metric", axis=label_axis),
                    y=alt.Y("Value:Q", title="Value"),
                    color=alt.Color("Period:N", title="Period"),
                    tooltip=["Metric", "Period", "Value"],
                )
                .properties(height=h)
            )
            st.altair_chart(comparison_chart, use_container_width=True)

            st.subheader("Individual Game Performance")

            for col, chart_title in [
                ("GF", "Goals For"),
                ("GA", "Goals Against"),
                ("Save%", "Save %"),
                ("GF Conv%", "Conversion % (For)"),
                ("GA Conv%", "Conversion % (Against)"),
            ]:
                chart = (
                    alt.Chart(individual_df)
                    .mark_circle(size=60)
                    .encode(
                        x=alt.X("Game #:O", title="Game Number"),
                        y=alt.Y(f"{col}:Q", title=chart_title),
                        color=alt.Color(
                            "Last 3 Games:N",
                            scale=alt.Scale(domain=[True, False], range=["#ff6b6b", "#4ecdc4"]),
                            title="Last 3 Games",
                        ),
                        tooltip=["Game #", "Date", "Opponent", col, "Last 3 Games"],
                    )
                    .properties(height=h)
                )

                trend_line = (
                    alt.Chart(individual_df)
                    .mark_line(color="gray", opacity=0.5)
                    .encode(x=alt.X("Game #:O"), y=alt.Y(f"{col}:Q"))
                    .properties(height=h)
                )

                final_chart = (chart + trend_line).resolve_scale(color="independent")
                st.altair_chart(final_chart, use_container_width=True)

    elif selected_tab == "Leaders":
        handlers.render_points_leaderboard(events_view, players, top_n=5, compact=compact)

    elif selected_tab == "Goals Allowed":
        handlers.render_goals_allowed_analysis(ga_view, matches_view, players, compact=compact)

    elif selected_tab == "Set Pieces":
        handlers.render_set_piece_analysis_from_plays(plays_view, matches_view, players)
