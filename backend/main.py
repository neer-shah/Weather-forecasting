from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone, timedelta
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# website /health
@app.get("/health")
def health():
    return {"status" : "ok"}

# get long and lat. asynchronous function not to block users
async def geocode_location(query: str) -> dict:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": query,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=10, limits=limits, http2=False) as client:
        r = await client.get(geo_url, params=params)
        r.raise_for_status()
        data = r.json()
    
    results = data.get("results") or []
    if not results:
        raise HTTPException(status_code=404, detail=f"Location not found: {query}")
    
    top = results[0]
    return {
        "name": f"{top.get('name')}, {top.get('country_code')}",
        "lat": top["latitude"],
        "lon": top["longitude"],
        "timezone": top.get("timezone", "auto")
    }
    
# get weather forecast data based on the location (long and lat)
async def fetch_forecast(lat: float, lon: float, tz: str) -> dict:
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto" if tz == "auto" else tz,
        "current_weather": "true",
        "hourly": "temperature_2m,precipitation_probability",
        "daily": "temperature_2m_min,temperature_2m_max,precipitation_probability_max",
    }
    
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=10, limits=limits, http2=False) as client:
        r = await client.get(forecast_url, params=params)
        r.raise_for_status()
        return r.json()

# website /weather
@app.get("/weather")
async def weather(query: str = Query(..., min_length=2, description="City or postcode")):
    now = datetime.now(timezone.utc)
    
    loc = await geocode_location(query)
    raw = await fetch_forecast(loc["lat"], loc["lon"], loc["timezone"])

    current_weather = raw.get("current_weather") or {}
    current_temp = current_weather.get("temperature")
    current_wind = current_weather.get("windspeed")
    
    feels_like = current_temp
    
    condition = f"Weather code {current_weather.get('weathercode', 'N/A')}"
    
    hourly = raw.get("hourly") or {}
    h_times = hourly.get("time") or []
    h_temps = hourly.get("temperature_2m") or []
    h_precip = hourly.get("precipitation_probability") or []
    
    hourly_out = []
    for i in range(min(12, len(h_times), len(h_temps), len(h_precip))):
        hourly_out.append(
            {
                "time": h_times[i],
                "temp_c": h_temps[i],
                "precip_prob": h_precip[i],
            }
        )

    daily = raw.get("daily") or {}
    d_dates = daily.get("time") or []
    d_min = daily.get("temperature_2m_min") or []
    d_max = daily.get("temperature_2m_max") or []
    d_precip = daily.get("precipitation_probability_max") or []

    daily_out = []
    for i in range(min(7, len(d_dates), len(d_min), len(d_max), len(d_precip))):
        daily_out.append(
            {
                "date": d_dates[i],
                "min_c": d_min[i],
                "max_c": d_max[i],
                "precip_prob": d_precip[i],
            }
        )

    return {
        "location": {
        "name": loc["name"],
        "lat": loc["lat"],
        "lon": loc["lon"],
        "timezone": raw.get("timezone", loc["timezone"]),
        },
        "current": {
            "temp_c": current_temp,
            "feels_like_c": feels_like,
            "condition": condition,
            "wind_kph": current_wind,
            "precip_mm": None,  # not included in this simple call; can add later
        },
        "hourly": hourly_out,
        "daily": daily_out,
        "meta": {
            "source": "open-meteo",
            "cached": False,
            "fetched_at": now.isoformat(),
        },
    }