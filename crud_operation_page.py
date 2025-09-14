import streamlit as st
import sqlite3
import pandas as pd

DB = "crickbuzz.db"

def get_conn():
    return sqlite3.connect(DB)

st.title("⚡ CRUD Operations")
st.markdown("Manage **Players** and **Matches** with Create, Read, Update, Delete.")

menu = st.sidebar.radio("Select Table", ["Players", "Matches"])

# -----------------------------
# PLAYERS CRUD
# -----------------------------
if menu == "Players":
    st.subheader("Players Table")

    # READ
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM players", conn)
    st.dataframe(df)
    conn.close()

    crud = st.radio("Action", ["Create", "Update", "Delete"])

    if crud == "Create":
        with st.form("add_player"):
            player_id = st.number_input("Player ID", step=1)
            player_name = st.text_input("Player Name")
            country = st.text_input("Country")
            role = st.selectbox("Role", ["Batsman", "Bowler", "Allrounder", "Wicketkeeper"])
            submitted = st.form_submit_button("Add Player")
            if submitted:
                conn = get_conn()
                conn.execute("INSERT INTO players VALUES (?, ?, ?, ?)", 
                             (player_id, player_name, country, role))
                conn.commit()
                conn.close()
                st.success(f"✅ Player {player_name} added!")

    elif crud == "Update":
        pid = st.number_input("Enter Player ID to Update", step=1)
        new_name = st.text_input("New Player Name")
        if st.button("Update"):
            conn = get_conn()
            conn.execute("UPDATE players SET player_name=? WHERE player_id=?", (new_name, pid))
            conn.commit()
            conn.close()
            st.success("✅ Player updated!")

    elif crud == "Delete":
        pid = st.number_input("Enter Player ID to Delete", step=1)
        if st.button("Delete"):
            conn = get_conn()
            conn.execute("DELETE FROM players WHERE player_id=?", (pid,))
            conn.commit()
            conn.close()
            st.success("🗑️ Player deleted!")

# -----------------------------
# MATCHES CRUD
# -----------------------------
elif menu == "Matches":
    st.subheader("Matches Table")

    # READ
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM matches", conn)
    st.dataframe(df)
    conn.close()

    crud = st.radio("Action", ["Create", "Update", "Delete"])

    if crud == "Create":
        with st.form("add_match"):
            match_id = st.number_input("Match ID", step=1)
            series_name = st.text_input("Series Name")
            match_format = st.selectbox("Format", ["Test", "ODI", "T20I", "IPL"])
            match_date = st.date_input("Match Date")
            team1 = st.text_input("Team 1")
            team2 = st.text_input("Team 2")
            status = st.text_input("Status")
            submitted = st.form_submit_button("Add Match")
            if submitted:
                conn = get_conn()
                conn.execute("INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?)", 
                             (match_id, series_name, match_format, str(match_date), team1, team2, status))
                conn.commit()
                conn.close()
                st.success(f"✅ Match {series_name} added!")

    elif crud == "Update":
        mid = st.number_input("Enter Match ID to Update", step=1)
        new_status = st.text_input("New Status")
        if st.button("Update"):
            conn = get_conn()
            conn.execute("UPDATE matches SET status=? WHERE match_id=?", (new_status, mid))
            conn.commit()
            conn.close()
            st.success("✅ Match updated!")

    elif crud == "Delete":
        mid = st.number_input("Enter Match ID to Delete", step=1)
        if st.button("Delete"):
            conn = get_conn()
            conn.execute("DELETE FROM matches WHERE match_id=?", (mid,))
            conn.commit()
            conn.close()
            st.success("🗑️ Match deleted!")
