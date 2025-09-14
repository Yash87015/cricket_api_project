import streamlit as st

# -------------------
# Page Config
# -------------------
st.set_page_config(
    page_title="🏏 Cricket Analytics Dashboard",
    layout="wide"
)

# -------------------
# Title & Intro
# -------------------
st.title("🏏 Cricket Analytics Dashboard")
st.markdown("## Project Overview")

st.write(
    """
    This project is a **Cricket Analytics Dashboard** built with **Streamlit**, powered by data 
    from the **Cricbuzz API** and stored in a **SQLite database**.  
    The dashboard provides insights into cricket series, players, and matches, with features like:  

    - 📡 **Live Match Page** → Fetch and display live scores  
    - 📊 **Top Player Stats** → Batting & Bowling leaders  
    - 🛠️ **CRUD Operations** → Create, Read, Update, Delete match & player stats  
    - 🔍 **Queries & Analysis** → Explore advanced cricket insights  

    ---
    """
)

# -------------------
# Tools Used
# -------------------
st.subheader("🛠️ Tools & Technologies Used")
st.markdown(
    """
    - **Python 3.10+**  
    - **Streamlit** → For building interactive dashboards  
    - **SQLite3** → Local database for match & player records  
    - **Pandas** → Data manipulation  
    - **Matplotlib / Plotly** → Data visualization  
    - **Cricbuzz API (via RapidAPI)** → Real-time cricket data  
    - **GitHub** → Version control & collaboration  
    """
)

# -------------------
# Instructions
# -------------------
st.subheader("🚀 Instructions to Run the Project")
st.markdown(
    """
    1. Clone this repository:  
       ```bash
       git clone https://github.com/Yash87015/cricket_api_project
       cd cricket-analytics
       ```

    2. Install required dependencies:  
       ```bash
       pip install -r requirements.txt
       ```

    3. Run the Streamlit app:  
       ```bash
       streamlit run main.py
       ```

    4. Use the **sidebar navigation** to switch between pages:
       - 📡 **Live Match Page**
       - 📊 **Top Player Stats**
       - 🛠️ **CRUD Operations**
       - 🔍 **Queries & Analysis**
    """
)

# -------------------
# Documentation
# -------------------
st.subheader("📄 Project Documentation")
st.markdown(
    """
    Full documentation is available here:  
    [📘 Cricket Analytics Documentation](https://github.com/your-username/cricket-analytics/wiki)  

    ---
    """
)

# -------------------
# Folder Structure
# -------------------
st.subheader("📂 Folder Structure")
st.code(
    """
    cricket-analytics/
    ├── main.py                     # Home page (Project Overview)
    ├── pages/
    │   ├── live_match_page.py      # Live scores page (Cricbuzz API)
    │   ├── top_player_stats.py     # Top batting & bowling stats
    │   ├── crud_operation_page.py  # CRUD operations on database
    │   ├── queries_page.py         # Custom cricket insights
    ├── crickbuzz.db                # SQLite database with match/player stats
    ├── requirements.txt            # Python dependencies
    ├── README.md                   # Documentation & instructions
    └── .gitignore                  # Ignore unnecessary files
    """
)

# -------------------
# Footer
# -------------------
st.markdown("---")
st.success("✅ Use the sidebar to navigate between pages")
