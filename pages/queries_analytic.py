
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
    conn = sqlite3.connect(os.path.join(db_dir, 'player_stats.db'),check_same_thread=False)
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


st.header("Question 9 :-Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.")
st.markdown("Show the player name and records but using old data till 2024 combining odi and t20 only and show new player data as well thoes who play recently played as well old records.")
# Fetch total ODI runs and wickets per player from conn1
query_odi_stats = """
SELECT
    ob.batsman AS player_id,
    SUM(ob.runs) AS TotalODIRuns,
    SUM(obowl.wickets) AS TotalODIWickets
FROM
    odi_bat ob
JOIN
    odi_bowl obowl ON ob.batsman = obowl."bowler id" -- Assuming batsman and bowler id are the same player
WHERE ob.runs IS NOT NULL AND obowl.wickets IS NOT NULL
GROUP BY
    ob.batsman;
"""
odi_stats_df = pd.read_sql_query(query_odi_stats, conn1)
# Fetch total T20 runs and wickets per player from conn2
query_t20_stats = """
SELECT
    tb.batsman AS player_id,
    SUM(tb.runs) AS TotalT20Runs,
    SUM(tbowl.wickets) AS TotalT20Wickets
FROM
    t20_bat tb
JOIN
    t20_bowl tbowl ON tb.batsman = tbowl."bowler id" -- Assuming batsman and bowler id are the same player
WHERE tb.runs IS NOT NULL AND tbowl.wickets IS NOT NULL
GROUP BY
    tb.batsman;
"""
t20_stats_df = pd.read_sql_query(query_t20_stats, conn2)
# Fetch player names and roles from conn3
query_players_info = """
SELECT
    id AS player_id,
    fullName,
    role
FROM
    players;
"""
players_info_df = pd.read_sql_query(query_players_info, conn3)
# Combine DataFrames and filter for all-rounders meeting criteria
# Merge ODI and T20 stats with player info
combined_stats_df = players_info_df.merge(odi_stats_df, on='player_id', how='left')
combined_stats_df = combined_stats_df.merge(t20_stats_df, on='player_id', how='left')

# Fill NaN values with 0 for players who might not have played in both formats
combined_stats_df.fillna(0, inplace=True)

# Filter for all-rounders (including Batting Allrounder and Bowling Allrounder)
allrounders_df = combined_stats_df[combined_stats_df['role'].str.contains('Allrounder', na=False)].copy()

# Check criteria for each format and select relevant columns
odi_allrounders = allrounders_df[(allrounders_df['TotalODIRuns'] > 1000) & (allrounders_df['TotalODIWickets'] > 50)].copy()
odi_allrounders['Format'] = 'ODI'
odi_allrounders = odi_allrounders[['fullName', 'role', 'Format', 'TotalODIRuns', 'TotalODIWickets']].rename(columns={'TotalODIRuns': 'TotalRuns', 'TotalODIWickets': 'TotalWickets'})

t20_allrounders = allrounders_df[(allrounders_df['TotalT20Runs'] > 1000) & (allrounders_df['TotalT20Wickets'] > 50)].copy()
t20_allrounders['Format'] = 'T20'
t20_allrounders = t20_allrounders[['fullName', 'role', 'Format', 'TotalT20Runs', 'TotalT20Wickets']].rename(columns={'TotalT20Runs': 'TotalRuns', 'TotalT20Wickets': 'TotalWickets'})


# Combine results from both formats
final_allrounders_df = pd.concat([odi_allrounders, t20_allrounders])

# display result
st.dataframe(final_allrounders_df)

st.header("Question 10 Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.")
st.markdown("Show the match description, both team names, winning team, victory margin, victory type, and venue name.")
query_last_20_matche = """ select * from match_list where state = 'Complete' limit 20 """

# display result
try:
    last_20_matches_df = pd.read_sql_query(query_last_20_matche, conn3)
    st.dataframe(last_20_matches_df)
except Exception as e:
    st.error(f"Error executing Question 10 query: {e}")


st.header("Question 11 Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.")
st.markdown("Player recently form thats i fetch in crickbuzz api")

# Fetch batting stats and player info from conn3
query_batting_stats = """
SELECT
    player_id,
    "Runs - Test",
    "Innings - Test",
    "Not Out - Test",
    "Runs - ODI",
    "Innings - ODI",
    "Not Out - ODI",
    "Runs - T20",
    "Innings - T20",
    "Not Out - T20"
FROM
    batting_stats;
"""
batting_stats_df = pd.read_sql_query(query_batting_stats, conn3)

query_players = """
SELECT
    id AS player_id,
    fullName
FROM
    players;
"""
players_df = pd.read_sql_query(query_players, conn3)

# Merge dataframes
merged_df = pd.merge(batting_stats_df, players_df, on='player_id')

# Calculate total runs and dismissals across formats
merged_df['TotalRunsOverall'] = merged_df['Runs - Test'].fillna(0) + merged_df['Runs - ODI'].fillna(0) + merged_df['Runs - T20'].fillna(0)
merged_df['TotalInningsOverall'] = merged_df['Innings - Test'].fillna(0) + merged_df['Innings - ODI'].fillna(0) + merged_df['Innings - T20'].fillna(0)
merged_df['TotalNotOutOverall'] = merged_df['Not Out - Test'].fillna(0) + merged_df['Not Out - ODI'].fillna(0) + merged_df['Not Out - T20'].fillna(0)
merged_df['TotalDismissalsOverall'] = merged_df['TotalInningsOverall'] - merged_df['TotalNotOutOverall']

# Calculate overall batting average, handle division by zero
merged_df['OverallAverage'] = merged_df.apply(
    lambda row: row['TotalRunsOverall'] / row['TotalDismissalsOverall'] if row['TotalDismissalsOverall'] > 0 else 0,
    axis=1
)

# Determine the number of formats played
merged_df['FormatsPlayed'] = merged_df.apply(
    lambda row: sum([
        1 if row['Innings - Test'] > 0 else 0,
        1 if row['Innings - ODI'] > 0 else 0,
        1 if row['Innings - T20'] > 0 else 0
    ]),
    axis=1
)

# Filter for players who played in at least 2 formats
multi_format_players_df = merged_df[merged_df['FormatsPlayed'] >= 2].copy()

# final result display
st.dataframe(multi_format_players_df[['fullName', 'Runs - Test', 'Runs - ODI', 'Runs - T20', 'OverallAverage']].drop_duplicates())


st.header("Question 12 Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.")
st.markdown("Show the team name, number of wins when playing at home, and number of wins when playing away using old data till 2024.")

query_t20_match_data = """
SELECT
    "Team1 Name" AS team1_name,
    "Team2 Name" AS team2_name,
    "Match Venue (Country)" AS venue_country,
    "Match Result Text"
FROM
    t20_match
WHERE
    "Match Result Text" IS NOT NULL;
"""
t20_match_list_df = pd.read_sql_query(query_t20_match_data, conn2)

# Determine the winning team (reusing the function)
def get_winning_team(result_text, team1, team2):
    if ' won ' in result_text:
        if result_text.startswith(team1 + ' won'):
            return team1
        elif result_text.startswith(team2 + ' won'):
            return team2
    return None

t20_match_list_df['WinningTeam'] = t20_match_list_df.apply(
    lambda row: get_winning_team(row['Match Result Text'], row['team1_name'], row['team2_name']),
    axis=1
)

# Filter for matches with a winning team
t20_completed_matches_df = t20_match_list_df[t20_match_list_df['WinningTeam'].notna()].copy()

# Determine Home vs Away status for the winning team (reusing the function)
def get_home_away_status(winning_team, venue_country, team1, team2):
    if winning_team == team1:
        if team1 == venue_country:
            return 'Home Win'
        else:
            return 'Away Win'
    elif winning_team == team2:
        if team2 == venue_country:
            return 'Home Win'
        else:
            return 'Away Win'
    return None

t20_completed_matches_df['WinType'] = t20_completed_matches_df.apply(
    lambda row: get_home_away_status(row['WinningTeam'], row['venue_country'], row['team1_name'], row['team2_name']),
    axis=1
)

# Count wins by team and home/away status
t20_home_away_wins = t20_completed_matches_df.groupby(['WinningTeam', 'WinType']).size().unstack(fill_value=0)

# Rename columns for clarity
t20_home_away_wins.columns.name = None
t20_home_away_wins.rename(columns={'Home Win': 'Home Wins', 'Away Win': 'Away Wins'}, inplace=True)


# Calculate total wins and sort
t20_home_away_wins['Total Wins'] = t20_home_away_wins['Home Wins'] + t20_home_away_wins['Away Wins']
t20_home_away_wins = t20_home_away_wins.sort_values(by='Total Wins', ascending=False)

# Analyze home vs. away wins for ODI matches using conn1
query_odi_match_data = """
SELECT
    "Team1 Name" AS team1_name,
    "Team2 Name" AS team2_name,
    "Match Venue (Country)" AS venue_country,
    "Match Result Text"
FROM
    odi_match
WHERE
    "Match Result Text" IS NOT NULL;
"""
odi_match_list_df = pd.read_sql_query(query_odi_match_data, conn1)

# Determine the winning team (reusing the function)
def get_winning_team(result_text, team1, team2):
    if ' won ' in result_text:
        if result_text.startswith(team1 + ' won'):
            return team1
        elif result_text.startswith(team2 + ' won'):
            return team2
    return None

odi_match_list_df['WinningTeam'] = odi_match_list_df.apply(
    lambda row: get_winning_team(row['Match Result Text'], row['team1_name'], row['team2_name']),
    axis=1
)

# Filter for matches with a winning team
odi_completed_matches_df = odi_match_list_df[odi_match_list_df['WinningTeam'].notna()].copy()

# Determine Home vs Away status for the winning team (reusing the function)
def get_home_away_status(winning_team, venue_country, team1, team2):
    if winning_team == team1:
        if team1 == venue_country:
            return 'Home Win'
        else:
            return 'Away Win'
    elif winning_team == team2:
        if team2 == venue_country:
            return 'Home Win'
        else:
            return 'Away Win'
    return None

odi_completed_matches_df['WinType'] = odi_completed_matches_df.apply(
    lambda row: get_home_away_status(row['WinningTeam'], row['venue_country'], row['team1_name'], row['team2_name']),
    axis=1
)

# Count wins by team and home/away status
odi_home_away_wins = odi_completed_matches_df.groupby(['WinningTeam', 'WinType']).size().unstack(fill_value=0)

# Rename columns for clarity
odi_home_away_wins.columns.name = None
odi_home_away_wins.rename(columns={'Home Win': 'Home Wins', 'Away Win': 'Away Wins'}, inplace=True)

# Calculate total wins and sort
odi_home_away_wins['Total Wins'] = odi_home_away_wins['Home Wins'] + odi_home_away_wins['Away Wins']
odi_home_away_wins = odi_home_away_wins.sort_values(by='Total Wins', ascending=False)

# Combine the ODI and T20 home/away win DataFrames
combined_home_away_wins = pd.concat([odi_home_away_wins, t20_home_away_wins])

# Group by team and sum the home, away, and total wins
combined_home_away_wins_summary = combined_home_away_wins.groupby('WinningTeam').sum().sort_values(by='Total Wins', ascending=False)

# display result
st.dataframe(combined_home_away_wins_summary)


st.header("Question 13:- Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.")
st.markdown("batter partnership but using old data till 2024.")

# Find ODI batting partnerships of 100 or more runs using conn1
query_odi_partnerships = """
SELECT
    op1.player_name AS player1_name,
    op2.player_name AS player2_name,
    opat."partnership runs",
    opat.innings,
    opat."Match ID"
FROM
    odi_pat opat
JOIN
    odi_player op1 ON opat.player1 = op1.player_id
JOIN
    odi_player op2 ON opat.player2 = op2.player_id
WHERE
    opat."partnership runs" >= 100
ORDER BY
    opat."partnership runs" DESC;
"""
odi_partnerships_df = pd.read_sql_query(query_odi_partnerships, conn1)

# Find T20 batting partnerships of 100 or more runs using conn2
query_t20_partnerships = """
SELECT
    tp1.player_name AS player1_name,
    tp2.player_name AS player2_name,
    tpat."partnership runs",
    tpat.innings,
    tpat."Match ID"
FROM
    t20_pat tpat
JOIN
    t20_player tp1 ON tpat.player1 = tp1.player_id
JOIN
    t20_player tp2 ON tpat.player2 = tp2.player_id
WHERE
    tpat."partnership runs" >= 100
ORDER BY
    tpat."partnership runs" DESC;
"""
t20_partnerships_df = pd.read_sql_query(query_t20_partnerships, conn2)

# Combine the ODI and T20 partnerships DataFrames
combined_partnerships_df = pd.concat([odi_partnerships_df, t20_partnerships_df])

# Display the combined results, sorted by partnership runs
combined_partnerships_df = combined_partnerships_df.sort_values(by='partnership runs', ascending=False)

# display result
st.dataframe(combined_partnerships_df)

st.markdown("batter partnership but using recent player performance in 2025 that i fetch data from crickbuzz api but only 10 matches ")
query_innings_partnerships_recent = """
SELECT
    p1.fullName AS player1_name,
    p2.fullName AS player2_name,
    istats.totalRuns AS partnership_runs,
    istats.inningsId AS innings,
    istats.matchId
FROM
    innings_stats istats
JOIN
    players p1 ON istats.bat1Id = p1.id
JOIN
    players p2 ON istats.bat2Id = p2.id
WHERE
    istats.playerType = 'Partnership'
    AND istats.totalRuns >= 100
ORDER BY
    istats.totalRuns DESC;
"""
innings_partnerships_df = pd.read_sql_query(query_innings_partnerships_recent, conn3)


# display result
try:
    innings_partnerships_df = pd.read_sql_query(query_innings_partnerships_recent, conn3)
    st.dataframe(innings_partnerships_df.drop_duplicates())
except Exception as e:
    st.error(f"Error executing Question 13 query: {e}")


st.header("Question 14 Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.")
st.markdown("bowler perfomance  but using old data till 2024 only t20 and odi data .")

query_odi_venue_bowling = """
WITH BowlerVenueStats AS (
    SELECT
        ob."bowler id",
        op.player_name,
        om."Match Venue (Stadium)" AS venue,
        ob.overs,
        ob.wickets,
        ob.economy,
        om."Match ID"
    FROM
        odi_bowl ob
    JOIN
        odi_match om ON ob."Match ID" = om."Match ID"
    JOIN
        odi_player op ON ob."bowler id" = op.player_id
    WHERE
        ob.overs >= 4 -- Filter for bowlers who bowled at least 4 overs in the innings
)
SELECT
    player_name,
    venue,
    COUNT(DISTINCT "Match ID") AS matches_played,
    AVG(economy) AS average_economy_rate,
    SUM(wickets) AS total_wickets_taken
FROM
    BowlerVenueStats
GROUP BY
    player_name, venue
HAVING
    COUNT(DISTINCT "Match ID") >= 3 -- Filter for bowlers who played at least 3 matches at the same venue
ORDER BY
    matches_played DESC, average_economy_rate ASC;
"""
odi_venue_bowling_df = pd.read_sql_query(query_odi_venue_bowling, conn1)

# Analyze bowling performance at different venues for T20 using conn2
query_t20_venue_bowling = """
WITH BowlerVenueStats AS (
    SELECT
        tb."bowler id",
        tp.player_name,
        tm."Match Venue (Stadium)" AS venue,
        tb.overs,
        tb.wickets,
        tb.economy,
        tm."Match ID"
    FROM
        t20_bowl tb
    JOIN
        t20_match tm ON tb."Match ID" = tm."Match ID"
    JOIN
        t20_player tp ON tb."bowler id" = tp.player_id
    WHERE
        tb.overs >= 4 -- Filter for bowlers who bowled at least 4 overs in the innings
)
SELECT
    player_name,
    venue,
    COUNT(DISTINCT "Match ID") AS matches_played,
    AVG(economy) AS average_economy_rate,
    SUM(wickets) AS total_wickets_taken
FROM
    BowlerVenueStats
GROUP BY
    player_name, venue
HAVING
    COUNT(DISTINCT "Match ID") >= 3 -- Filter for bowlers who played at least 3 matches at the same venue
ORDER BY
    matches_played DESC, average_economy_rate ASC;
"""
t20_venue_bowling_df = pd.read_sql_query(query_t20_venue_bowling, conn2)

combined_venue_bowling_df = pd.concat([odi_venue_bowling_df, t20_venue_bowling_df])

# Display the combined results, sorted by matches played and then average economy rate
combined_venue_bowling_df = combined_venue_bowling_df.sort_values(by=['matches_played', 'average_economy_rate'], ascending=[False, True])


# display result
st.dataframe(combined_venue_bowling_df)


st.header("Question 15 Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.")
st.markdown("Player perfomance  but using old data till 2024 only t20 and odi data .")

query_close_odi_matches = """
SELECT
    "Match ID"
FROM
    odi_match
WHERE
    "Match Result Text" LIKE '% won %'
    AND (
        ABS("Team1 Runs Scored" - "Team2 Runs Scored") < 50
        OR ABS("Team1 Wickets Fell" - "Team2 Wickets Fell") < 5
    );
"""
close_odi_matches_df = pd.read_sql_query(query_close_odi_matches, conn1)

query_close_t20_matches = """
SELECT
    "Match ID"
FROM
    t20_match
WHERE
    "Match Result Text" LIKE '% won %'
    AND (
        ABS("Team1 Runs Scored" - "Team2 Runs Scored") < 50
        OR ABS("Team1 Wickets Fell" - "Team2 Wickets Fell") < 5
    );
"""
close_t20_matches_df = pd.read_sql_query(query_close_t20_matches, conn2)


# Combine the Match IDs from both DataFrames
close_match_ids = pd.concat([close_odi_matches_df['Match ID'], close_t20_matches_df['Match ID']]).unique().tolist()


query_odi_batting_in_close_matches = f"""
SELECT
    "Match ID",
    batsman AS player_id,
    runs
FROM
    odi_bat
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))})
    AND runs IS NOT NULL;
"""
odi_batting_in_close_matches_df = pd.read_sql_query(query_odi_batting_in_close_matches, conn1)


query_t20_batting_in_close_matches = f"""
SELECT
    "Match ID",
    batsman AS player_id,
    runs
FROM
    t20_bat
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))})
    AND runs IS NOT NULL;
"""
t20_batting_in_close_matches_df = pd.read_sql_query(query_t20_batting_in_close_matches, conn2)

# 1. Query the odi_match table from conn1 to select the "Match ID" and "Match Result Text" columns.
query_odi_results = """
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    odi_match
WHERE
    "Match ID" IN ({});
""".format(','.join(map(str, close_match_ids)))
odi_match_results_df = pd.read_sql_query(query_odi_results, conn1)

# 2. Query the t20_match table from conn2 to select the "Match ID" and "Match Result Text" columns.
query_t20_results = """
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    t20_match
WHERE
    "Match ID" IN ({});
""".format(','.join(map(str, close_match_ids)))
t20_match_results_df = pd.read_sql_query(query_t20_results, conn2)

# 3. Combine the two match results DataFrames into a single DataFrame.
combined_match_results_df = pd.concat([odi_match_results_df, t20_match_results_df])

# 4. Merge the odi_batting_in_close_matches_df with the combined match results DataFrame on the "Match ID" column.
odi_batting_with_results_df = pd.merge(odi_batting_in_close_matches_df, combined_match_results_df, on="Match ID")

# 5. Merge the t20_batting_in_close_matches_df with the combined match results DataFrame on the "Match ID" column.
t20_batting_with_results_df = pd.merge(t20_batting_in_close_matches_df, combined_match_results_df, on="Match ID")

# 6. For both the merged ODI and T20 DataFrames, extract the winning team name from the "Match Result Text" column.
def extract_winning_team(result_text, team1, team2):
    if ' won ' in result_text:
        if result_text.startswith(team1 + ' won'):
            return team1
        elif result_text.startswith(team2 + ' won'):
            return team2
    return None

odi_batting_with_results_df['WinningTeam'] = odi_batting_with_results_df.apply(
    lambda row: extract_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']), axis=1
)
t20_batting_with_results_df['WinningTeam'] = t20_batting_with_results_df.apply(
    lambda row: extract_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']), axis=1
)

# 7. Add a new column to both merged DataFrames indicating whether the player's team won the match.
# Need to join batting data with match data to get the player's team in that innings
query_odi_batting_with_team = """
SELECT
    "Match ID",
    innings,
    team,
    batsman AS player_id,
    runs
FROM
    odi_bat
WHERE
    "Match ID" IN ({}) AND runs IS NOT NULL;
""".format(','.join(map(str, close_match_ids)))
odi_batting_with_team_df = pd.read_sql_query(query_odi_batting_with_team, conn1)

query_t20_batting_with_team = """
SELECT
    "Match ID",
    innings,
    team,
    batsman AS player_id,
    runs
FROM
    t20_bat
WHERE
    "Match ID" IN ({}) AND runs IS NOT NULL;
""".format(','.join(map(str, close_match_ids)))
t20_batting_with_team_df = pd.read_sql_query(query_t20_batting_with_team, conn2)

# Merge batting data with team information and match results
odi_batting_full_df = pd.merge(odi_batting_with_team_df, combined_match_results_df, on="Match ID")
t20_batting_full_df = pd.merge(t20_batting_with_team_df, combined_match_results_df, on="Match ID")


odi_batting_full_df['WinningTeam'] = odi_batting_full_df.apply(
    lambda row: extract_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']), axis=1
)
t20_batting_full_df['WinningTeam'] = t20_batting_full_df.apply(
    lambda row: extract_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']), axis=1
)

odi_batting_full_df['TeamWonCloseMatch'] = (odi_batting_full_df['team'] == odi_batting_full_df['WinningTeam']).astype(int)
t20_batting_full_df['TeamWonCloseMatch'] = (t20_batting_full_df['team'] == t20_batting_full_df['WinningTeam']).astype(int)

# 8. Concatenate the processed ODI and T20 DataFrames
combined_batting_in_close_matches_df = pd.concat([odi_batting_full_df, t20_batting_full_df])

# Identify close matches from conn1 and conn2
query_close_odi_matches = """
SELECT
    "Match ID"
FROM
    odi_match
WHERE
    "Match Result Text" IS NOT NULL AND (
        ABS("Team1 Runs Scored" - "Team2 Runs Scored") < 50
        OR ABS("Team1 Wickets Fell" - "Team2 Wickets Fell") < 5
    );
"""
close_odi_matches_df = pd.read_sql_query(query_close_odi_matches, conn1)

query_close_t20_matches = """
SELECT
    "Match ID"
FROM
    t20_match
WHERE
    "Match Result Text" IS NOT NULL AND (
        ABS("Team1 Runs Scored" - "Team2 Runs Scored") < 50
        OR ABS("Team1 Wickets Fell" - "Team2 Wickets Fell") < 5
    );
"""
close_t20_matches_df = pd.read_sql_query(query_close_t20_matches, conn2)

# Combine the Match IDs from both DataFrames
close_match_ids = pd.concat([close_odi_matches_df['Match ID'], close_t20_matches_df['Match ID']]).unique().tolist()

print(f"Number of unique close match IDs found: {len(close_match_ids)}")

# Fetch batting performance in close matches from conn1 and conn2
query_odi_batting_in_close_matches = f"""
SELECT
    "Match ID",
    batsman AS player_id,
    runs,
    team -- Include team to check if player's team won
FROM
    odi_bat
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))})
    AND runs IS NOT NULL;
"""
odi_batting_in_close_matches_df = pd.read_sql_query(query_odi_batting_in_close_matches, conn1)

query_t20_batting_in_close_matches = f"""
SELECT
    "Match ID",
    batsman AS player_id,
    runs,
    team -- Include team to check if player's team won
FROM
    t20_bat
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))})
    AND runs IS NOT NULL;
"""
t20_batting_in_close_matches_df = pd.read_sql_query(query_t20_batting_in_close_matches, conn2)

# Combine batting data from close matches
combined_batting_in_close_matches_df = pd.concat([odi_batting_in_close_matches_df, t20_batting_in_close_matches_df])

query_odi_player_names = """
SELECT
    player_id,
    player_name
FROM
    odi_player;
"""
odi_player_names_df = pd.read_sql_query(query_odi_player_names, conn1)

query_t20_player_names = """
SELECT
    player_id,
    player_name
FROM
    t20_player;
"""
t20_player_names_df = pd.read_sql_query(query_t20_player_names, conn2)

# Combine player names from both databases
combined_player_names_df = pd.concat([odi_player_names_df, t20_player_names_df]).drop_duplicates(subset=['player_id'])

query_close_odi_results = f"""
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    odi_match
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))});
"""
close_odi_results_df = pd.read_sql_query(query_close_odi_results, conn1)

query_close_t20_results = f"""
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    t20_match
WHERE
    "Match ID" IN ({','.join(map(str, close_match_ids))});
"""
close_t20_results_df = pd.read_sql_query(query_close_t20_results, conn2)

# Combine close match results
combined_close_match_results_df = pd.concat([close_odi_results_df, close_t20_results_df])

# Determine winning team (reusing the function)
def extract_winning_team(result_text, team1, team2):
    if ' won ' in result_text:
        if result_text.startswith(team1 + ' won'):
            return team1
        elif result_text.startswith(team2 + ' won'):
            return team2
    return None

combined_close_match_results_df['WinningTeam'] = combined_close_match_results_df.apply(
    lambda row: extract_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']), axis=1
)

# Merge batting data with match results and player names
batting_with_results_df = pd.merge(combined_batting_in_close_matches_df, combined_close_match_results_df[['Match ID', 'WinningTeam']], on='Match ID', how='left')
final_close_match_performance_df = pd.merge(batting_with_results_df, combined_player_names_df, on='player_id', how='left')

# Determine if player's team won the close match when they batted
final_close_match_performance_df['TeamWonCloseMatch'] = (final_close_match_performance_df['team'] == final_close_match_performance_df['WinningTeam']).astype(int)

# Group by player and calculate the requested metrics
player_close_match_performance_summary = final_close_match_performance_df.groupby('player_id').agg(
    player_name=('player_name', 'first'), # Get player name
    average_runs=('runs', 'mean'),
    total_close_matches_played=('Match ID', 'nunique'),
    close_matches_won_by_team=('TeamWonCloseMatch', 'sum')
).reset_index()

# Select and display the requested columns
final_player_performance_display_df = player_close_match_performance_summary[['player_name', 'average_runs', 'total_close_matches_played', 'close_matches_won_by_team']]

# display result
st.dataframe(final_player_performance_display_df.sort_values(by='close_matches_won_by_team', ascending=False))


st.header("Q16 Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.")
st.markdown("Player batting perfomance  but using old data till 2024 only t20 and odi data .")

# Track batting performance over different years (since 2020) for ODI from conn1
query_odi_yearly_batting = """
SELECT
    ob.batsman AS player_id,
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) AS match_year,
    SUM(ob.runs) AS total_runs,
    SUM(ob.balls) AS total_balls,
    COUNT(DISTINCT ob."Match ID") AS matches_played
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID"
WHERE
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) >= 2020 AND ob.runs IS NOT NULL
GROUP BY
    ob.batsman, match_year;
"""
odi_yearly_batting_df = pd.read_sql_query(query_odi_yearly_batting, conn1)

# Track batting performance over different years (since 2020) for T20 from conn2
query_t20_yearly_batting = """
SELECT
    tb.batsman AS player_id,
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) AS match_year,
    SUM(tb.runs) AS total_runs,
    SUM(tb.balls) AS total_balls,
    COUNT(DISTINCT tb."Match ID") AS matches_played
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID"
WHERE
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) >= 2020 AND tb.runs IS NOT NULL
GROUP BY
    tb.batsman, match_year;
"""
t20_yearly_batting_df = pd.read_sql_query(query_t20_yearly_batting, conn2)

# Combine the yearly batting data from ODI and T20
combined_yearly_batting_df = pd.concat([odi_yearly_batting_df, t20_yearly_batting_df])

# Group by player and year to aggregate stats across formats for that year
aggregated_yearly_batting_df = combined_yearly_batting_df.groupby(['player_id', 'match_year']).agg(
    total_runs=('total_runs', 'sum'),
    total_balls=('total_balls', 'sum'),
    matches_played=('matches_played', 'sum')
).reset_index()

# Calculate average runs per match and average strike rate
aggregated_yearly_batting_df['average_runs_per_match'] = aggregated_yearly_batting_df['total_runs'] / aggregated_yearly_batting_df['matches_played']
aggregated_yearly_batting_df['average_strike_rate'] = (aggregated_yearly_batting_df['total_runs'] / aggregated_yearly_batting_df['total_balls']) * 100

# Filter for players who played at least 5 matches in that year
filtered_yearly_batting_df = aggregated_yearly_batting_df[aggregated_yearly_batting_df['matches_played'] >= 5].copy()

# Fetch player names from conn1 and conn2 (or conn3 if needed) - using conn1 and conn2 player tables
query_odi_player_names = """SELECT player_id, player_name FROM odi_player;"""
odi_player_names_df = pd.read_sql_query(query_odi_player_names, conn1)

query_t20_player_names = """SELECT player_id, player_name FROM t20_player;"""
t20_player_names_df = pd.read_sql_query(query_t20_player_names, conn2)

# Combine player names from both databases and remove duplicates
combined_player_names_df = pd.concat([odi_player_names_df, t20_player_names_df]).drop_duplicates(subset=['player_id'])


# Merge with player names
final_yearly_batting_df = pd.merge(filtered_yearly_batting_df, combined_player_names_df, on='player_id', how='left')


# display result
st.dataframe(final_yearly_batting_df[['player_name', 'match_year', 'average_runs_per_match', 'average_strike_rate']].sort_values(by=['match_year', 'player_name']))

st.header("Question 17 Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).")
st.markdown("display result Toss Winner Choice,total_matches,toss_winner_wins,win_percentage  but using old data till 2024 only t20 and odi data .")

# Analyze the impact of winning the toss on match outcomes for ODI matches from conn1
query_odi_toss_analysis = """
SELECT
    "Toss Winner",
    "Toss Winner Choice",
    "Match Winner",
    COUNT(*) AS total_matches,
    SUM(CASE WHEN "Toss Winner" = "Match Winner" THEN 1 ELSE 0 END) AS toss_winner_wins
FROM
    odi_match
WHERE
    "Toss Winner" IS NOT NULL AND "Toss Winner Choice" IS NOT NULL AND "Match Winner" IS NOT NULL
GROUP BY
    "Toss Winner", "Toss Winner Choice", "Match Winner";
"""
odi_toss_analysis_df = pd.read_sql_query(query_odi_toss_analysis, conn1)

# Analyze the impact of winning the toss on match outcomes for T20 matches from conn2
query_t20_toss_analysis = """
SELECT
    "Toss Winner",
    "Toss Winner Choice",
    "Match Winner",
    COUNT(*) AS total_matches,
    SUM(CASE WHEN "Toss Winner" = "Match Winner" THEN 1 ELSE 0 END) AS toss_winner_wins
FROM
    t20_match
WHERE
    "Toss Winner" IS NOT NULL AND "Toss Winner Choice" IS NOT NULL AND "Match Winner" IS NOT NULL
GROUP BY
    "Toss Winner", "Toss Winner Choice", "Match Winner";
"""
t20_toss_analysis_df = pd.read_sql_query(query_t20_toss_analysis, conn2)

# Combine the results from both formats
combined_toss_analysis_df = pd.concat([odi_toss_analysis_df, t20_toss_analysis_df])

# Group by toss winner choice and calculate total matches and wins for each choice
toss_choice_summary_df = combined_toss_analysis_df.groupby('Toss Winner Choice').agg(
    total_matches=('total_matches', 'sum'),
    toss_winner_wins=('toss_winner_wins', 'sum')
).reset_index()

# Calculate the percentage of matches won by the toss winner for each choice
toss_choice_summary_df['win_percentage'] = (toss_choice_summary_df['toss_winner_wins'] / toss_choice_summary_df['total_matches']) * 100


# display result
st.dataframe(toss_choice_summary_df)

st.header("Q18 Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.")
st.markdown("display most economical bowler  but using old data till 2024 only t20 and odi data .")

# Find the most economical bowlers in ODI from conn1
query_odi_economical_bowlers = """
SELECT
    ob."bowler id" AS player_id,
    SUM(ob.overs) AS total_overs,
    SUM(ob.conceded) AS total_runs_conceded,
    SUM(ob.wickets) AS total_wickets,
    COUNT(DISTINCT ob."Match ID") AS matches_bowled
FROM
    odi_bowl ob
WHERE
    ob.overs IS NOT NULL AND ob.conceded IS NOT NULL AND ob.wickets IS NOT NULL
GROUP BY
    ob."bowler id";
"""
odi_bowling_stats_df = pd.read_sql_query(query_odi_economical_bowlers, conn1)

# Find the most economical bowlers in T20 from conn2
query_t20_economical_bowlers = """
SELECT
    tb."bowler id" AS player_id,
    SUM(tb.overs) AS total_overs,
    SUM(tb.conceded) AS total_runs_conceded,
    SUM(tb.wickets) AS total_wickets,
    COUNT(DISTINCT tb."Match ID") AS matches_bowled
FROM
    t20_bowl tb
WHERE
    tb.overs IS NOT NULL AND tb.conceded IS NOT NULL AND tb.wickets IS NOT NULL
GROUP BY
    tb."bowler id";
"""
t20_bowling_stats_df = pd.read_sql_query(query_t20_economical_bowlers, conn2)

# Combine the bowling stats from both formats
combined_bowling_stats_df = pd.concat([odi_bowling_stats_df, t20_bowling_stats_df])

# Group by player and aggregate stats across formats
aggregated_bowling_stats_df = combined_bowling_stats_df.groupby('player_id').agg(
    total_overs=('total_overs', 'sum'),
    total_runs_conceded=('total_runs_conceded', 'sum'),
    total_wickets=('total_wickets', 'sum'),
    matches_bowled=('matches_bowled', 'sum')
).reset_index()

# Calculate overall economy rate
aggregated_bowling_stats_df['overall_economy_rate'] = (aggregated_bowling_stats_df['total_runs_conceded'] / aggregated_bowling_stats_df['total_overs']) * 6

# Filter based on criteria: at least 10 matches and at least 2 overs per match on average
filtered_economical_bowlers_df = aggregated_bowling_stats_df[
    (aggregated_bowling_stats_df['matches_bowled'] >= 10) &
    (aggregated_bowling_stats_df['total_overs'] / aggregated_bowling_stats_df['matches_bowled'] >= 2)
].copy()

# Fetch player names from combined player names DataFrame (assuming it was created earlier or create it if not)
# Re-creating combined_player_names_df for completeness if the kernel was reset or cell wasn't run
query_odi_player_names = """SELECT player_id, player_name FROM odi_player;"""
odi_player_names_df = pd.read_sql_query(query_odi_player_names, conn1)

query_t20_player_names = """SELECT player_id, player_name FROM t20_player;"""
t20_player_names_df = pd.read_sql_query(query_t20_player_names, conn2)

combined_player_names_df = pd.concat([odi_player_names_df, t20_player_names_df]).drop_duplicates(subset=['player_id'])


# Merge with player names
final_economical_bowlers_df = pd.merge(filtered_economical_bowlers_df, combined_player_names_df, on='player_id', how='left')

# Select and display result the requested columns, ordered by economy rate (lowest first)
st.dataframe(final_economical_bowlers_df[['player_name', 'overall_economy_rate', 'total_wickets']].sort_values(by='overall_economy_rate'))

st.header("Question 19 Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.")
st.markdown("display most valuble batsmen  but using old data till 2024 only t20 and odi data .")

# Find consistent batsmen in ODI from conn1
query_odi_consistency = """
SELECT
    ob.batsman AS player_id,
    ob.runs,
    ob.balls,
    om."Match Date"
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID"
WHERE
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) >= 2022
    AND ob.balls IS NOT NULL
    AND ob.balls >= 10;
"""
odi_consistency_df = pd.read_sql_query(query_odi_consistency, conn1)

# Find consistent batsmen in T20 from conn2
query_t20_consistency = """
SELECT
    tb.batsman AS player_id,
    tb.runs,
    tb.balls,
    tm."Match Date"
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID"
WHERE
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) >= 2022
    AND tb.balls IS NOT NULL
    AND tb.balls >= 10;
"""
t20_consistency_df = pd.read_sql_query(query_t20_consistency, conn2)

# Combine the data from both formats
combined_consistency_df = pd.concat([odi_consistency_df, t20_consistency_df])

# Calculate average runs and standard deviation of runs for each player
player_consistency_stats = combined_consistency_df.groupby('player_id').agg(
    average_runs=('runs', 'mean'),
    std_dev_runs=('runs', 'std'),
    total_innings=('runs', 'count')
).reset_index()

# Filter out players with less than 2 innings (std deviation is NaN for 1 inning)
player_consistency_stats = player_consistency_stats[player_consistency_stats['total_innings'] >= 2].copy()

# Fetch player names from combined player names DataFrame
# Re-creating combined_player_names_df for completeness if the kernel was reset or cell wasn't run
query_odi_player_names = """SELECT player_id, player_name FROM odi_player;"""
odi_player_names_df = pd.read_sql_query(query_odi_player_names, conn1)

query_t20_player_names = """SELECT player_id, player_name FROM t20_player;"""
t20_player_names_df = pd.read_sql_query(query_t20_player_names, conn2)

combined_player_names_df = pd.concat([odi_player_names_df, t20_player_names_df]).drop_duplicates(subset=['player_id'])

# Merge with player names
final_consistency_df = pd.merge(player_consistency_stats, combined_player_names_df, on='player_id', how='left')

# Select and display result the requested columns, sorted by standard deviation (lowest first)
st.dataframe(final_consistency_df[['player_name', 'average_runs', 'std_dev_runs']].sort_values(by='std_dev_runs'))
