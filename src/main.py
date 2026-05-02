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
            w_code = int(current["weathercode"])
            current_info = WEATHER_MAP.get(w_code, {"condition": "Cloudy", "icon": "fa-cloud"})
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

            days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            for i in range(1, 6):
                date_str = daily["time"][i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days[date_obj.weekday()]
                f_code = int(daily["weathercode"][i])
                f_prob = daily["precipitation_probability_max"][i]
                f_info = WEATHER_MAP.get(f_code, {"icon": "fa-cloud"})
                icon = f_info["icon"]
                if f_code >= 51 and f_prob < 25:
                    icon = "fa-cloud-sun"
                weather_data["forecast"].append({
                    "day": day_name,
                    "temp": f"{round(daily['temperature_2m_max'][i])}°",
                    "icon": icon,
                    "prob": f"{f_prob}%"
                })

            weather_cache["data"] = weather_data
            weather_cache["expiry"] = datetime.now() + timedelta(minutes=15)
            return weather_data
    except Exception:
        return {
            "current": {"temp": "--", "condition": "Offline", "icon": "fa-exclamation-triangle", "high": "--", "low": "--", "rain_prob": "0%"},
            "forecast": []
        }

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
async def read_wallboard(request: Request, pup: str = "ParentName & PupName", img: str = "example_pup.jpg"):
    live_weather = await get_live_weather()
    
    # Scan for available dogs
    dogs_dir = os.path.join(BASE_DIR, "static", "assets", "dogs")
    available_dogs = []
    if os.path.exists(dogs_dir):
        for filename in os.listdir(dogs_dir):
            file_path = os.path.join(dogs_dir, filename)
            if os.path.isdir(file_path) or filename == "example_pup.jpg":
                continue
                
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                name_part = filename.rsplit('.', 1)[0]
                parts = name_part.split('_')
                
                if len(parts) >= 3:
                    # New format: [Parent1]_[Parent2]_..._[Pup]_[Date]
                    date_str = parts[-1]
                    pup_name = parts[-2].capitalize()
                    parent_list = [p.capitalize() for p in parts[:-2]]
                    
                    if len(parent_list) == 1:
                        display_name = f"{parent_list[0]} & {pup_name}"
                    else:
                        display_name = f"{', '.join(parent_list[:-1])}, {parent_list[-1]} & {pup_name}"
                        
                    if len(date_str) == 6:
                        display_date = f"{date_str[:2]}.{date_str[2:4]}.{date_str[4:]}"
                    else:
                        display_date = date_str
                elif len(parts) == 2:
                    # Fallback: [Pup]_[Date]
                    pup_name, date_str = parts
                    display_name = pup_name.capitalize()
                    if len(date_str) == 6:
                        display_date = f"{date_str[:2]}.{date_str[2:4]}.{date_str[4:]}"
                    else:
                        display_date = date_str
                else:
                    display_name = name_part.capitalize()
                    display_date = "Unknown"
                
                available_dogs.append({
                    "display_name": display_name,
                    "date": display_date,
                    "filename": filename,
                    "sort_key": display_name.lower()
                })
    
    pup_image = f"/static/assets/dogs/{img}"

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
            "available_dogs": sorted(available_dogs, key=lambda x: x['sort_key']),
            "current_time": datetime.now().strftime("%I:%M %p")
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
