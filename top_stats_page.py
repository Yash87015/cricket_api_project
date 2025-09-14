 import streamlit as st
import pandas as pd
import requests

def top_stats_page():
    """Streamlit page to display top cricket statistics."""
    st.title("Top Cricket Statistics")

def top_stats_page():
    """Streamlit page to display top cricket statistics."""
    st.title("Top Cricket Statistics")

    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0" # Using 0 for overall stats

    headers = {
        "x-rapidapi-key": "af412425bamsh0d5d43bcb05971ap11b4ccjsn1e3f99f58a33", # Replace with your actual API key
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    # Fetch Most Runs data
    querystring_runs = {"statsType":"mostRuns"}

    try:
        response_runs = requests.get(url, headers=headers, params=querystring_runs)
        response_runs.raise_for_status()  # Raise an HTTPError for bad responses
        data_runs = response_runs.json()

        # Process Most Runs data
        top_batting_stats = []
        if 'topPerformance' in data_runs and 'sections' in data_runs['topPerformance']:
            for section in data_runs['topPerformance']['sections']:
                if 'categories' in section:
                    for category in section['categories']:
                        if 'rankings' in category:
                            for ranking in category['rankings']:
                                player_data = {
                                    'category_name': category.get('categoryName'),
                                    'rank': ranking.get('rank'),
                                    'player_id': ranking.get('playerId'),
                                    'player_name': ranking.get('playerName'),
                                    'team_id': ranking.get('teamId'),
                                    'team_name': ranking.get('teamName'),
                                    'value': ranking.get('value'), # The stat value (e.g., runs)
                                    'innings': ranking.get('innings'),
                                    'matches': ranking.get('matches')
                                }
                                top_batting_stats.append(player_data)
        elif 'headers' in data_runs and 'values' in data_runs:
            # Handle the case where the structure is different (observed in previous attempts)
            headers_runs = data_runs.get('headers', [])
            values_runs = data_runs.get('values', [])
            extracted_data_runs = []
            if headers_runs and values_runs:
                stat_headers_runs = headers_runs[1:]
                for entry in values_runs:
                    if 'values' in entry and len(entry['values']) > 1:
                        player_info = {'player_id': entry['values'][0]}
                        stats = entry['values'][1:]
                        player_stats = {}
                        for i in range(min(len(stats), len(stat_headers_runs))):
                            player_stats[stat_headers_runs[i]] = stats[i]
                        combined_data = {**player_info, **player_stats}
                        extracted_data_runs.append(combined_data)
            top_batting_stats = extracted_data_runs


        df_most_runs = pd.DataFrame(top_batting_stats)

        # Display Most Runs
        st.header("Most Runs (Overall)")
        if not df_most_runs.empty:
            st.dataframe(df_most_runs)
        else:
            st.info("No data available for Most Runs.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Most Runs data: {e}")

    # Fetch Most Wickets data
    querystring_wickets = {"statsType":"mostWickets"}

    try:
        response_wickets = requests.get(url, headers=headers, params=querystring_wickets)
        response_wickets.raise_for_status()  # Raise an HTTPError for bad responses
        data_wickets = response_wickets.json()

        # Process Most Wickets data
        extracted_wickets_data = []
        if 'topPerformance' in data_wickets and 'sections' in data_wickets['topPerformance']:
            for section in data_wickets['topPerformance']['sections']:
                if 'categories' in section:
                    for category in section['categories']:
                        if 'rankings' in category:
                            for ranking in category['rankings']:
                                player_data = {
                                    'category_name': category.get('categoryName'),
                                    'rank': ranking.get('rank'),
                                    'player_id': ranking.get('playerId'),
                                    'player_name': ranking.get('playerName'),
                                    'team_id': ranking.get('teamId'),
                                    'team_name': ranking.get('teamName'),
                                    'value': ranking.get('value'), # The stat value (e.g., wickets)
                                    'innings': ranking.get('innings'),
                                    'matches': ranking.get('matches')
                                }
                                extracted_wickets_data.append(player_data)
        elif 'headers' in data_wickets and 'values' in data_wickets:
            # Handle the case where the structure is different (observed in previous attempts)
            headers_wickets = data_wickets.get('headers', [])
            values_wickets = data_wickets.get('values', [])
            if headers_wickets and values_wickets:
                stat_headers_wickets = headers_wickets[1:]
                for entry in values_wickets:
                    if 'values' in entry and len(entry['values']) > 1:
                        player_info = {'player_id': entry['values'][0]}
                        stats = entry['values'][1:]
                        player_stats = {}
                        for i in range(min(len(stats), len(stat_headers_wickets))):
                            player_stats[stat_headers_wickets[i]] = stats[i]
                        combined_data = {**player_info, **player_stats}
                        extracted_wickets_data.append(combined_data)


        df_most_wickets = pd.DataFrame(extracted_wickets_data)

        # Display Most Wickets
        st.header("Most Wickets (Overall)")
        if not df_most_wickets.empty:
            st.dataframe(df_most_wickets)
        else:
            st.info("No data available for Most Wickets.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Most Wickets data: {e}")

    # Fetch Highest Score data
    querystring_highest_score = {"statsType":"highestScore"}

    try:
        response_highest_score = requests.get(url, headers=headers, params=querystring_highest_score)
        response_highest_score.raise_for_status()  # Raise an HTTPError for bad responses
        data_highest_score = response_highest_score.json()

        # Process Highest Score data
        extracted_highest_score_data = []
        if 'topPerformance' in data_highest_score and 'sections' in data_highest_score['topPerformance']:
            for section in data_highest_score['topPerformance']['sections']:
                if 'categories' in section:
                    for category in section['categories']:
                        if 'rankings' in category:
                            for ranking in category['rankings']:
                                player_data = {
                                    'category_name': category.get('categoryName'),
                                    'rank': ranking.get('rank'),
                                    'player_id': ranking.get('playerId'),
                                    'player_name': ranking.get('playerName'),
                                    'team_id': ranking.get('teamId'),
                                    'team_name': ranking.get('teamName'),
                                    'value': ranking.get('value'), # The stat value (e.g., runs)
                                    'innings': ranking.get('innings'),
                                    'matches': ranking.get('matches')
                                }
                                extracted_highest_score_data.append(player_data)
        elif 'headers' in data_highest_score and 'values' in data_highest_score:
            # Handle the case where the structure is different (observed in previous attempts)
            headers_highest_score = data_highest_score.get('headers', [])
            values_highest_score = data_highest_score.get('values', [])
            if headers_highest_score and values_highest_score:
                stat_headers_highest_score = headers_highest_score[1:]
                for entry in values_highest_score:
                    if 'values' in entry and len(entry['values']) > 1:
                        player_info = {'player_id': entry['values'][0]}
                        stats = entry['values'][1:]
                        player_stats = {}
                        for i in range(min(len(stats), len(stat_headers_highest_score))):
                            player_stats[stat_headers_highest_score[i]] = stats[i]
                        combined_data = {**player_info, **player_stats}
                        extracted_highest_score_data.append(combined_data)

        df_highest_score = pd.DataFrame(extracted_highest_score_data)


        # Display Highest Score
        st.header("Highest Score (Overall)")
        if not df_highest_score.empty:
            st.dataframe(df_highest_score)
        else:
            st.info("No data available for Highest Score.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Highest Score data: {e}")
