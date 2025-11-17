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
    st.subheader("Players leaderboard")
    filtered_players_df = players_df[players_df["Match Played"] > 0]
    st.data_editor(filtered_players_df, num_rows="dynamic")

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
