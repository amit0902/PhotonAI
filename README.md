# Solar AI Advisor ☀️

AI-powered rooftop solar advisory platform that designs solar systems based on user energy usage.

## Features

• Conversational solar consultation  
• PV system simulation using PVlib  
• Financial ROI analysis  
• Government subsidy calculation  
• Break-even visualization  
• Solar consultancy PDF proposal  

## Architecture

User Chat → LangGraph Agents → PVlib Simulation → Financial Analysis → PDF Proposal

## Tech Stack

Python  
Streamlit  
LangGraph  
PVlib  
Plotly  
SQLite  
ReportLab  

## Run Locally

Clone repo

git clone https://github.com/yourusername/solar-ai-advisor.git

Install dependencies

pip install -r requirements.txt

Create `.env`

GROQ_API_KEY=your_key_here

Run application

streamlit run app.py
