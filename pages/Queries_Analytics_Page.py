import streamlit as st
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Function to get database connection
@st.cache_resource
def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

# Database Connections (assuming the .db files are available in the project's root directory)
conn1 = get_connection('old_odi_data.db')
conn2 = get_connection('old_T20_data.db')
conn3 = get_connection('crickbuzz.db')
conn = get_connection('player_stats.db') # Assuming a fourth database based on Q20 and Q21 queries


# Helper functions (previously defined)
def get_winning_team(result_text, team1, team2):
    if ' won ' in result_text:
        if result_text.startswith(team1 + ' won'):
            return team1
        elif result_text.startswith(team2 + ' won'):
            return team2
    return None

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

def standardize_team_pair(row):
    teams = sorted([row['Team1 Name'], row['Team2 Name']])
    return '_'.join(teams)

def calculate_victory_margin(row):
    if row['WinningTeam'] == row['Team1 Name']:
        if 'runs' in row['Match Result Text']:
            return abs(row['Team1 Runs Scored'] - row['Team2 Runs Scored'])
        elif 'wickets' in row['Match Result Text']:
            return abs(10 - row['Team2 Wickets Fell']) # Assuming 10 wickets in an innings
    elif row['WinningTeam'] == row['Team2 Name']:
        if 'runs' in row['Match Result Text']:
            return abs(row['Team2 Runs Scored'] - row['Team1 Runs Scored'])
        elif 'wickets' in row['Match Result Text']:
            return abs(10 - row['Team1 Wickets Fell']) # Assuming 10 wickets in an innings
    return np.nan

def analyze_team_pair_head_to_head(df_pair):
    team1 = df_pair['Team1 Name'].iloc[0]
    team2 = df_pair['Team2 Name'].iloc[0]
    team_pair_name = df_pair['TeamPair'].iloc[0]

    total_matches = len(df_pair)

    df_pair['WinningTeam'] = df_pair.apply(
        lambda row: get_winning_team(row['Match Result Text'], row['Team1 Name'], row['Team2 Name']),
        axis=1
    )

    team1_wins = df_pair[df_pair['WinningTeam'] == team1].shape[0]
    team2_wins = df_pair[df_pair['WinningTeam'] == team2].shape[0]

    df_pair['VictoryMargin'] = df_pair.apply(calculate_victory_margin, axis=1)

    avg_margin_team1 = df_pair[df_pair['WinningTeam'] == team1]['VictoryMargin'].mean() if team1_wins > 0 else 0
    avg_margin_team2 = df_pair[df_pair['WinningTeam'] == team2]['VictoryMargin'].mean() if team2_wins > 0 else 0

    team1_bat_first_wins = df_pair[(df_pair['Toss Winner'] == team1) & (df_pair['Toss Winner Choice'] == 'bat') & (df_pair['WinningTeam'] == team1)].shape[0]
    team1_bowl_first_wins = df_pair[(df_pair['Toss Winner'] == team1) & (df_pair['Toss Winner Choice'] == 'bowl') & (df_pair['WinningTeam'] == team1)].shape[0]
    team2_bat_first_wins = df_pair[(df_pair['Toss Winner'] == team2) & (df_pair['Toss Winner Choice'] == 'bat') & (df_pair['WinningTeam'] == team2)].shape[0]
    team2_bowl_first_wins = df_pair[(df_pair['Toss Winner'] == team2) & (df_pair['Toss Winner Choice'] == 'bowl') & (df_pair['WinningTeam'] == team2)].shape[0]


    team1_win_percentage = (team1_wins / total_matches) * 100 if total_matches > 0 else 0
    team2_win_percentage = (team2_wins / total_matches) * 100 if total_matches > 0 else 0

    return {
        'TeamPair': team_pair_name,
        'Team1': team1,
        'Team2': team2,
        'TotalMatches': total_matches,
        f'{team1}_Wins': team1_wins,
        f'{team2}_Wins': team2_wins,
        f'Avg_Margin_{team1}': avg_margin_team1,
        f'Avg_Margin_{team2}': avg_margin_team2,
        f'{team1}_BatFirst_Wins': team1_bat_first_wins,
        f'{team1}_BowlFirst_Wins': team1_bowl_first_wins,
        f'{team2}_BatFirst_Wins': team2_bat_first_wins,
        f'{team2}_BowlFirst_Wins': team2_bowl_first_wins,
        f'{team1}_WinPercentage': team1_win_percentage,
        f'{team2}_WinPercentage': team2_win_percentage
    }

def analyze_recent_form(df):
    if len(df) < 5:
        return pd.Series([np.nan] * 7, index=['avg_runs_last_5', 'avg_runs_last_10', 'recent_strike_rate', 'scores_above_50', 'std_dev_runs', 'consistency_score', 'form_category'])

    avg_runs_last_5 = df['runs'].tail(5).mean()
    avg_runs_last_10 = df['runs'].mean()
    recent_strike_rate = (df['runs'].sum() / df['balls'].sum()) * 100 if df['balls'].sum() > 0 else 0
    scores_above_50 = (df['runs'] > 50).sum()
    std_dev_runs = df['runs'].std()
    consistency_score = 1 / (std_dev_runs + 1)

    if avg_runs_last_5 > avg_runs_last_10 * 1.2 and scores_above_50 >= 2 and consistency_score > 0.5:
        form_category = 'Excellent Form'
    elif avg_runs_last_5 >= avg_runs_last_10 * 1.05 and scores_above_50 >= 1 and consistency_score > 0.3:
        form_category = 'Good Form'
    elif avg_runs_last_10 > 20 and consistency_score > 0.2:
        form_category = 'Average Form'
    else:
        form_category = 'Poor Form'

    return pd.Series([avg_runs_last_5, avg_runs_last_10, recent_strike_rate, scores_above_50, std_dev_runs, consistency_score, form_category], index=['avg_runs_last_5', 'avg_runs_last_10', 'recent_strike_rate', 'scores_above_50', 'std_dev_runs', 'consistency_score', 'form_category'])


def performance_trend(current, previous):
    if pd.isna(previous):
        return 'Stable'
    if current > previous * 1.1:
        return 'Improving'
    elif current < previous * 0.9:
        return 'Declining'
    else:
        return 'Stable'

def career_trajectory(df):
    if len(df) < 6:
        return 'Not enough data'

    df_sorted = df.sort_values(by=['year', 'quarter']).reset_index(drop=True)

    recent_avg_runs = df_sorted['average_runs'].tail(3).mean()
    earlier_avg_runs = df_sorted['average_runs'].head(3).mean()

    if earlier_avg_runs == 0:
        if recent_avg_runs > 0:
            return 'Career Ascending'
        else:
            return 'Career Stable'

    percentage_change = (recent_avg_runs - earlier_avg_runs) / earlier_avg_runs

    if percentage_change > 0.2:
        return 'Career Ascending'
    elif percentage_change < -0.2:
        return 'Career Declining'
    else:
        return 'Career Stable'

def categorize_career_phase(df):
    if len(df) < 6:
        return 'Not enough data'

    trajectory = df['career_trajectory'].iloc[0]

    recent_trends = df.tail(3)
    runs_improving_recent = (recent_trends['runs_trend'] == 'Improving').sum()
    sr_improving_recent = (recent_trends['sr_trend'] == 'Improving').sum()
    runs_declining_recent = (recent_trends['runs_trend'] == 'Declining').sum()
    sr_declining_recent = (recent_trends['sr_trend'] == 'Declining').sum()

    if trajectory == 'Career Ascending' and (runs_improving_recent >= 2 or sr_improving_recent >= 2):
        return 'Career Ascending'
    elif trajectory == 'Career Declining' and (runs_declining_recent >= 2 or sr_declining_recent >= 2):
        return 'Career Declining'
    elif trajectory == 'Career Stable' and (runs_improving_recent + sr_improving_recent >= runs_declining_recent + sr_declining_recent):
        return 'Career Stable'
    elif runs_improving_recent >= 2 or sr_improving_recent >= 2:
         return 'Career Ascending'
    elif runs_declining_recent >= 2 or sr_declining_recent >= 2:
         return 'Career Declining'
    else:
        return 'Career Stable'

def calculate_points(batting_df, bowling_df, fielding_df, format_name):
    merged_df = batting_df.merge(bowling_df, on='Player', how='left').merge(fielding_df, on='Player', how='left')

    cols_to_numeric = ['Runs', 'BattingAverage', 'StrikeRate', 'Wickets', 'BowlingAverage', 'EconomyRate', 'Catches', 'Stumpings', 'Inns']
    for col in cols_to_numeric:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0)
        else:
            merged_df[col] = 0

    if format_name == 'Test':
        merged_df['Batting Points'] = (merged_df['Runs'] * 0.01) + (merged_df['BattingAverage'] * 0.5)
    else:
        merged_df['StrikeRate_calc'] = merged_df['StrikeRate'].replace(0, np.nan)
        merged_df['Batting Points'] = (merged_df['Runs'] * 0.01) + (merged_df['BattingAverage'] * 0.5) + (merged_df['StrikeRate_calc'].fillna(0) * 0.3)
        merged_df = merged_df.drop(columns=['StrikeRate_calc'])

    merged_df['BowlingAverage_calc'] = merged_df['BowlingAverage'].replace([np.inf, -np.inf], np.nan).fillna(50)
    merged_df['EconomyRate_calc'] = merged_df['EconomyRate'].replace([np.inf, -np.inf], np.nan).fillna(6)

    merged_df['BowlingPoints_Avg'] = (50 - merged_df['BowlingAverage_calc']) * 0.5
    merged_df['BowlingPoints_Avg'] = merged_df['BowlingPoints_Avg'].apply(lambda x: max(0, x))

    merged_df['BowlingPoints_Econ'] = (6 - merged_df['EconomyRate_calc']) * 2
    merged_df['BowlingPoints_Econ'] = merged_df['BowlingPoints_Econ'].apply(lambda x: max(0, x))

    merged_df['Bowling Points'] = (merged_df['Wickets'] * 2) + merged_df['BowlingPoints_Avg'] + merged_df['BowlingPoints_Econ']

    merged_df = merged_df.drop(columns=['BowlingAverage_calc', 'EconomyRate_calc', 'BowlingPoints_Avg', 'BowlingPoints_Econ'])

    merged_df['Fielding Points'] = (merged_df['Catches'] * 3) + (merged_df['Stumpings'] * 5)

    merged_df['Total Score'] = merged_df['Batting Points'] + merged_df['Bowling Points'] + merged_df['Fielding Points']

    return merged_df[['Player', 'Batting Points', 'Bowling Points', 'Fielding Points', 'Total Score']].copy()

# Query definitions (previously defined and used within functions)
query_1_recent = """ select id,name,fullName,role from players WHERE teamName = 'IND'  """
query_india_players_old = """
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

query_top_odi_batters_new = """
SELECT
    p.fullName,
    p.role,
    bs."Highest - ODI",
    bs."Runs - ODI",
    bs."Average - ODI",
    bs."100s - ODI"
FROM
    players p
JOIN
    batting_stats bs ON p.id = bs.player_id
WHERE
    bs."Runs - ODI" IS NOT NULL
ORDER BY
    bs."Runs - ODI" DESC
LIMIT 10;
"""

query_top_odi_batters_old = """
SELECT
    op.player_name,
    SUM(ob.runs) AS total_runs,
    CAST(SUM(ob.runs) AS REAL) / COUNT(CASE WHEN ob.isOut = 1 THEN 1 ELSE NULL END) AS batting_average,
    SUM(CASE WHEN ob.runs >= 100 THEN 1 ELSE 0 END) AS centuries
FROM
    odi_bat ob
JOIN
    odi_player op ON ob.batsman = op.player_id
WHERE
    ob.runs IS NOT NULL
GROUP BY
    op.player_name
ORDER BY
    total_runs DESC
LIMIT 10;
"""

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

query_role_count = """
SELECT
    role,
    COUNT(*) AS player_count
FROM
    players
GROUP BY
    role;
"""

query_highest_scores = """
SELECT
    MAX("Highest - Test") AS HighestTestScore,
    MAX("Highest - ODI") AS HighestODIScore,
    MAX("Highest - T20") AS HighestT20Score
FROM
    batting_stats;
"""

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

query_odi_stats_q9 = """
SELECT
    ob.batsman AS player_id,
    SUM(ob.runs) AS TotalODIRuns
FROM
    odi_bat ob
WHERE ob.runs IS NOT NULL
GROUP BY
    ob.batsman;
"""

query_odi_bowl_stats_q9 = """
SELECT
    obowl."bowler id" AS player_id,
    SUM(obowl.wickets) AS TotalODIWickets
FROM
    odi_bowl obowl
WHERE obowl.wickets IS NOT NULL
GROUP BY
    obowl."bowler id";
"""


query_t20_stats_q9 = """
SELECT
    tb.batsman AS player_id,
    SUM(tb.runs) AS TotalT20Runs
FROM
    t20_bat tb
WHERE tb.runs IS NOT NULL
GROUP BY
    tb.batsman;
"""

query_t20_bowl_stats_q9 = """
SELECT
    tbowl."bowler id" AS player_id,
    SUM(tbowl.wickets) AS TotalT20Wickets
FROM
    t20_bowl tbowl
WHERE tbowl.wickets IS NOT NULL
GROUP BY
    tbowl."bowler id";
"""

query_players_info_q9 = """
SELECT
    id AS player_id,
    fullName,
    role
FROM
    players;
"""

query_last_20_matches = """
SELECT
    matchDesc,
    team1_name,
    team2_name,
    stateTitle AS winning_team_info,
    ground AS venue_name
FROM
    match_list
WHERE
    state = 'Complete'
ORDER BY
    startDate DESC
LIMIT 20;
"""

query_batting_stats_q11 = """
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

query_players_q11 = """
SELECT
    id AS player_id,
    fullName
FROM
    players;
"""

query_t20_match_data_q12 = """
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

query_odi_match_data_q12 = """
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

query_odi_partnerships_q13 = """
SELECT
    player1,
    player2,
    "partnership runs",
    innings,
    "Match ID"
FROM
    odi_pat
WHERE
    "partnership runs" >= 100;
"""

query_t20_partnerships_q13 = """
SELECT
    player1,
    player2,
    "partnership runs",
    innings,
    "Match ID"
FROM
    t20_pat
WHERE
    "partnership runs" >= 100;
"""

query_innings_partnerships_q13 = """
SELECT
    bat1Id,
    bat2Id,
    totalRuns,
    inningsId,
    matchId
FROM
    innings_stats
WHERE
    playerType = 'Partnership'
    AND totalRuns >= 100;
"""

query_odi_player_names_q13 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q13 = """SELECT player_id, player_name FROM t20_player;"""
query_players_names_conn3_q13 = """SELECT id AS player_id, fullName AS player_name FROM players;"""

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
        ob.overs >= 4
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
    COUNT(DISTINCT "Match ID") >= 3;
"""

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
        tb.overs >= 4
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
    COUNT(DISTINCT "Match ID") >= 3;
"""

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

query_odi_batting_in_close_matches = """
SELECT
    "Match ID",
    batsman AS player_id,
    runs,
    team
FROM
    odi_bat
WHERE
    "Match ID" IN ({}) AND runs IS NOT NULL;
"""

query_t20_batting_in_close_matches = """
SELECT
    "Match ID",
    batsman AS player_id,
    runs,
    team
FROM
    t20_bat
WHERE
    "Match ID" IN ({}) AND runs IS NOT NULL;
"""

query_odi_player_names_q15 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q15 = """SELECT player_id, player_name FROM t20_player;"""

query_close_odi_results_q15 = """
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    odi_match
WHERE
    "Match ID" IN ({});
"""
query_close_t20_results_q15 = """
SELECT
    "Match ID",
    "Match Result Text",
    "Team1 Name",
    "Team2 Name"
FROM
    t20_match
WHERE
    "Match ID" IN ({});
"""

query_odi_yearly_batting = """
SELECT
    ob.batsman AS player_id,
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) AS match_year,
    SUM(ob.runs) AS total_runs,
    SUM(ob.balls) AS total_balls,
    COUNT(DISTINCT om."Match ID") AS matches_played
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID"
WHERE
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) >= 2020 AND ob.runs IS NOT NULL
GROUP BY
    ob.batsman, match_year;
"""

query_t20_yearly_batting = """
SELECT
    tb.batsman AS player_id,
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) AS match_year,
    SUM(tb.runs) AS total_runs,
    SUM(tb.balls) AS total_balls,
    COUNT(DISTINCT tm."Match ID") AS matches_played
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID"
WHERE
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) >= 2020 AND tb.runs IS NOT NULL
GROUP BY
    tb.batsman, match_year;
"""

query_odi_player_names_q16 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q16 = """SELECT player_id, player_name FROM t20_player;"""


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

query_odi_player_names_q18 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q18 = """SELECT player_id, player_name FROM t20_player;"""


query_odi_consistency = """
SELECT
    ob.batsman AS player_id,
    ob.runs,
    ob.balls,
    om."Match Date" AS match_date
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID"
WHERE
    CAST(SUBSTR(om."Match Date", 1, 4) AS INTEGER) >= 2022
    AND ob.balls IS NOT NULL
    AND ob.balls >= 10;
"""

query_t20_consistency = """
SELECT
    tb.batsman AS player_id,
    tb.runs,
    tb.balls,
    tm."Match Date" AS match_date
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID"
WHERE
    CAST(SUBSTR(tm."Match Date", 1, 4) AS INTEGER) >= 2022
    AND tb.balls IS NOT NULL
    AND tb.balls >= 10;
"""

query_odi_player_names_q19 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q19 = """SELECT player_id, player_name FROM t20_player;"""


query_test_batting_q20 = """
SELECT
    Player,
    'Test' AS Format,
    Mat AS MatchesPlayed,
    Inns AS Innings,
    Runs,
    NO AS NotOut
FROM
    batt_test_stats;
"""
query_odi_batting_q20 = """
SELECT
    Player,
    'ODI' AS Format,
    Mat AS MatchesPlayed,
    Inns AS Innings,
    Runs,
    NO AS NotOut
FROM
    batt_odi_stats;
"""
query_t20_batting_q20 = """
SELECT
    Player,
    'T20' AS Format,
    Mat AS MatchesPlayed,
    Inns AS Innings,
    Runs,
    NO AS NotOut
FROM
    batt_t20_stats;
"""

query_test_batting_q21 = """SELECT Player, Runs, Ave AS BattingAverage, Inns FROM batt_test_stats;"""
query_odi_batting_q21 = """SELECT Player, Runs, Ave AS BattingAverage, SR AS StrikeRate, Inns FROM batt_odi_stats;"""
query_t20_batting_q21 = """SELECT Player, Runs, Ave AS BattingAverage, SR AS StrikeRate, Inns FROM batt_t20_stats;"""

query_test_bowling_q21 = """SELECT Player, Wkts AS Wickets, Ave AS BowlingAverage, Econ AS EconomyRate FROM bowl_test_stats;"""
query_odi_bowling_q21 = """SELECT Player, Wkts AS Wickets, Ave AS BowlingAverage, Econ AS EconomyRate FROM bowl_odi_stats;"""
query_t20_bowling_q21 = """SELECT Player, Wkts AS Wickets, Ave AS BowlingAverage, Econ AS EconomyRate FROM bowl_t20_stats;"""

query_test_fielding_q21 = """SELECT Player, Ct AS Catches, St AS Stumpings FROM field_test_stats;"""
query_odi_fielding_q21 = """SELECT Player, Ct AS Catches, St AS Stumpings FROM field_odi_stats;"""
query_t20_fielding_q21 = """SELECT Player, Ct AS Catches, St AS Stumpings FROM field_t20_stats;"""

query_recent_odi_matches_q22 = """
SELECT
    "Match ID",
    "Match Date",
    "Team1 Name",
    "Team2 Name",
    "Match Result Text",
    "Team1 Runs Scored",
    "Team2 Runs Scored",
    "Team1 Wickets Fell",
    "Team2 Wickets Fell",
    "Toss Winner",
    "Toss Winner Choice",
    "Match Venue (Country)" AS VenueCountry
FROM
    odi_match
WHERE
    CAST(SUBSTR("Match Date", 1, 4) AS INTEGER) >= {};
"""

query_recent_t20_matches_q22 = """
SELECT
    "Match ID",
    "Match Date",
    "Team1 Name",
    "Team2 Name",
    "Match Result Text",
    "Team1 Runs Scored",
    "Team2 Runs Scored",
    "Team1 Wickets Fell",
    "Team2 Wickets Fell",
    "Toss Winner",
    "Toss Winner Choice",
    "Match Venue (Country)" AS VenueCountry
FROM
    t20_match
WHERE
    CAST(SUBSTR("Match Date", 1, 4) AS INTEGER) >= {};
"""

query_odi_batting_performance = """
SELECT
    ob.batsman AS player_id,
    ob.runs,
    ob.balls,
    om."Match Date" AS match_date
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID"
WHERE
    ob.runs IS NOT NULL AND ob.balls IS NOT NULL;
"""

query_t20_batting_performance = """
SELECT
    tb.batsman AS player_id,
    tb.runs,
    tb.balls,
    tm."Match Date" AS match_date
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID"
WHERE
    tb.runs IS NOT NULL AND tb.balls IS NOT NULL;
"""

query_odi_player_names_q23 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q23 = """SELECT player_id, player_name FROM t20_player;"""

query_odi_partnerships_q24 = """
SELECT
    player1,
    player2,
    "partnership runs",
    innings,
    "Match ID"
FROM
    odi_pat;
"""

query_t20_partnerships_q24 = """
SELECT
    player1,
    player2,
    "partnership runs",
    innings,
    "Match ID"
FROM
    t20_pat;
"""

query_innings_partnerships_q24 = """
SELECT
    bat1Id,
    bat2Id,
    totalRuns,
    inningsId,
    matchId
FROM
    innings_stats
WHERE
    playerType = 'Partnership';
"""

query_odi_player_names_q24 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q24 = """SELECT player_id, player_name FROM t20_player;"""
query_players_names_conn3_q24 = """SELECT id AS player_id, fullName AS player_name FROM players;"""

query_odi_batting_q25 = """
SELECT
    ob.batsman AS player_id,
    ob.runs,
    ob.balls,
    om."Match Date" AS match_date,
    om."Match ID" AS "Match ID"
FROM
    odi_bat ob
JOIN
    odi_match om ON ob."Match ID" = om."Match ID";
"""

query_t20_batting_q25 = """
SELECT
    tb.batsman AS player_id,
    tb.runs,
    tb.balls,
    tm."Match Date" AS match_date,
    tm."Match ID" AS "Match ID"
FROM
    t20_bat tb
JOIN
    t20_match tm ON tb."Match ID" = tm."Match ID";
"""

query_odi_player_names_q25 = """SELECT player_id, player_name FROM odi_player;"""
query_t20_player_names_q25 = """SELECT player_id, player_name FROM t20_player;"""
query_players_names_conn3_q25 = """SELECT id AS player_id, fullName AS player_name FROM players;"""


# Streamlit UI
st.title("Cricket Data Analysis")

st.write("""
Explore various cricket statistics and analyses by selecting a question from the dropdown below.
The results will be displayed based on the selected query and data processing.
""")

# Define the questions as a dictionary with question text and corresponding function
questions = {
    "Question 1: Find all players who represent India.": question1,
    "Question 2: Show all cricket matches that were played in the last 30 days.": question2,
    "Question 3: List the top 10 highest run scorers in ODI cricket.": question3,
    "Question 4: Display all cricket venues that have a seating capacity of more than 50,000 spectators.": question4,
    "Question 5: Calculate how many matches each team has won.": question5,
    "Question 6: Count how many players belong to each playing role.": question6,
    "Question 7: Find the highest individual batting score in each format.": question7,
    "Question 8: Show all cricket series that started in the year 2024.": question8,
    "Question 9: Find all-rounder players with more than 1000 runs and 50 wickets.": question9,
    "Question 10: Get details of the last 20 completed matches.": question10,
    "Question 11: Compare each player's performance across different cricket formats.": question11,
    "Question 12: Analyze international team's home vs. away performance.": question12,
    "Question 13: Identify batting partnerships with 100+ runs.": question13,
    "Question 14: Examine bowling performance at different venues.": question14,
    "Question 15: Identify players who perform well in close matches.": question15,
    "Question 16: Track how players' batting performance changes over different years (since 2020).": question16,
    "Question 17: Investigate whether winning the toss gives teams an advantage.": question17,
    "Question 18: Find the most economical bowlers in limited-overs cricket.": question18,
    "Question 19: Determine which batsmen are most consistent in their scoring (since 2022).": question19,
    "Question 20: Analyze player match counts and batting averages across formats.": question20,
    "Question 21: Create a comprehensive performance ranking system for players.": question21,
    "Question 22: Build a head-to-head match prediction analysis between teams.": question22,
    "Question 23: Analyze recent player form and momentum.": question23,
    "Question 24: Study successful batting partnerships to identify the best player combinations.": question24,
    "Question 25: Perform a time-series analysis of player performance evolution.": question25,
}

selected_question = st.selectbox("Select a question:", list(questions.keys()))

st.header(selected_question)

if selected_question:
    query_function = questions[selected_question]

    try:
        result = query_function()

        if isinstance(result, pd.DataFrame):
            st.write("Results:")
            st.dataframe(result)
        elif isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], pd.DataFrame) and isinstance(result[1], plt.Figure):
            st.write("Results:")
            st.dataframe(result[0])
            st.pyplot(result[1])
        else:
            st.write("Unexpected result format.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
