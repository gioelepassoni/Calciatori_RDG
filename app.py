import streamlit as st
import pandas as pd
from io import BytesIO

# Page config
st.set_page_config(page_title="Football Stats Manager", layout="wide")
st.title("⚽ Football Stats Manager")

# File upload
uploaded_file = "NUOVO_CALCIATORI_RDG_with_player_name_fixed_dropdown.xlsx"

if uploaded_file:
    # Load sheets
    players_df = pd.read_excel(uploaded_file, sheet_name="Players")
    matches_df = pd.read_excel(uploaded_file, sheet_name="Matches")
    lineups_df = pd.read_excel(uploaded_file, sheet_name="Team Lineups")

    # Filter players with at least 1 match
    st.subheader("Players (with at least 1 match played)")
    filtered_players_df = players_df[players_df["Match Played"] > 0]
    st.data_editor(filtered_players_df, num_rows="dynamic")

    # Matches MVP selection
    st.subheader("Matches")
    mvp_options = players_df["Player Name"].tolist()
    for i in range(len(matches_df)):
        current_mvp = matches_df.loc[i, "MVP"]
        index = mvp_options.index(current_mvp) + 1 if current_mvp in mvp_options else 0
        matches_df.loc[i, "MVP"] = st.selectbox(
            f"MVP for Match {matches_df.loc[i, 'Match ID']}",
            options=[""] + mvp_options,
            index=index
        )

    # Team Lineups player selection
    st.subheader("Team Lineups")
    for i in range(len(lineups_df)):
        current_player = lineups_df.loc[i, "Player Name"]
        index = mvp_options.index(current_player) if current_player in mvp_options else 0
        lineups_df.loc[i, "Player Name"] = st.selectbox(
            f"Player for lineup row {i+1}",
            options=mvp_options,
            index=index
        )

    # Download button
    if st.button("Download Updated Excel"):
        # Auto-calculation logic
        for idx, player in players_df.iterrows():
            name = player["Player Name"]
            player_lineups = lineups_df[lineups_df["Player Name"] == name]

            players_df.at[idx, "Match Played"] = len(player_lineups)
            players_df.at[idx, "Goal Scored"] = player_lineups["Goals Scored"].sum()
            players_df.at[idx, "Assists"] = player_lineups["Assists"].sum()
            players_df.at[idx, "Games Won"] = (player_lineups["Result"] == "Win").sum()
            players_df.at[idx, "Games Drew"] = (player_lineups["Result"] == "Draw").sum()
            players_df.at[idx, "Games Lost"] = (player_lineups["Result"] == "Loss").sum()
            players_df.at[idx, "MVP"] = (matches_df["MVP"] == name).sum()
            players_df.at[idx, "Goal/Game"] = (
                players_df.at[idx, "Goal Scored"] / players_df.at[idx, "Match Played"]
                if players_df.at[idx, "Match Played"] > 0 else 0
            )

        # Add % Win column
        players_df["% Win"] = players_df.apply(
            lambda row: (row["Games Won"] / row["Match Played"]) * 100 if row["Match Played"] > 0 else 0,
            axis=1
        )

        # Sort by Games Won, % Win, MVP, Goal Scored
        players_df = players_df.sort_values(
            by=["Games Won", "% Win", "MVP", "Goal Scored"],
            ascending=[False, False, False, False]
        )

        # Save updated file
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            players_df.to_excel(writer, sheet_name="Players", index=False)
            matches_df.to_excel(writer, sheet_name="Matches", index=False)
            lineups_df.to_excel(writer, sheet_name="Team Lineups", index=False)
        output.seek(0)

        st.download_button("Download File", data=output, file_name="updated_file.xlsx")

        # Show sorted table
        st.subheader("Players Sorted by Performance")
        st.dataframe(players_df)
