import os
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "travele-secure-secret-key-harshit-2026")

DB_PATH = os.path.join(os.path.dirname(__file__), "travele_auth.db")

# Open-Meteo Geocoding API
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
# Open-Meteo Weather API
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
# Wikipedia API
WIKI_URL = "https://en.wikipedia.org/w/api.php"

def get_gemini_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, encoding='utf-8') as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        key = line.strip().split("=", 1)[1]
    return key

def call_gemini(prompt, system_instruction=None):
    key = get_gemini_key()
    if not key:
        return "⚠️ Google AI Studio GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your environment or .env file."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={key}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"AI Studio Error ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Network Exception: {str(e)}"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            city TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_pwd = generate_password_hash("HarshitTravelAdmin2026!")
        c.execute("INSERT INTO users (username, password_hash, role) VALUES ('admin', ?, 'admin')", (admin_pwd,))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# ─── GOOGLE AI STUDIO (GEMINI) ENDPOINTS ─────────────────────────

@app.route('/api/ai/plan', methods=['POST'])
def ai_plan():
    data = request.get_json() or {}
    city = data.get('city', '').strip()
    days = data.get('days', 3)
    budget = data.get('budget', 'Moderate (₹₹)')
    travel_type = data.get('travel_type', 'Friends / Solo')
    language = data.get('language', 'Hindi & English (Hinglish)')

    if not city:
        return jsonify({"error": "City name is required"}), 400

    prompt = f"""
    Create a detailed, exciting, and realistic {days}-day travel itinerary for {city}.
    - Target Audience/Style: {travel_type}
    - Budget Category: {budget}
    - Language: {language}

    Structure the response clearly with:
    1. 🌟 Trip Overview & Highlights
    2. 📅 Day-by-Day Breakdown (Day 1, Day 2, etc.) with Morning, Afternoon, Evening schedule & approximate entry tickets/costs in INR (₹).
    3. 🍲 Best Local Street Food & Must-Try Dishes (with top area/market suggestions).
    4. 💡 Insider Hacks (Best local transport/Metro vs Auto, best sunset point, photo spot).
    5. 💰 Estimated Total Budget Breakdown (Stay, Food, Sightseeing, Transport).

    Keep the tone friendly, practical, and highly engaging.
    """
    system_instruction = "You are an elite travel architect and local cultural connoisseur with deep knowledge of Indian and global travel logistics, budgets, safety, and cuisine."
    
    plan_text = call_gemini(prompt, system_instruction)
    return jsonify({
        "city": city,
        "days": days,
        "itinerary": plan_text
    })

@app.route('/api/ai/ask', methods=['POST'])
def ai_ask():
    data = request.get_json() or {}
    city = data.get('city', '').strip()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    prompt = f"Regarding traveling to or exploring {city}: {question}. Provide an accurate, helpful, friendly answer with practical tips."
    reply = call_gemini(prompt, "You are Travele's instant AI travel assistant. Answer helpfully, accurately, and concisely.")
    return jsonify({"reply": reply})

@app.route('/api/hotels/affiliates', methods=['GET'])
def get_hotel_affiliates():
    city = request.args.get('city', '').strip()
    if not city:
        return jsonify({"deals": []})

    deals = [
        {
            "partner": "Booking.com",
            "title": f"Top Rated Hotels & Stays in {city}",
            "discount": "Up to 30% Off Deals",
            "url": f"https://www.booking.com/searchresults.html?ss={requests.utils.quote(city)}",
            "badge": "Best Price Guarantee",
            "color": "#003580"
        },
        {
            "partner": "MakeMyTrip",
            "title": f"Budget & Luxury Hotels in {city}",
            "discount": "Instant Bank Offers",
            "url": f"https://www.makemytrip.com/hotels/{requests.utils.quote(city.lower())}-hotels.html",
            "badge": "Popular in India",
            "color": "#e41d25"
        },
        {
            "partner": "Agoda",
            "title": f"Secret Flash Deals on Resorts in {city}",
            "discount": "Special Mobile Rates",
            "url": f"https://www.agoda.com/search?city={requests.utils.quote(city)}",
            "badge": "Verified Guest Reviews",
            "color": "#5392f9"
        }
    ]
    return jsonify({"city": city, "deals": deals})

# ─── AUTHENTICATION API ROUTES ───────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row and check_password_hash(row[2], password):
        session['user_id'] = row[0]
        session['username'] = row[1]
        session['role'] = row[3]
        return jsonify({
            "success": True,
            "username": row[1],
            "role": row[3],
            "redirect": "/admin" if row[3] == "admin" else "/"
        })
    return jsonify({"error": "गलत यूज़रनेम या पासवर्ड!"}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if len(username) < 3 or len(password) < 4:
        return jsonify({"error": "यूज़रनेम कम से कम 3 और पासवर्ड 4 अक्षरों का होना चाहिए"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'user')", 
                  (username, generate_password_hash(password)))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['username'] = username
        session['role'] = 'user'
        conn.close()
        return jsonify({"success": True, "username": username, "role": "user"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "यह यूज़रनेम पहले से मौजूद है"}), 409

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/auth/me', methods=['GET'])
def current_user():
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "username": session.get('username'),
            "role": session.get('role')
        })
    return jsonify({"authenticated": False})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM favorites")
    total_favorites = c.fetchone()[0]

    c.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC")
    users = [{"id": r[0], "username": r[1], "role": r[2], "created_at": r[3]} for r in c.fetchall()]
    conn.close()

    return jsonify({
        "total_users": total_users,
        "total_favorites": total_favorites,
        "users": users
    })

# ─── CORE TRAVEL APIS ──────────────────────────────────────────

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', '')
    if not city:
        return jsonify({"error": "City name is required"}), 400

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_resp = requests.get(geo_url)
    geo_data = geo_resp.json()
    
    lat = None
    lon = None
    resolved_city = city
    country_code = ""
    country_name = ""
    
    if geo_data.get("results"):
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_city = location["name"]
        country_code = location.get("country_code", "")
        country_name = location.get("country", "")
    else:
        wiki_geo_url = "https://en.wikipedia.org/w/api.php"
        wiki_params = {
            "action": "query",
            "prop": "coordinates",
            "titles": city,
            "format": "json"
        }
        wiki_headers = {"User-Agent": "TravelCompanionApp/2.0 (student.project@localhost.com)"}
        try:
            wiki_resp = requests.get(wiki_geo_url, params=wiki_params, headers=wiki_headers)
            wiki_data = wiki_resp.json()
            pages = wiki_data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if "coordinates" in page_info:
                    lat = page_info["coordinates"][0]["lat"]
                    lon = page_info["coordinates"][0]["lon"]
                    resolved_city = page_info.get("title", city)
                    break
        except Exception:
            pass
            
    if lat is None or lon is None:
        return jsonify({"error": "Location not found"}), 404

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m&timezone=auto"
    weather_resp = requests.get(weather_url)
    weather_data = weather_resp.json()

    return jsonify({
        "city": resolved_city,
        "country": country_name,
        "country_code": country_code,
        "latitude": lat,
        "longitude": lon,
        "timezone": weather_data.get("timezone", "UTC"),
        "weather": weather_data.get("current", {})
    })

@app.route('/api/suggest')
def get_suggestions():
    q = request.args.get('q', '')
    if len(q) < 1:
        return jsonify({"suggestions": []})

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=5&language=en&format=json"
    try:
        resp = requests.get(geo_url)
        data = resp.json()
        suggestions = []
        if data.get("results"):
            for loc in data["results"]:
                name = loc.get("name", "")
                admin1 = loc.get("admin1", "")
                country = loc.get("country", "")
                parts = [name]
                if admin1 and admin1 != name:
                    parts.append(admin1)
                if country:
                    parts.append(country)
                full_label = ", ".join(parts)
                if full_label not in [s['label'] for s in suggestions]:
                    suggestions.append({
                        "name": name,
                        "label": full_label
                    })
        return jsonify({"suggestions": suggestions})
    except Exception:
        return jsonify({"suggestions": []})

@app.route('/api/places')
def get_places():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City name is required."}), 400

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{city} tourism OR {city} landmarks",
        "gsrlimit": 20,
        "prop": "pageimages|extracts",
        "pithumbsize": 800,
        "exchars": 150,
        "exintro": 1,
        "explaintext": 1
    }
    
    headers = {
        "User-Agent": "TravelCompanionApp/2.0 (student.project@localhost.com)"
    }
    
    try:
        resp = requests.get(WIKI_URL, params=params, headers=headers)
        if resp.status_code != 200:
            return jsonify({"places": [], "error": f"Wikipedia returned {resp.status_code}"}), 200

        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        
        places = []
        summer = []
        winter = []
        monsoon = []

        summer_kw = ['museum', 'mall', 'indoor', 'palace', 'gallery', 'park', 'water', 'lake']
        monsoon_kw = ['waterfall', 'lake', 'garden', 'hill', 'nature', 'green', 'river']
        winter_kw = ['fort', 'desert', 'temple', 'monument', 'safari', 'outdoor', 'ruins']

        for page_id, page_info in pages.items():
            if page_id == "-1": continue
            title = page_info.get("title", "")
            desc = page_info.get("extract", "")
            img = page_info.get("thumbnail", {}).get("source", "")
            
            if title.lower() == city.lower():
                continue

            place_obj = {
                "title": title,
                "description": desc,
                "image": img
            }
            places.append(place_obj)

            text_to_check = (title + " " + desc).lower()
            if any(kw in text_to_check for kw in monsoon_kw):
                monsoon.append(place_obj)
            elif any(kw in text_to_check for kw in summer_kw):
                summer.append(place_obj)
            else:
                winter.append(place_obj)

        if not summer and places: summer = places[:7]
        if not monsoon and places: monsoon = places[7:14]
        if not winter and places: winter = places[14:]

        return jsonify({
            "places": places,
            "seasonal": {
                "summer": summer,
                "winter": winter,
                "monsoon": monsoon
            }
        })
    except Exception as e:
        return jsonify({"places": [], "error": str(e)}), 200

@app.route('/api/city_info')
def get_city_info():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City name is required."}), 400

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageimages",
        "titles": city,
        "exchars": 1200,
        "exintro": 1,
        "explaintext": 1,
        "pithumbsize": 800
    }
    
    headers = {
        "User-Agent": "TravelCompanionApp/2.0 (student.project@localhost.com)"
    }
    
    try:
        resp = requests.get(WIKI_URL, params=params, headers=headers)
        if resp.status_code != 200:
            return jsonify({"title": city, "description": f"Currently unavailable (Rate limit: {resp.status_code})", "image": ""}), 200
            
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if str(page_id) != "-1":
                return jsonify({
                    "title": page_info.get("title", city),
                    "description": page_info.get("extract", "No detailed information found."),
                    "image": page_info.get("thumbnail", {}).get("source", "")
                })
        return jsonify({"title": city, "description": "No detailed information found for this city.", "image": ""})
    except ValueError:
        return jsonify({"error": "Failed to fetch data."}), 502

@app.route('/api/country', methods=['GET'])
def get_country():
    code = request.args.get('code', '')
    if not code:
        return jsonify({"error": "Country code is required"}), 400

    resp = requests.get(f"https://restcountries.com/v3.1/alpha/{code}")
    if resp.status_code != 200:
        return jsonify({"error": "Country not found"}), 404
        
    try:
        json_data = resp.json()
        if isinstance(json_data, dict) and json_data.get('success') is False:
            return jsonify({"error": "Country data unavailable"}), 404
            
        data = json_data[0] if isinstance(json_data, list) else json_data
        currencies = data.get("currencies", {})
        currency_names = [f"{c.get('name')} ({c.get('symbol', '')})" for c in currencies.values()]
        
        languages = data.get("languages", {})
        language_names = list(languages.values())
        timezones = data.get("timezones", [])
        
        return jsonify({
            "currencies": currency_names,
            "languages": language_names,
            "timezones": timezones,
            "flag": data.get("flags", {}).get("png", "")
        })
    except Exception:
        return jsonify({"error": "Failed to parse country data"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
