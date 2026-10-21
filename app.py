import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Open-Meteo Geocoding API
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
# Open-Meteo Weather API
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
# Wikipedia API
WIKI_URL = "https://en.wikipedia.org/w/api.php"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', '')
    if not city:
        return jsonify({"error": "City name is required"}), 400

    # 1. Get Coordinates
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_resp = requests.get(geo_url)
    geo_data = geo_resp.json()
    
    # Coordinates fallback logic
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
        # Fallback to Wikipedia API if Open-Meteo fails (e.g., for States like Rajasthan or Countries)
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

    # Fetch Weather
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

        # Keywords for categorization
        summer_kw = ['museum', 'mall', 'indoor', 'palace', 'gallery', 'park', 'water', 'lake']
        monsoon_kw = ['waterfall', 'lake', 'garden', 'hill', 'nature', 'green', 'river']
        winter_kw = ['fort', 'desert', 'temple', 'monument', 'safari', 'outdoor', 'ruins']

        for page_id, page_info in pages.items():
            if page_id == "-1": continue
            
            title = page_info.get("title", "")
            desc = page_info.get("extract", "")
            img = page_info.get("thumbnail", {}).get("source", "")
            
            # Avoid the main city page itself
            if title.lower() == city.lower():
                continue

            place_obj = {
                "title": title,
                "description": desc,
                "image": img
            }
            places.append(place_obj)

            # Categorize
            text_to_check = (title + " " + desc).lower()
            
            if any(kw in text_to_check for kw in monsoon_kw):
                monsoon.append(place_obj)
            elif any(kw in text_to_check for kw in summer_kw):
                summer.append(place_obj)
            else:
                winter.append(place_obj) # Default for historical/outdoor places

        # If categories are empty, distribute evenly as fallback
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
