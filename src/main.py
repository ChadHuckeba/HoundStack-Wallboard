import os
import httpx
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="HoundStack Wallboard")

# Setup templates and static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configuration
PFLUGERVILLE_COORDS = {"lat": 30.4548, "lon": -97.6223}

# WMO Weather Codes to FontAwesome mapping
WEATHER_MAP = {
    0: {"condition": "Clear", "icon": "fa-sun"},
    1: {"condition": "Mainly Clear", "icon": "fa-sun"},
    2: {"condition": "Partly Cloudy", "icon": "fa-cloud-sun"},
    3: {"condition": "Overcast", "icon": "fa-cloud"},
    45: {"condition": "Foggy", "icon": "fa-smog"},
    48: {"condition": "Foggy", "icon": "fa-smog"},
    51: {"condition": "Light Drizzle", "icon": "fa-cloud-rain"},
    61: {"condition": "Rain", "icon": "fa-cloud-showers-heavy"},
    80: {"condition": "Showers", "icon": "fa-cloud-rain"},
    95: {"condition": "Stormy", "icon": "fa-bolt"},
}

# In-memory cache for weather
weather_cache = {"data": None, "expiry": datetime.now()}

async def get_live_weather():
    if weather_cache["data"] and datetime.now() < weather_cache["expiry"]:
        return weather_cache["data"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": PFLUGERVILLE_COORDS["lat"],
        "longitude": PFLUGERVILLE_COORDS["lon"],
        "current_weather": True,
        "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "temperature_unit": "fahrenheit",
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            current = data["current_weather"]
            daily = data["daily"]
            
            # 1. Process Current Weather
            w_code = int(current["weathercode"])
            current_info = WEATHER_MAP.get(w_code, {"condition": "Cloudy", "icon": "fa-cloud"})
            
            # Logic: If it's a "Stormy" code but prob is < 20%, override to Clear/Cloudy
            prob_today = daily['precipitation_probability_max'][0]
            if w_code >= 51 and prob_today < 20:
                 current_info = {"condition": "Partly Cloudy", "icon": "fa-cloud-sun"}

            weather_data = {
                "current": {
                    "temp": f"{round(current['temperature'])}°",
                    "condition": current_info["condition"],
                    "icon": current_info["icon"],
                    "high": f"{round(daily['temperature_2m_max'][0])}°",
                    "low": f"{round(daily['temperature_2m_min'][0])}°",
                    "rain_prob": f"{prob_today}%"
                },
                "forecast": []
            }

            # 2. Build 5-day forecast
            days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            for i in range(1, 6):
                date_str = daily["time"][i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days[date_obj.weekday()]
                
                f_code = int(daily["weathercode"][i])
                f_prob = daily["precipitation_probability_max"][i]
                f_info = WEATHER_MAP.get(f_code, {"icon": "fa-cloud"})
                
                # Accuracy Logic: Override icons if probability is low
                icon = f_info["icon"]
                if f_code >= 51 and f_prob < 25:
                    icon = "fa-cloud-sun" # Better safe than wet

                weather_data["forecast"].append({
                    "day": day_name,
                    "temp": f"{round(daily['temperature_2m_max'][i])}°",
                    "icon": icon,
                    "prob": f"{f_prob}%"
                })

            weather_cache["data"] = weather_data
            weather_cache["expiry"] = datetime.now() + timedelta(minutes=15)
            return weather_data
    except Exception as e:
        print(f"Weather API Error: {e}")
        return {
            "current": {"temp": "--", "condition": "Offline", "icon": "fa-exclamation-triangle", "high": "--", "low": "--", "rain_prob": "0%"},
            "forecast": []
        }

# Mock data
SCHEDULE = [
    {"time": "05:00 AM", "activity": "Wake Up & Potty", "icon": "🌅"},
    {"time": "06:00 AM", "activity": "Breakfast", "icon": "🥣"},
    {"time": "07:00 AM", "activity": "Morning Walk (~1.5 mi)", "icon": "🦮"},
    {"time": "Every ~2h", "activity": "Potty & Play", "icon": "🎾"},
    {"time": "06:00 PM", "activity": "Dinner", "icon": "🥩"},
    {"time": "07:00 PM", "activity": "Evening Walk (1.5 mi)", "icon": "🌙"},
    {"time": "09:00 PM", "activity": "Bedtime", "icon": "💤"},
]

VET_INFO = {
    "name": "Heart of Texas",
    "address": "3675 Gattis School Rd, Round Rock, TX",
    "phone": "512-744-4644",
    "distance": "~12 minutes"
}

@app.get("/")
async def read_wallboard(request: Request, pup: str = "Our Guest", img: str = None):
    live_weather = await get_live_weather()
    
    # Default image logic: If no image provided, use a placeholder
    # You can drop images into src/static/assets/dogs/
    pup_image = f"/static/assets/dogs/{img}" if img else None

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "host_name": "Chad Huckeba",
            "schedule": SCHEDULE,
            "vet": VET_INFO,
            "weather": live_weather,
            "pup_name": pup,
            "pup_image": pup_image,
            "current_time": datetime.now().strftime("%I:%M %p")
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
