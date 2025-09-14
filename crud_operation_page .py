import streamlit as st
import sqlite3
import pandas as pd

DB = "crickbuzz.db"

def get_conn():
    return sqlite3.connect(DB)

st.title("⚡ CRUD Operations")
st.markdown("Manage **Players** and **Matches** with Create, Read, Update, Delete.")

menu = st.sidebar.radio("Select Table", ["Players", "Match List"]) # Changed "Matches" to "Match List" to match table name

# -----------------------------
# PLAYERS CRUD
# -----------------------------
if menu == "Players":
    st.subheader("Players Table")

    # READ
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM players", conn)
        st.dataframe(df)
    except pd.io.sql.DatabaseError as e:
        st.error(f"Error reading players table: {e}")
        df = pd.DataFrame() # Create empty DataFrame on error
    finally:
        conn.close()


    st.subheader("Player Actions")
    crud = st.radio("Action", ["Create", "Update", "Delete"])

    if crud == "Create":
        with st.form("add_player"):
            st.write("Add New Player")
            # Based on the players table schema: id, name, fullName, nickName, captain, role, keeper, substitute, teamId, battingStyle, bowlingStyle, teamName, faceImageId, squad_type, match_id, team_id, isSupportStaff, playingXIChange, isOverseas, inMatchChange, splSubstitute
            # We'll include some key fields for creation. You can add more as needed.
            player_id = st.number_input("Player ID", step=1, format="%d")
            name = st.text_input("Name")
            full_name = st.text_input("Full Name")
            nick_name = st.text_input("Nick Name")
            role = st.text_input("Role")
            team_id = st.number_input("Team ID", step=1, format="%d")
            team_name = st.text_input("Team Name")
            squad_type = st.selectbox("Squad Type", ["Playing XI", "Bench"])

            submitted = st.form_submit_button("Add Player")
            if submitted:
                conn = get_conn()
                try:
                    # Adjust insert statement to match the actual columns in the players table
                    # Note: Not all columns are included in the form, others will be NULL or default
                    conn.execute("""
                        INSERT INTO players (id, name, fullName, nickName, role, teamId, teamName, squad_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (player_id, name, full_name, nick_name, role, team_id, team_name, squad_type))
                    conn.commit()
                    st.success(f"✅ Player {name} added!")
                except sqlite3.Error as e:
                    st.error(f"Error adding player: {e}")
                finally:
                    conn.close()


    elif crud == "Update":
        st.subheader("Update Player")
        pid = st.number_input("Enter Player ID to Update", step=1, format="%d")
        # Offer fields to update based on players table schema
        new_name = st.text_input("New Name")
        new_role = st.text_input("New Role")
        new_team_name = st.text_input("New Team Name")


        if st.button("Update Player"):
            conn = get_conn()
            try:
                # Construct update query based on fields the user might want to change
                update_fields = []
                update_values = []
                if new_name:
                    update_fields.append("name = ?")
                    update_values.append(new_name)
                if new_role:
                    update_fields.append("role = ?")
                    update_values.append(new_role)
                if new_team_name:
                    update_fields.append("teamName = ?")
                    update_values.append(new_team_name)

                if update_fields:
                    query = f"UPDATE players SET {', '.join(update_fields)} WHERE id = ?"
                    update_values.append(pid)
                    conn.execute(query, update_values)
                    conn.commit()
                    st.success(f"✅ Player {pid} updated!")
                else:
                    st.info("No fields provided for update.")
            except sqlite3.Error as e:
                st.error(f"Error updating player: {e}")
            finally:
                conn.close()


    elif crud == "Delete":
        st.subheader("Delete Player")
        pid = st.number_input("Enter Player ID to Delete", step=1, format="%d")
        if st.button("Delete Player"):
            conn = get_conn()
            try:
                conn.execute("DELETE FROM players WHERE id=?", (pid,))
                conn.commit()
                st.success(f"🗑️ Player {pid} deleted!")
            except sqlite3.Error as e:
                st.error(f"Error deleting player: {e}")
            finally:
                conn.close()


# -----------------------------
# MATCH LIST CRUD
# -----------------------------
elif menu == "Match List": # Matched the menu option
    st.subheader("Match List Table")

    # READ
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM match_list", conn)
        st.dataframe(df)
    except pd.io.sql.DatabaseError as e:
        st.error(f"Error reading match_list table: {e}")
        df = pd.DataFrame() # Create empty DataFrame on error
    finally:
        conn.close()

    st.subheader("Match Actions")
    crud = st.radio("Action", ["Create", "Update", "Delete"])

    if crud == "Create":
        with st.form("add_match"):
            st.write("Add New Match")
            # Based on the match_list table schema: matchId, seriesId, seriesName, matchDesc, matchFormat, startDate, endDate, state, status, currBatTeamId, seriesStartDt, seriesEndDt, isTimeAnnounced, stateTitle, team1_overs, team2_overs, team1_id, team1_name, team1_sname, team1_image_id, team2_id, team2_name, team2_sname, team2_image_id, venue_id, ground, city, timezone, latitude, longitude
            # We'll include some key fields for creation.
            match_id = st.number_input("Match ID", step=1, format="%d")
            series_id = st.number_input("Series ID", step=1, format="%d")
            series_name = st.text_input("Series Name")
            match_desc = st.text_input("Match Description")
            match_format = st.text_input("Match Format")
            start_date = st.text_input("Start Date (YYYY-MM-DD HH:MM:SS)") # Keep as text for flexibility
            end_date = st.text_input("End Date (YYYY-MM-DD HH:MM:SS)") # Keep as text for flexibility
            state = st.text_input("State")
            status = st.text_input("Status")
            team1_id = st.number_input("Team 1 ID", step=1, format="%d")
            team1_name = st.text_input("Team 1 Name")
            team2_id = st.number_input("Team 2 ID", step=1, format="%d")
            team2_name = st.text_input("Team 2 Name")
            venue_id = st.number_input("Venue ID", step=1, format="%d")
            ground = st.text_input("Ground")
            city = st.text_input("City")


            submitted = st.form_submit_button("Add Match")
            if submitted:
                conn = get_conn()
                try:
                    # Adjust insert statement to match the actual columns in the match_list table
                    # Include relevant columns from the form
                    conn.execute("""
                        INSERT INTO match_list (matchId, seriesId, seriesName, matchDesc, matchFormat, startDate, endDate, state, status, team1_id, team1_name, team2_id, team2_name, venue_id, ground, city)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (match_id, series_id, series_name, match_desc, match_format, start_date, end_date, state, status, team1_id, team1_name, team2_id, team2_name, venue_id, ground, city))
                    conn.commit()
                    st.success(f"✅ Match {match_id} added!")
                except sqlite3.Error as e:
                    st.error(f"Error adding match: {e}")
                finally:
                    conn.close()


    elif crud == "Update":
        st.subheader("Update Match")
        mid = st.number_input("Enter Match ID to Update", step=1, format="%d")
        # Offer fields to update based on match_list table schema
        new_status = st.text_input("New Status")
        new_state = st.text_input("New State")
        new_match_desc = st.text_input("New Match Description")


        if st.button("Update Match"):
            conn = get_conn()
            try:
                update_fields = []
                update_values = []
                if new_status:
                    update_fields.append("status = ?")
                    update_values.append(new_status)
                if new_state:
                    update_fields.append("state = ?")
                    update_values.append(new_state)
                if new_match_desc:
                    update_fields.append("matchDesc = ?")
                    update_values.append(new_match_desc)


                if update_fields:
                    query = f"UPDATE match_list SET {', '.join(update_fields)} WHERE matchId = ?"
                    update_values.append(mid)
                    conn.execute(query, update_values)
                    conn.commit()
                    st.success(f"✅ Match {mid} updated!")
                else:
                    st.info("No fields provided for update.")
            except sqlite3.Error as e:
                st.error(f"Error updating match: {e}")
            finally:
                conn.close()


    elif crud == "Delete":
        st.subheader("Delete Match")
        mid = st.number_input("Enter Match ID to Delete", step=1, format="%d")
        if st.button("Delete Match"):
            conn = get_conn()
            try:
                conn.execute("DELETE FROM match_list WHERE matchId=?", (mid,))
                conn.commit()
                st.success(f"🗑️ Match {mid} deleted!")
            except sqlite3.Error as e:
                st.error(f"Error deleting match: {e}")
            finally:
                conn.close()
