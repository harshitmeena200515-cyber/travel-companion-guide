# 🌍 Travele — Smart Travel Companion & Destination Explorer

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](#)

**Travele** is an interactive, intelligent web application designed to help travelers search, discover, and plan their journeys across world cities and tourist destinations. It aggregates live weather forecasts, seasonal trip recommendations, popular historical landmarks, Wikipedia city insights, and real-time geocoding.

---

## ✨ Features

- 🔍 **Real-Time City Search & Auto-suggestions**: Instant search with typeahead location suggestions powered by Open-Meteo Geocoding.
- 🌤️ **Live Weather Updates**: Live temperature, weather condition code, wind speeds, and relative humidity for any global city.
- 🏛️ **Top Attractions & Landmark Discovery**: Automatically retrieves top monuments, museums, parks, and viewpoints using Wikipedia API with image previews and summaries.
- ☀️ ❄️ 🌧️ **Seasonal Categorization**: Categorizes places into Summer, Winter, and Monsoon recommendations based on landmark characteristics.
- 🌐 **Country & Currency Details**: Retrieves official currencies, languages, timezones, and national flag representations via RestCountries API.
- 🎙️ **Voice Search**: Hands-free voice recognition support for destination lookups.
- 📱 **Fully Responsive UI**: Modern, sleek glassmorphic user interface designed for both mobile and desktop screens.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Requests
- **Frontend**: HTML5, Modern CSS3 (Glassmorphism & Flexbox/Grid), JavaScript (ES6+ Fetch API, Web Speech API)
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
│   └── style.css        # Clean, modern UI styling
├── templates/
│   └── index.html       # Single-page application interface
├── app.py               # Flask application server & API routes
├── convert.py           # Report formatting utility
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore configurations (protects venv, secrets)
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

Open your browser and navigate to `http://localhost:5000` to start exploring!

---

## 🔒 Privacy & Security

This project contains zero hardcoded API keys or private credentials. It exclusively utilizes publicly available, open-access endpoints and adheres to modern security and data privacy standards.

---

## 📜 License

This project is licensed under the MIT License - feel free to use and modify for personal or academic projects.
