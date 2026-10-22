# 🌍 Travele — Smart Travel Companion & AI Destination Explorer

[![Python Version](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-000000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000.svg?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![AI Studio](https://img.shields.io/badge/AI-AI%20Studio%20Engine-4285F4.svg?style=for-the-badge&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](#)

**Travele** is an interactive, intelligent web application designed to help travelers search, discover, and plan their journeys across world cities and tourist destinations. It aggregates live weather forecasts, seasonal trip recommendations, popular historical landmarks, Wikipedia city insights, and real-time itinerary generation powered by **AI Studio Neural Engine**.

---

## ✨ Features

- 🔍 **Real-Time City Search & Auto-suggestions**: Instant search with typeahead location suggestions powered by Open-Meteo Geocoding.
- 🌤️ **Live Weather Updates**: Live temperature, weather condition code, wind speeds, and relative humidity for any global city.
- 🏛️ **Top Attractions & Landmark Discovery**: Automatically retrieves top monuments, museums, parks, and viewpoints using Wikipedia API with image previews and summaries.
- ☀️ ❄️ 🌧️ **Seasonal Categorization**: Categorizes places into Summer, Winter, and Monsoon recommendations based on landmark characteristics.
- 🤖 **Smart AI Travel Planner**: Custom day-by-day itineraries and travel advisory generated in real time.
- 🌐 **Country & Currency Details**: Retrieves official currencies, languages, timezones, and national flags via RestCountries API.
- 🎙️ **Voice Search**: Hands-free voice recognition support for destination lookups.
- 📱 **Fully Responsive UI**: Modern glassmorphic interface designed for seamless mobile and desktop browsing.
- ⚡ **Serverless Ready**: Built with `vercel.json` for one-click deployment on Vercel.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, SQLite
- **AI Engine**: AI Studio Neural Engine
- **Frontend**: HTML5, Modern CSS3 (Glassmorphism), JavaScript (ES6+ Fetch API, Web Speech API)
- **External Data APIs**:
  - [Open-Meteo API](https://open-meteo.com/) (Geocoding & Forecast)
  - [MediaWiki / Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) (Places, Photos, Extracts)
  - [REST Countries API](https://restcountries.com/) (Country & Currency data)

---

## 📁 Project Structure

```text
travele/
├── static/
│   ├── script.js        # Frontend logic, API callers, UI event handlers
│   └── style.css        # Glassmorphic UI styling
├── templates/
│   ├── index.html       # Single-page application interface
│   └── admin.html       # Admin analytics & metrics
├── app.py               # Flask application server & API routes
├── travele_auth.db      # SQLite user authentication database
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel Serverless WSGI configuration
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.8 or above installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/harshitmeena200515-cyber/travel-companion-guide.git
cd travel-companion-guide
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## ☁️ Deploying to Vercel

This repository is pre-configured with `vercel.json` for serverless deployment:
1. Import the repository `travel-companion-guide` on [Vercel](https://vercel.com/new).
2. Set the framework preset to **Other** (Vercel automatically detects `vercel.json` and Python runtime).
3. (Optional) Add your `AI_API_KEY` under Environment Variables in the Vercel project settings.
4. Click **Deploy**.

---

## 👨‍💻 Author
Developed by **Harshit Meena**.
