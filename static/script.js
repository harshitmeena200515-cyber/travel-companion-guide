document.addEventListener('DOMContentLoaded', () => {
    // 3D Globe Initialization
    const globe = Globe()
        (document.getElementById('globeViz'))
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .backgroundColor('rgba(0,0,0,0)');

    // Auto-rotate
    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.5;

    // Adjust globe size on window resize
    window.addEventListener('resize', () => {
        globe.width(window.innerWidth);
        globe.height(window.innerHeight);
    });

    const searchBtn = document.getElementById('searchBtn');
    const cityInput = document.getElementById('cityInput');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    const mainContent = document.getElementById('mainContent');
    
    // Weather DOM elements
    const cityNameEl = document.getElementById('cityName');
    const temperatureEl = document.getElementById('temperature');
    const humidityEl = document.getElementById('humidity');
    const windSpeedEl = document.getElementById('windSpeed');
    const weatherIconEl = document.getElementById('weatherIcon');
    
    // Places DOM elements
    const placesCityNameEl = document.getElementById('placesCityName');
    const placesGrid = document.getElementById('placesGrid');

    // Overview DOM elements
    const overviewPanel = document.getElementById('overviewPanel');
    const overviewCityName = document.getElementById('overviewCityName');
    const cityDescription = document.getElementById('cityDescription');
    const cityImage = document.getElementById('cityImage');

    // Tourist DOM elements
    const cityMap = document.getElementById('cityMap');
    const countryCurrency = document.getElementById('countryCurrency');
    const countryLanguages = document.getElementById('countryLanguages');
    const countryTimezones = document.getElementById('countryTimezones');
    const packingList = document.getElementById('packingList');
    const micBtn = document.getElementById('micBtn');
    const autocompleteDropdown = document.getElementById('autocompleteDropdown');

    // Voice Search Logic (Web Speech API)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition && micBtn) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';

        micBtn.onclick = () => {
            micBtn.classList.add('mic-active');
            cityInput.placeholder = "Listening...";
            recognition.start();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            cityInput.value = transcript;
            searchCity();
        };

        recognition.onspeechend = () => {
            recognition.stop();
        };

        recognition.onend = () => {
            micBtn.classList.remove('mic-active');
            cityInput.placeholder = "Search for a city, state, or country...";
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            micBtn.classList.remove('mic-active');
            cityInput.placeholder = "Voice search failed. Try typing.";
        };
    } else if (micBtn) {
        micBtn.style.display = 'none'; // Hide if not supported
    }

    // Autocomplete Logic
    let debounceTimer;
    if (cityInput && autocompleteDropdown) {
        cityInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                autocompleteDropdown.classList.add('hidden');
                autocompleteDropdown.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    
                    autocompleteDropdown.innerHTML = '';
                    if (data.suggestions && data.suggestions.length > 0) {
                        data.suggestions.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'autocomplete-item';
                            
                            // Highlight the matching part
                            const regex = new RegExp(`^(${query})`, 'i');
                            const highlightedLabel = item.label.replace(regex, '<b>$1</b>');
                            
                            div.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> <span>${highlightedLabel}</span>`;
                            div.onclick = () => {
                                cityInput.value = item.name;
                                autocompleteDropdown.classList.add('hidden');
                                searchCity();
                            };
                            autocompleteDropdown.appendChild(div);
                        });
                        autocompleteDropdown.classList.remove('hidden');
                    } else {
                        autocompleteDropdown.classList.add('hidden');
                    }
                } catch (err) {
                    console.error("Autocomplete error:", err);
                }
            }, 300); // 300ms debounce
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target !== cityInput && e.target !== autocompleteDropdown) {
                autocompleteDropdown.classList.add('hidden');
            }
        });
    }

    // Handle Enter Key
    if (cityInput) {
        cityInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                autocompleteDropdown.classList.add('hidden');
                searchCity();
            }
        });
    }

    searchBtn.addEventListener('click', searchCity);

    async function searchCity() {
        const city = cityInput.value.trim();
        if (!city) return;

        // Reset UI
        mainContent.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loading.classList.remove('hidden');

        try {
            // Fetch Weather Data
            const weatherRes = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            const weatherData = await weatherRes.json();

            if (!weatherRes.ok) throw new Error(weatherData.error || 'Failed to fetch weather');

            // Use the officially resolved city name for other APIs to auto-correct spelling
            const correctedCity = weatherData.city;

            // Fetch Places Data
            const placesRes = await fetch(`/api/places?city=${encodeURIComponent(correctedCity)}`);
            const placesData = await placesRes.json();

            // Fetch City Info Data
            const cityInfoRes = await fetch(`/api/city_info?city=${encodeURIComponent(correctedCity)}`);
            const cityInfoData = await cityInfoRes.json();

            // Fetch Country Essentials if country_code exists
            let countryData = null;
            if (weatherData.country_code) {
                const countryRes = await fetch(`/api/country?code=${weatherData.country_code}`);
                if (countryRes.ok) {
                    countryData = await countryRes.json();
                }
            }

            updateUI(weatherData, placesData.places, placesData.seasonal, cityInfoData, countryData);
            
            loading.classList.add('hidden');
            mainContent.classList.remove('hidden');
        } catch (error) {
            loading.classList.add('hidden');
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('hidden');
        }
    }

    function updateUI(weatherInfo, places, seasonalData, cityInfo, countryInfo) {
        // Update Weather
        cityNameEl.textContent = `${weatherInfo.city}, ${weatherInfo.country}`;
        placesCityNameEl.textContent = weatherInfo.city;
        
        const current = weatherInfo.weather;
        temperatureEl.textContent = `${Math.round(current.temperature_2m)}°C`;
        humidityEl.textContent = `${current.relative_humidity_2m}%`;
        windSpeedEl.textContent = `${current.wind_speed_10m} km/h`;
        
        // Simple mapping of WMO Weather codes to FontAwesome icons
        updateWeatherIcon(current.weather_code);

        // Fly Globe to Location
        const lat = weatherInfo.latitude;
        const lon = weatherInfo.longitude;

        // Zoom in much closer (altitude from 1.5 to 0.6)
        globe.pointOfView({ lat: lat, lng: lon, altitude: 0.6 }, 2500);
        
        // Add Marker
        globe.labelsData([{
            lat: lat,
            lng: lon,
            text: weatherInfo.city,
            color: 'white',
            size: 2
        }])
        .labelText('text')
        .labelSize('size')
        .labelColor('color')
        .labelDotRadius(0.8)
        .labelAltitude(0.01);

        // Add Pulsating Ring (Radar effect) exactly at the location
        globe.ringsData([{ lat: lat, lng: lon }])
        .ringColor(() => '#3b82f6')
        .ringMaxRadius(2)
        .ringPropagationSpeed(1.5)
        .ringRepeatPeriod(800);

        // Map Transition Logic (Go Deep)
        function openDeepMap(targetLat, targetLon) {
            const tLat = parseFloat(targetLat);
            const tLon = parseFloat(targetLon);
            
            // Zoom in super deep
            globe.pointOfView({ lat: tLat, lng: tLon, altitude: 0.01 }, 1500);
            
            // After zoom animation finishes, show the map overlay
            setTimeout(() => {
                const mapContainer = document.getElementById('fullScreenMapContainer');
                const mapFrame = document.getElementById('fullScreenMap');
                // Tighter bounding box for a very close street view
                const bbox = `${tLon - 0.05},${tLat - 0.05},${tLon + 0.05},${tLat + 0.05}`;
                mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik`;
                mapContainer.classList.add('active');
            }, 1500);
        }

        // Open map when clicking the label
        if (typeof globe.onLabelClick === 'function') {
            globe.onLabelClick((label) => openDeepMap(label.lat, label.lng));
        }

        // Add a global click fallback just in case the label is too hard to click
        // Only trigger if we have a searched location and they double click the globe
        let clickTimeout = null;
        globe.onGlobeClick(({ lat: clickedLat, lng: clickedLng }) => {
            // Check if it's a double click (simple implementation)
            if (clickTimeout !== null) {
                clearTimeout(clickTimeout);
                clickTimeout = null;
                // Double click registered, open deep map at the searched location
                openDeepMap(lat, lon);
            } else {
                clickTimeout = setTimeout(() => {
                    clickTimeout = null;
                }, 600); // 600ms double click window (easier to trigger)
            }
        });

        // Close map button logic
        const closeBtn = document.getElementById('closeMapBtn');
        if (closeBtn) {
            closeBtn.onclick = () => {
                document.getElementById('fullScreenMapContainer').classList.remove('active');
                // Zoom back out to normal view
                globe.pointOfView({ altitude: 0.6 }, 1500);
            };
        }

        // Update Small Map
        const pLat = parseFloat(lat);
        const pLon = parseFloat(lon);
        // Adjust bounding box for the iframe
        const smallBbox = `${pLon-0.05},${pLat-0.05},${pLon+0.05},${pLat+0.05}`;
        cityMap.src = `https://www.openstreetmap.org/export/embed.html?bbox=${smallBbox}&layer=mapnik`;

        // Update Travel Essentials
        if (countryInfo && !countryInfo.error) {
            countryCurrency.textContent = countryInfo.currencies ? countryInfo.currencies.join(", ") : "Unknown";
            countryLanguages.textContent = countryInfo.languages ? countryInfo.languages.join(", ") : "Unknown";
        } else {
            countryCurrency.textContent = "Data unavailable";
            countryLanguages.textContent = "Data unavailable";
        }

        // Live Local Time (using timezone from Weather API)
        const timezone = weatherInfo.weather.timezone || weatherInfo.timezone || 'UTC';
        try {
            const localTimeString = new Date().toLocaleTimeString('en-US', { timeZone: timezone, hour: '2-digit', minute: '2-digit' });
            document.getElementById('localTime').textContent = localTimeString;
        } catch(e) {
            document.getElementById('localTime').textContent = "Unknown";
        }

        // Update Trip Planner Links
        const queryCity = encodeURIComponent(weatherInfo.city);
        document.getElementById('linkFlights').href = `https://www.google.com/flights?q=flights+to+${queryCity}`;
        document.getElementById('linkHotels').href = `https://www.google.com/maps/search/Hotels+in+${queryCity}`;
        document.getElementById('linkFood').href = `https://www.google.com/maps/search/Restaurants+in+${queryCity}`;
        document.getElementById('linkCabs').href = `https://www.google.com/maps/search/Transport+in+${queryCity}`;

        // Smart Packing Tips
        generatePackingTips(current.weather_code, current.temperature_2m);

        // Update Overview (History & About)
        if (cityInfo && cityInfo.description) {
            overviewCityName.textContent = `About ${cityInfo.title || weatherInfo.city}`;
            cityDescription.textContent = cityInfo.description;
            if (cityInfo.image) {
                cityImage.src = cityInfo.image;
                cityImage.classList.remove('hidden');
            } else {
                cityImage.classList.add('hidden');
            }
            overviewPanel.classList.remove('hidden');
        } else {
            overviewPanel.classList.add('hidden');
        }

        // Helper function to render a grid of places
        function renderGrid(container, placesArray) {
            container.innerHTML = '';
            if (placesArray && placesArray.length > 0) {
                placesArray.forEach((place, index) => {
                    const delay = index * 0.05;
                    const card = document.createElement('div');
                    card.className = 'place-card glass-panel';
                    card.setAttribute('data-tilt', '');
                    card.style.animation = `fadeInDown 0.5s ease ${delay}s both`;
                    
                    const imageUrl = place.image || 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80';
                    
                    card.innerHTML = `
                        <div style="overflow: hidden; border-radius: 10px 10px 0 0;">
                            <img src="${imageUrl}" alt="${place.title}" class="place-image" onerror="this.src='https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'">
                        </div>
                        <div class="place-content">
                            <h4 class="place-title">${place.title}</h4>
                            <p class="place-desc">${place.description || 'A beautiful famous location to visit.'}</p>
                        </div>
                    `;
                    container.appendChild(card);
                });
            } else {
                container.innerHTML = `<p style="text-align: center; grid-column: 1/-1; color: white;">No famous places found. Try another search!</p>`;
            }
        }

        // Render All Places
        renderGrid(placesGrid, places);

        // Seasonal Logic
        const seasonalGrid = document.getElementById('seasonalGrid');
        const tabBtns = document.querySelectorAll('.tab-btn');
        let currentSeasonData = null;

        if (seasonalData) {
            currentSeasonData = seasonalData;
            document.getElementById('seasonalGuideContainer').classList.remove('hidden');
            // Default render summer
            renderGrid(seasonalGrid, currentSeasonData.summer);
            
            // Tab Event Listeners
            tabBtns.forEach(btn => {
                btn.onclick = (e) => {
                    tabBtns.forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    const season = e.target.getAttribute('data-season');
                    renderGrid(seasonalGrid, currentSeasonData[season]);
                    // Re-init tilt for new cards
                    VanillaTilt.init(document.querySelectorAll(".glass-panel"), { max: 5, speed: 400, glare: true, "max-glare": 0.2 });
                };
            });
        } else {
            document.getElementById('seasonalGuideContainer').classList.add('hidden');
        }

        // Apply 3D Tilt to all newly created glass panels
        VanillaTilt.init(document.querySelectorAll(".glass-panel"), {
            max: 5,
            speed: 400,
            glare: true,
            "max-glare": 0.2
        });
    }

    function updateWeatherIcon(code) {
        // WMO Weather interpretation codes
        // 0: Clear sky
        // 1, 2, 3: Mainly clear, partly cloudy, and overcast
        // 45, 48: Fog and depositing rime fog
        // 51, 53, 55: Drizzle
        // 61, 63, 65: Rain
        // 71, 73, 75: Snow fall
        // 80, 81, 82: Rain showers
        // 95, 96, 99: Thunderstorm
        
        weatherIconEl.className = 'fa-solid'; // Reset classes
        
        if (code === 0 || code === 1) weatherIconEl.classList.add('fa-sun');
        else if (code === 2) weatherIconEl.classList.add('fa-cloud-sun');
        else if (code === 3 || code === 45 || code === 48) weatherIconEl.classList.add('fa-cloud');
        else if (code >= 51 && code <= 65) weatherIconEl.classList.add('fa-cloud-rain');
        else if (code >= 71 && code <= 75) weatherIconEl.classList.add('fa-snowflake');
        else if (code >= 80 && code <= 82) weatherIconEl.classList.add('fa-cloud-showers-heavy');
        else if (code >= 95 && code <= 99) weatherIconEl.classList.add('fa-cloud-bolt');
        else weatherIconEl.classList.add('fa-cloud-sun'); // Default fallback
    }

    function generatePackingTips(weatherCode, temp) {
        packingList.innerHTML = '';
        const tips = [];

        // Temperature based tips
        if (temp < 10) {
            tips.push('<i class="fa-solid fa-mitten"></i> Heavy jacket, gloves, and warm clothes.');
            tips.push('<i class="fa-solid fa-mug-hot"></i> Thermos for hot drinks.');
        } else if (temp >= 10 && temp < 20) {
            tips.push('<i class="fa-solid fa-shirt"></i> Light jacket or sweater.');
            tips.push('<i class="fa-solid fa-shoe-prints"></i> Comfortable walking shoes.');
        } else {
            tips.push('<i class="fa-solid fa-glasses"></i> Sunglasses and sunscreen.');
            tips.push('<i class="fa-solid fa-bottle-water"></i> Reusable water bottle to stay hydrated.');
            tips.push('<i class="fa-solid fa-hat-sun"></i> Light, breathable cotton clothing.');
        }

        // Weather condition based tips
        if (weatherCode >= 51 && weatherCode <= 65) {
            tips.push('<i class="fa-solid fa-umbrella"></i> Umbrella and waterproof shoes for the rain.');
        } else if (weatherCode >= 71 && weatherCode <= 75) {
            tips.push('<i class="fa-solid fa-person-snowboarding"></i> Snow boots and waterproof pants.');
        } else if (weatherCode >= 80 && weatherCode <= 99) {
            tips.push('<i class="fa-solid fa-cloud-bolt"></i> Strong raincoat. Avoid outdoor plans if thunderstorm hits.');
        }

        tips.push('<i class="fa-solid fa-camera"></i> Camera or smartphone for memories!');

        tips.forEach(tip => {
            const li = document.createElement('li');
            li.innerHTML = tip;
            packingList.appendChild(li);
        });
    }
});
