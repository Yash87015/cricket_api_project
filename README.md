# cricket_api_project

---
streamlit :- https://cricketapiproject-w8k27gnj8bydfjxubneujm.streamlit.app
🏏 Cricket Analytics Dashboard

📌 Project Overview

The Cricket Analytics Dashboard is an end-to-end data engineering and analytics project built with Streamlit Cloud and SQLite databases.
It integrates live cricket data (via Cricbuzz API) with historical match databases to deliver:

- Real-time match tracking
- Player and team statistics
- Custom SQL-driven insights
- CRUD operations for learning database management
- Interactive dashboards deployed on the web
- This project demonstrates the full data pipeline:

> Fetch Data → Store in Databases → Run SQL Queries → Build Analytics → Deploy Streamlit Multipage App on GitHub + Streamlit Cloud

---

⚙️ Tools & Technologies

Python (data fetching, transformations, analytics)

Streamlit (dashboard, multipage UI, deployment)

SQLite (database storage, multiple DBs for ODI, T20, Cricbuzz meta data)

Pandas (data manipulation & integration)

Cricbuzz API (live cricket data: matches, players, series, stats)

GitHub + Streamlit Cloud (CI/CD deployment)



---

📂 Project Structure

Cricket-Analytics-Dashboard/
│
├── main.py                     # Home Page (intro, navigation)
├── pages/                      # Streamlit multipage directory
│   ├── Live_Matches.py         # Live matches dashboard
│   ├── Top_Player_Stats.py     # Leaderboards (batting & bowling)
│   ├── CRUD_Operation_Page.py  # Create, Read, Update, Delete on DB
│   ├── Queries_Analytics_Page.py # 25 SQL-driven analytical questions
│   
│
├── databases/                  # SQLite Databases
│   ├── odi.db
│   ├── t20.db
│   ├── crickbuzz.db
│   └── stats.db
│
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation


---

🚀 Features

1️⃣ Live Matches Page

Fetches real-time live data via Cricbuzz API

Displays match ID, series name, format, state, status, team names

Auto-refresh to always show ongoing cricket matches


2️⃣ Top Player Stats Page

Displays top batting & bowling stats using Cricbuzz API

Categories: Most Runs, Highest Score, Most Wickets, Best Averages, etc.

Clean visualization with Streamlit + charts


3️⃣ CRUD Operations Page

Full Create, Read, Update, Delete functionality

Operates on players and matches tables inside SQLite DBs

Form-based UI → great for learning database operations


4️⃣ Queries _ Analytics Page

The heart of the project 💡

Contains 25 SQL-driven analytical questions, including:

Players representing India

Matches in the last 30 days

Top 10 ODI run scorers

Venues with 50,000+ capacity

Teams’ home vs away performance

Toss impact analysis

Most consistent batsmen

Successful batting partnerships

Player performance evolution (time-series analysis)


Results displayed as interactive tables + charts


5️⃣ Home Page

Provides project introduction

Explains navigation between pages

Quick links to documentation



---

📊 Example Analytics Questions (from Queries & Analytics Page)

Q5: How many matches has each team won?

Q11: Compare player performance across formats (Test, ODI, T20).

Q17: Does winning the toss improve win probability?

Q19: Who are the most consistent batsmen since 2022?

Q25: Time-series analysis of career trajectory (ascending, declining, stable).



---

🗄️ Database Design

odi.db → ODI historical stats

t20.db → T20 historical stats

crickbuzz.db → Meta data: players, venues, live matches

stats.db → Additional stats (optional, for extended analytics)


All DB connections use:

import os, sqlite3
db_path = os.path.join(os.path.dirname(os.path.dirname(_file_)), "odi.db")
conn = sqlite3.connect(db_path)

✅ This ensures paths work in Streamlit multipage apps.


---

🛠️ How to Run Locally

1. Clone the repository:

git clone https://github.com/Yash87015/cricket_api_project/tree/main
cd Cricket-Analytics-Dashboard


2. Install dependencies:

pip install -r requirements.txt


3. Run Streamlit app:

streamlit run main.py




---

☁️ Deployment (Streamlit Cloud)

1. Push this project to GitHub.


2. Go to Streamlit Cloud.


3. Link your GitHub repo.


4. Set the main file as main.py.


5. Deploy 🚀 → Your app goes live with all pages integrated.




---

📖 Documentation

Project Report: This README file

Folder Structure & Navigation: Explained above

Database Schema: Each DB file contains player stats, matches, and metadata

Queries: All 25 queries documented inside Queries_Analytics_Page.py



---

🎯 Learning Outcomes

By completing this project, you learn:

Fetching & integrating live API data

Designing & querying SQLite databases

Performing advanced SQL analytics (25 real-world cricket queries)

Building Streamlit multipage dashboards

Deploying apps via GitHub → Streamlit Cloud



---

✅ Future Enhancements

Add machine learning models (match predictions, player performance forecasting).

Integrate more historical data (Test matches, IPL).

Add user authentication for personalized dashboards.

Build REST API endpoints for analytics results.



---
