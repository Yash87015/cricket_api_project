
import streamlit as st
import pandas as pd
import sqlite3
import os

# Function to connect to the databases
@st.cache_resource
def get_connections():
    # Use os.path.join for cross-platform compatibility
    # Assuming databases are in a 'pages' directory relative to the script
    db_dir = os.path.dirname(__file__)
    conn1 = sqlite3.connect(os.path.join(db_dir, 'old_odi_data.db'),check_same_thread=False)
    conn2 = sqlite3.connect(os.path.join(db_dir, 'old_T20_data.db'),check_same_thread=False)
    conn3 = sqlite3.connect(os.path.join(db_dir, 'crickbuzz.db'),check_same_thread=False)
    return conn1, conn2, conn3

conn1, conn2, conn3 = get_connections()

st.title("Cricket Data Analysis")

st.header("Question 1 Find all players who represent India. Display their full name, playing role, batting style, and bowling style")
st.markdown("Show player name, team, rating, and career span. Display the highest rated player first.")
query_1_recent = """ select id,name,fullName,role from players WHERE teamName = 'IND'  """
try:
    query_1_recent = pd.read_sql_query(query_1_recent, conn3)
    st.dataframe(query_1_recent)
except Exception as e:
    st.error(f"Error executing Question 1 query: {e}")


st.header("Question 1 Find all players who represent India. Display their full name, playing role, batting style, and bowling style")
st.markdown("Show player name, team, rating, and career span. Display the highest rated player first.")
query_india_players = """
SELECT
    tp.player_id,
    tp.player_name,
    tp.batting_style,
    tp.bowling_style,
    tm."Team1 Name" AS country
FROM
    t20_player tp
JOIN
    t20_match tm ON tp.country_id = tm."Team1 ID"
WHERE
    tm."Team1 Name" = 'India'
GROUP BY
    tp.player_id;
"""
try:
    india_players_df = pd.read_sql_query(query_india_players, conn2)
    st.dataframe(india_players_df)
except Exception as e:
    st.error(f"Error executing Question from old 1 query: {e}")


st.header("Question 2 Show all cricket matches that were played in the last 30 days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.")
st.markdown("Recent last matches last 30 days from collacted by crickbuss api")
query_recent_matches = """
SELECT
    matchDesc,
    team1_name,
    team2_name,
    ground || ', ' || city AS venue_with_city,
    startDate
FROM
    match_list
WHERE
    substr(startDate, 1, 10) >= date('now', '-30 days')
ORDER BY
    startDate DESC;
"""
try:
    recent_matches_df = pd.read_sql_query(query_recent_matches, conn3)
    st.dataframe(recent_matches_df)
except Exception as e:
    st.error(f"Error executing Question 2 query: {e}")


st.header("Question 2: Find the average number of matches played by players in different roles.")
st.markdown("Show the role and the average number of matches played for that role.")
query_avg_matches_by_role = """
SELECT
    p.role,
    AVG(
        CAST(bs."Matches - Test" AS REAL) +
        CAST(bs."Matches - ODI" AS REAL) +
        CAST(bs."Matches - T20" AS REAL)
    ) AS average_matches_played
FROM
    players p
JOIN
    batting_stats bs ON p.id = bs.player_id
WHERE
    p.role IS NOT NULL
GROUP BY
    p.role;
"""
try:
    avg_matches_by_role_df = pd.read_sql_query(query_avg_matches_by_role, conn3)
    st.dataframe(avg_matches_by_role_df)
except Exception as e:
    st.error(f"Error executing Question 2 query: {e}")


st.header("Question 3: List the top 10 highest run scorers in ODI cricket.")
st.markdown("Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.")
query_top_odi_batters_new = """
SELECT
    p.fullName,
    p.role,
    MAX(bs."Highest - ODI") AS "Highest - ODI", -- Select max highest score
    SUM(bs."Runs - ODI") AS "Runs - ODI", -- Sum runs in case of multiple entries per player
    AVG(bs."Average - ODI") AS "Average - ODI", -- Average the average if multiple entries
    SUM(bs."100s - ODI") AS "100s - ODI" -- Sum centuries
FROM
    players p
JOIN
    batting_stats bs ON p.id = bs.player_id
WHERE
    bs."Runs - ODI" IS NOT NULL
GROUP BY
    p.fullName, p.role -- Group by player name and role to handle potential different roles for same name
ORDER BY
    "Runs - ODI" DESC
LIMIT 10;
"""
try:
    top_odi_batters_df = pd.read_sql_query(query_top_odi_batters_new, conn3)
    st.dataframe(top_odi_batters_df)
except Exception as e:
    st.error(f"Error executing Question 3 query: {e}")


st.header("Question 4: Display all cricket venues that have a seating capacity of more than 50,000 spectators.")
st.markdown("Show venue name, city, country, and capacity. Order by largest capacity first.")
query_venues_capacity = """
SELECT
    ground,
    city,
    country,
    capacity
FROM
    venue_stats
WHERE
    capacity > 50000
ORDER BY
    capacity DESC;
"""
try:
    venues_capacity_df = pd.read_sql_query(query_venues_capacity, conn3)
    st.dataframe(venues_capacity_df)
except Exception as e:
    st.error(f"Error executing Question 4 query: {e}")


st.header("Question 5: Calculate how many matches each team has won.")
st.markdown("Show team name and total number of wins. Display teams with most wins first.")

query_wins_t20 = """
SELECT
    CASE
        WHEN "Match Result Text" LIKE "%won%" THEN
            CASE
                WHEN "Match Result Text" LIKE "Team1 Name" || " won%" THEN "Team1 Name"
                WHEN "Match Result Text" LIKE "Team2 Name" || " won%" THEN "Team2 Name"
                ELSE NULL
            END
        ELSE NULL
    END AS WinningTeam,
    COUNT(*) AS TotalWins
FROM
    t20_match
WHERE
    "Match Result Text" IS NOT NULL
GROUP BY
    WinningTeam
HAVING
    WinningTeam IS NOT NULL;
"""

query_wins_odi = """
SELECT
    CASE
        WHEN "Match Result Text" LIKE "%won%" THEN
            CASE
                WHEN "Match Result Text" LIKE "Team1 Name" || " won%" THEN "Team1 Name"
                WHEN "Match Result Text" LIKE "Team2 Name" || " won%" THEN "Team2 Name"
                ELSE NULL
            END
        ELSE NULL
    END AS WinningTeam,
    COUNT(*) AS TotalWins
FROM
    odi_match
WHERE
    "Match Result Text" IS NOT NULL
GROUP BY
    WinningTeam
HAVING
    WinningTeam IS NOT NULL;
"""

try:
    t20_wins_df = pd.read_sql_query(query_wins_t20, conn2)
    odi_wins_df = pd.read_sql_query(query_wins_odi, conn1)

    combined_wins_df = pd.concat([t20_wins_df, odi_wins_df]).groupby('WinningTeam').sum().sort_values(by='TotalWins', ascending=False)
    st.dataframe(combined_wins_df)
except Exception as e:
    st.error(f"Error executing Question 5 query: {e}")


st.header("Question 6: Count how many players belong to each playing role.")
st.markdown("Show the role and count of players for each role.")
query_role_count = """
SELECT
    role,
    COUNT(*) AS player_count
FROM
    players
GROUP BY
    role;
"""
try:
    role_count_df = pd.read_sql_query(query_role_count, conn3)
    st.dataframe(role_count_df)
except Exception as e:
    st.error(f"Error executing Question 6 query: {e}")


st.header("Question 7: Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I).")
st.markdown("Display the format and the highest score for that format.")

batting_stats_df = pd.read_sql_query('select * from batting_stats', conn3)
players_df = pd.read_sql_query('SELECT id, fullName, role FROM players', conn3)

highest_scores_per_player = batting_stats_df.merge(players_df, left_on='player_id', right_on='id', how='inner')

# Group by player and find the maximum highest score in each format
highest_scores_per_player = highest_scores_per_player.groupby(['player_id', 'fullName', 'role']).agg({
    'Highest - Test': 'max',
    'Highest - ODI': 'max',
    'Highest - T20': 'max' # Using 'Highest - T20' as per dataframe columns
}).reset_index()

# display result
st.dataframe(highest_scores_per_player)


st.header("Question 8: Show all cricket series that started in the year 2024.")
st.markdown("Include series name, host country, match type, start date, and total number of matches planned.")

# Find series that had matches in 2024
# Include series name and the earliest match date in 2024 as a proxy for start date.
# Note: Host country, match type, and total planned matches are not available in these tables from the previous analysis.
# Adjusting the query to only show available information.

query_2024_series_t20 = """
SELECT
    "Series Name" AS series_name,
    MIN("Match Date") AS start_date_2024
FROM
    t20_match
WHERE
    CAST(SUBSTR("Match Date", 1, 4) AS INTEGER) = 2024
GROUP BY
    "Series Name";
"""

query_2024_series_odi = """
SELECT
    "Series Name" AS series_name,
    MIN("Match Date") AS start_date_2024
FROM
    odi_match
WHERE
    CAST(SUBSTR("Match Date", 1, 4) AS INTEGER) = 2024
GROUP BY
    "Series Name";
"""

try:
    t20_2024_series_df = pd.read_sql_query(query_2024_series_t20, conn2)
    odi_2024_series_df = pd.read_sql_query(query_2024_series_odi, conn1)

    combined_2024_series_df = pd.concat([t20_2024_series_df, odi_2024_series_df]).drop_duplicates(subset=['series_name']).sort_values(by='start_date_2024')
    st.dataframe(combined_2024_series_df)
except Exception as e:
    st.error(f"Error executing Question 8 query: {e}")
