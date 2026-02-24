from fastapi import FastAPI, Query
from datetime import datetime, timezone, timedelta

app = FastAPI()

# website /health
@app.get("/health")
def health():
    return {"status" : "ok"}

# website /weather
@app.get("/weather")
def weather(query: str = Query(..., min_length=2, description="City or postcode")):
    now = datetime.now(timezone.utc)
    
    # simple mock hour + daily data
    hourly = []
    for i in range(0, 12):
        t = now + timedelta(hours=i)
        hourly.append(
            {
                "time": t.isoformat(),
                "temp_c": round(6.5 + i * 0.2, 1),
                "precip_prob": min(90, 10 + i * 4)
            }
        )
        
    daily = []
    for d in range(0, 7):
        day = (now + timedelta(days=d)).date().isoformat()
        daily.append(
            {
                "date": day,
                "min_c": round(4.0 + d * 0.2, 1),
                "max_c": round(9.0 + d * 0.3, 1),
                "precip_prob": min(95, 30 + d * 5)
            }
        )
    
    return {
        "location": {
            "name": query.title(),
            "lat": 51.5072,
            "lon": -0.1276,
            "timezone": "Europe/London",
        },
        "current": {
            "temp_c": 8.1,
            "feels_like_c": 6.2,
            "condition": "Cloudy",
            "wind_kph": 18,
            "precip_mm": 0.2,
        },
        "hourly": hourly,
        "daily": daily,
        "meta": {
            "source": "mock",
            "cached": False,
            "fetched_at": now.isoformat(),
        },
    }