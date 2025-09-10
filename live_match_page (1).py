import streamlit as st
import requests
import pandas as pd
import time

url_live = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
url_upcoming = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
url_recent = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"

headers = {
    "x-rapidapi-key": "7cd1451496msh26d2809dcb7535ap12515bjsn5b15e7be8226", # Replace with your actual API key
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_live_matches(url, headers):
    """Fetches live match data from the Cricbuzz API with caching."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching live match data: {e}")
        return None

@st.cache_data(ttl=300) # Cache for 5 minutes (upcoming matches change less frequently)
def fetch_upcoming_matches(url, headers):
    """Fetches upcoming match data from the Cricbuzz API with caching."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching upcoming match data: {e}")
        return None

@st.cache_data(ttl=300) # Cache for 5 minutes (recent matches change less frequently)
def fetch_recent_matches(url, headers):
    """Fetches recent match data from the Cricbuzz API with caching."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recent match data: {e}")
        return None

def process_recent_matches(data):
    """Processes recent match data to extract team and venue details."""
    recent_match_data = []
    if data and 'typeMatches' in data:
        for match_type_entry in data['typeMatches']:
            if 'seriesMatches' in match_type_entry:
                for series_match_entry in match_type_entry['seriesMatches']:
                    if 'seriesAdWrapper' in series_match_entry and 'matches' in series_match_entry['seriesAdWrapper']:
                        for match in series_match_entry['seriesAdWrapper']['matches']:
                            if 'matchInfo' in match:
                                match_info = match['matchInfo']
                                extracted_details = {
                                    'matchId': match_info.get('matchId'),
                                    'seriesId': match_info.get('seriesId'),
                                    'seriesName': match_info.get('seriesName'),
                                    'matchDesc': match_info.get('matchDesc'),
                                    'matchFormat': match_info.get('matchFormat'),
                                    'startDate': match_info.get('startDate'),
                                    'endDate': match_info.get('endDate'),
                                    'state': match_info.get('state'),
                                    'status': match_info.get('status'),
                                    'currBatTeamId': match_info.get('currBatTeamId'),
                                    'seriesStartDt': match_info.get('seriesStartDt'),
                                    'seriesEndDt': match_info.get('seriesEndDt'),
                                    'isTimeAnnounced': match_info.get('isTimeAnnounced'),
                                    'stateTitle': match_info.get('stateTitle')
                                }
                                # Extract team details
                                if 'team1' in match_info:
                                    extracted_details['team1_id'] = match_info['team1'].get('teamId')
                                    extracted_details['team1_name'] = match_info['team1'].get('teamName')
                                    extracted_details['team1_sname'] = match_info['team1'].get('teamSName')
                                    extracted_details['team1_image_id'] = match_info['team1'].get('imageId')
                                else:
                                    extracted_details['team1_id'] = None
                                    extracted_details['team1_name'] = None
                                    extracted_details['team1_sname'] = None
                                    extracted_details['team1_image_id'] = None

                                if 'team2' in match_info:
                                    extracted_details['team2_id'] = match_info['team2'].get('teamId')
                                    extracted_details['team2_name'] = match_info['team2'].get('teamName')
                                    extracted_details['team2_sname'] = match_info['team2'].get('teamSName')
                                    extracted_details['team2_image_id'] = match_info['team2'].get('imageId')
                                else:
                                    extracted_details['team2_id'] = None
                                    extracted_details['team2_name'] = None
                                    extracted_details['team2_sname'] = None
                                    extracted_details['team2_image_id'] = None

                                # Extract venue details
                                if 'venueInfo' in match_info:
                                    extracted_details['venue_id'] = match_info['venueInfo'].get('id')
                                    extracted_details['ground'] = match_info['venueInfo'].get('ground')
                                    extracted_details['city'] = match_info['venueInfo'].get('city')
                                    extracted_details['timezone'] = match_info['venueInfo'].get('timezone')
                                    extracted_details['latitude'] = match_info['venueInfo'].get('latitude')
                                    extracted_details['longitude'] = match_info['venueInfo'].get('longitude')
                                else:
                                    extracted_details['venue_id'] = None
                                    extracted_details['ground'] = None
                                    extracted_details['city'] = None
                                    extracted_details['timezone'] = None
                                    extracted_details['latitude'] = None
                                    extracted_details['longitude'] = None

                                # Extract overs from matchScore if available
                                if 'matchScore' in match:
                                    if 'team1Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team1Score']:
                                        extracted_details['team1_overs'] = match['matchScore']['team1Score']['inngs1'].get('overs')
                                    else:
                                        extracted_details['team1_overs'] = None

                                    if 'team2Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team2Score']:
                                        extracted_details['team2_overs'] = match['matchScore']['team2Score']['inngs1'].get('overs')
                                    else:
                                        extracted_details['team2_overs'] = None
                                else:
                                    extracted_details['team1_overs'] = None
                                    extracted_details['team2_overs'] = None

                                recent_match_data.append(extracted_details)
    return pd.DataFrame(recent_match_data)

def display_live_matches(data):
    """Processes and displays live match data in the Streamlit app."""
    st.header("Live Matches")
    if data and 'typeMatches' in data:
        for match_type_entry in data['typeMatches']:
            if 'seriesMatches' in match_type_entry:
                for series_match_entry in match_type_entry['seriesMatches']:
                    if 'seriesAdWrapper' in series_match_entry and 'matches' in series_match_entry['seriesAdWrapper']:
                        for match in series_match_entry['seriesAdWrapper']['matches']:
                            if 'matchInfo' in match:
                                match_info = match['matchInfo']
                                st.subheader(f"{match_info.get('seriesName', 'N/A')} - {match_info.get('matchDesc', 'N/A')}")
                                st.write(f"**Format:** {match_info.get('matchFormat', 'N/A')}")
                                st.write(f"**State:** {match_info.get('state', 'N/A')}")
                                st.write(f"**Status:** {match_info.get('status', 'N/A')}")

                                team1_name = match_info.get('team1', {}).get('teamName')
                                team2_name = match_info.get('team2', {}).get('teamName')

                                if team1_name and team2_name:
                                    st.write(f"**Teams:** {team1_name} vs {team2_name}")
                                elif team1_name:
                                    st.write(f"**Team 1:** {team1_name}")
                                elif team2_name:
                                     st.write(f"**Team 2:** {team2_name}")

                                if 'matchScore' in match:
                                    st.write("**Score:**")
                                    if 'team1Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team1Score']:
                                        score1 = match['matchScore']['team1Score']['inngs1']
                                        st.write(f"  {team1_name}: {score1.get('runs', 'N/A')}/{score1.get('wickets', 'N/A')} ({score1.get('overs', 'N/A')} Overs)")
                                    if 'team2Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team2Score']:
                                        score2 = match['matchScore']['team2Score']['inngs1']
                                        st.write(f"  {team2_name}: {score2.get('runs', 'N/A')}/{score2.get('wickets', 'N/A')} ({score2.get('overs', 'N/A')} Overs)")
                                st.markdown("---")
    else:
        st.info("No live match data available at the moment.")

def display_upcoming_matches(data):
    """Processes and displays upcoming match data in the Streamlit app."""
    st.header("Upcoming Matches")
    if data and 'typeMatches' in data:
        for match_type_entry in data['typeMatches']:
            if 'seriesMatches' in match_type_entry:
                for series_match_entry in match_type_entry['seriesMatches']:
                    if 'seriesAdWrapper' in series_match_entry and 'matches' in series_match_entry['seriesAdWrapper']:
                        for match in series_match_entry['seriesAdWrapper']['matches']:
                            if 'matchInfo' in match:
                                match_info = match['matchInfo']
                                st.subheader(f"{match_info.get('seriesName', 'N/A')} - {match_info.get('matchDesc', 'N/A')}")
                                st.write(f"**Format:** {match_info.get('matchFormat', 'N/A')}")
                                st.write(f"**State:** {match_info.get('state', 'N/A')}")
                                st.write(f"**Status:** {match_info.get('status', 'N/A')}")
                                team1_name = match_info.get('team1', {}).get('teamName')
                                team2_name = match_info.get('team2', {}).get('teamName')

                                if team1_name and team2_name:
                                    st.write(f"**Teams:** {team1_name} vs {team2_name}")
                                elif team1_name:
                                    st.write(f"**Team 1:** {team1_name}")
                                elif team2_name:
                                     st.write(f"**Team 2:** {team2_name}")
                                st.markdown("---")
    else:
        st.info("No upcoming match data available at the moment.")

def display_recent_matches(df):
    """Displays recent match data from a DataFrame in the Streamlit app."""
    st.header("Recent Matches")
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No recent match data available.")

import time

st.title("Cricket Match Updates")

# Fetch live matches and display
live_matches_data = fetch_live_matches(url_live, headers)
display_live_matches(live_matches_data)

# Fetch upcoming matches and display
upcoming_matches_data = fetch_upcoming_matches(url_upcoming, headers)
display_upcoming_matches(upcoming_matches_data)

# Fetch recent matches, process, and display
recent_matches_data_raw = fetch_recent_matches(url_recent, headers)
df_recent_matches = process_recent_matches(recent_matches_data_raw)
display_recent_matches(df_recent_matches)

# Auto-refresh mechanism (every 60 seconds)
time.sleep(60)
st.rerun()

def process_recent_matches(data):
    """Processes recent match data to extract team and venue details."""
    recent_match_data = []
    if data and 'typeMatches' in data:
        for match_type_entry in data['typeMatches']:
            if 'seriesMatches' in match_type_entry:
                for series_match_entry in series_match_entry['seriesMatches']:
                    if 'seriesAdWrapper' in series_match_entry and 'matches' in series_match_entry['seriesAdWrapper']:
                        for match in series_match_entry['seriesAdWrapper']['matches']:
                            if 'matchInfo' in match:
                                match_info = match['matchInfo']
                                extracted_details = {
                                    'matchId': match_info.get('matchId'),
                                    'seriesId': match_info.get('seriesId'),
                                    'seriesName': match_info.get('seriesName'),
                                    'matchDesc': match_info.get('matchDesc'),
                                    'matchFormat': match_info.get('matchFormat'),
                                    'startDate': match_info.get('startDate'),
                                    'endDate': match_info.get('endDate'),
                                    'state': match_info.get('state'),
                                    'status': match_info.get('status'),
                                    'currBatTeamId': match_info.get('currBatTeamId'),
                                    'seriesStartDt': match_info.get('seriesStartDt'),
                                    'seriesEndDt': match_info.get('seriesEndDt'),
                                    'isTimeAnnounced': match_info.get('isTimeAnnounced'),
                                    'stateTitle': match_info.get('stateTitle')
                                }
                                # Extract team details
                                if 'team1' in match_info:
                                    extracted_details['team1_id'] = match_info['team1'].get('teamId')
                                    extracted_details['team1_name'] = match_info['team1'].get('teamName')
                                    extracted_details['team1_sname'] = match_info['team1'].get('teamSName')
                                    extracted_details['team1_image_id'] = match_info['team1'].get('imageId')
                                else:
                                    extracted_details['team1_id'] = None
                                    extracted_details['team1_name'] = None
                                    extracted_details['team1_sname'] = None
                                    extracted_details['team1_image_id'] = None

                                if 'team2' in match_info:
                                    extracted_details['team2_id'] = match_info['team2'].get('teamId')
                                    extracted_details['team2_name'] = match_info['team2'].get('teamName')
                                    extracted_details['team2_sname'] = match_info['team2'].get('teamSName')
                                    extracted_details['team2_image_id'] = match_info['team2'].get('imageId')
                                else:
                                    extracted_details['team2_id'] = None
                                    extracted_details['team2_name'] = None
                                    extracted_details['team2_sname'] = None
                                    extracted_details['team2_image_id'] = None

                                # Extract venue details
                                if 'venueInfo' in match_info:
                                    extracted_details['venue_id'] = match_info['venueInfo'].get('id')
                                    extracted_details['ground'] = match_info['venueInfo'].get('ground')
                                    extracted_details['city'] = match_info['venueInfo'].get('city')
                                    extracted_details['timezone'] = match_info['venueInfo'].get('timezone')
                                    extracted_details['latitude'] = match_info['venueInfo'].get('latitude')
                                    extracted_details['longitude'] = match_info['venueInfo'].get('longitude')
                                else:
                                    extracted_details['venue_id'] = None
                                    extracted_details['ground'] = None
                                    extracted_details['city'] = None
                                    extracted_details['timezone'] = None
                                    extracted_details['latitude'] = None
                                    extracted_details['longitude'] = None

                                # Extract overs from matchScore if available
                                if 'matchScore' in match:
                                    if 'team1Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team1Score']:
                                        extracted_details['team1_overs'] = match['matchScore']['team1Score']['inngs1'].get('overs')
                                    else:
                                        extracted_details['team1_overs'] = None

                                    if 'team2Score' in match['matchScore'] and 'inngs1' in match['matchScore']['team2Score']:
                                        extracted_details['team2_overs'] = match['matchScore']['team2Score']['inngs1'].get('overs')
                                    else:
                                        extracted_details['team2_overs'] = None
                                else:
                                    extracted_details['team1_overs'] = None
                                    extracted_details['team2_overs'] = None

                                recent_match_data.append(extracted_details)

    df_recent_matches = pd.DataFrame(recent_match_data)

    # Convert date columns to datetime objects
    date_cols = ['startDate', 'endDate', 'seriesStartDt', 'seriesEndDt']
    for col in date_cols:
        if col in df_recent_matches.columns:
            df_recent_matches[col] = pd.to_datetime(df_recent_matches[col], unit='ms', errors='coerce')

    # Fill NaN values in overs and currBatTeamId columns
    if 'team1_overs' in df_recent_matches.columns:
        df_recent_matches['team1_overs'].fillna(df_recent_matches['team1_overs'].mode()[0] if not df_recent_matches['team1_overs'].empty else 0, inplace=True)
    if 'team2_overs' in df_recent_matches.columns:
        df_recent_matches['team2_overs'].fillna(df_recent_matches['team2_overs'].mode()[0] if not df_recent_matches['team2_overs'].empty else 0, inplace=True)
    if 'currBatTeamId' in df_recent_matches.columns:
        df_recent_matches['currBatTeamId'].fillna(df_recent_matches['currBatTeamId'].mode()[0] if not df_recent_matches['currBatTeamId'].empty else 0, inplace=True)


    return df_recent_matches
