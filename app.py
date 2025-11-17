import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Football Stats Manager", layout="wide")
st.title("⚽ Football Stats Manager")

uploaded_file = "NUOVO_CALCIATORI_RDG_with_player_name_fixed_dropdown.xlsx"

if uploaded_file:
    # Load sheets
    players_df = pd.read_excel(uploaded_file, sheet_name="Players")
    matches_df = pd.read_excel(uploaded_file, sheet_name="Matches")
    lineups_df = pd.read_excel(uploaded_file, sheet_name="Team Lineups")

    
    st.subheader("Players (with at least 1 match played)")
    filtered_players_df = players_df[players_df["Match Played"] > 0]
    st.data_editor(filtered_players_df, num_rows="dynamic")


    st.subheader("Matches")
    mvp_options = players_df["Player Name"].tolist()
    for i in range(len(matches_df)):
        matches_df.loc[i, "MVP"] = st.selectbox(
            f"MVP for Match {matches_df.loc[i, 'Match ID']}",
            options=[""] + mvp_options,
            index=mvp_options.index(matches_df.loc[i, "MVP"]) + 1 if matches_df.loc[i, "MVP"] in mvp_options else 0
        )

    st.subheader("Team Lineups")
    for i in range(len(lineups_df)):
        lineups_df.loc[i, "Player Name"] = st.selectbox(
            f"Player for lineup row {i+1}",
            options=mvp_options,
            index=mvp_options.index(lineups_df.loc[i, "Player Name"]) if lineups_df.loc[i, "Player Name"] in mvp_options else 0
        )

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

        # Save updated file
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            players_df.to_excel(writer, sheet_name="Players", index=False)
            matches_df.to_excel(writer, sheet_name="Matches", index=False)
            lineups_df.to_excel(writer, sheet_name="Team Lineups", index=False)
        output.seek(0)
        st.download_button("Download File", data=output, file_name="updated_file.xlsx")

