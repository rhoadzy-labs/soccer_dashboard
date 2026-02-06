import altair as alt
import streamlit as st


def render_home_tab_trends(
    matches_view,
    *,
    compact: bool,
    build_comparison_trend_frame,
    build_individual_game_trends,
) -> None:
    # NOTE: Keep widget/chart construction order identical to the original inline
    # Trends tab block (refactor-only extraction).

    if matches_view.empty:
        st.info("No games yet to build trends.")
    else:
        # Comparison between all games vs last 3 games
        comparison_df = build_comparison_trend_frame(matches_view)
        individual_df = build_individual_game_trends(matches_view)

        st.subheader("All Games vs Last 3 Games Comparison")

        # Display comparison table
        st.dataframe(
            comparison_df.round(2),
            use_container_width=True,
            hide_index=True,
            height=200,
        )

        # Create comparison charts
        label_axis = alt.Axis(labelAngle=-45) if compact else alt.Axis()
        h = 220

        # Melt the comparison data for better charting
        comparison_melted = comparison_df.melt(
            id_vars=["Metric"],
            value_vars=["All Games", "Last 3 Games"],
            var_name="Period",
            value_name="Value",
        )

        # Comparison bar chart
        comparison_chart = alt.Chart(comparison_melted).mark_bar().encode(
            x=alt.X("Metric:N", title="Metric", axis=label_axis),
            y=alt.Y("Value:Q", title="Value"),
            color=alt.Color("Period:N", title="Period"),
            tooltip=["Metric", "Period", "Value"],
        ).properties(height=h)
        st.altair_chart(comparison_chart, use_container_width=True)

        st.subheader("Individual Game Performance")

        # Individual game trends
        for col, title in [
            ("GF", "Goals For"),
            ("GA", "Goals Against"),
            ("Save%", "Save %"),
            ("GF Conv%", "Conversion % (For)"),
            ("GA Conv%", "Conversion % (Against)"),
        ]:
            # Create chart with different colors for last 3 games
            chart = alt.Chart(individual_df).mark_circle(size=60).encode(
                x=alt.X("Game #:O", title="Game Number"),
                y=alt.Y(f"{col}:Q", title=title),
                color=alt.Color(
                    "Last 3 Games:N",
                    scale=alt.Scale(domain=[True, False], range=["#ff6b6b", "#4ecdc4"]),
                    title="Last 3 Games",
                ),
                tooltip=["Game #", "Date", "Opponent", col, "Last 3 Games"],
            ).properties(height=h)

            # Add trend line
            trend_line = alt.Chart(individual_df).mark_line(color="gray", opacity=0.5).encode(
                x=alt.X("Game #:O"),
                y=alt.Y(f"{col}:Q"),
            ).properties(height=h)

            final_chart = (chart + trend_line).resolve_scale(color="independent")
            st.altair_chart(final_chart, use_container_width=True)
