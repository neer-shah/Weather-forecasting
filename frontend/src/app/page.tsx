"use client";

import { useState } from "react";

type WeatherResponse = {
  location: { name: string; lat: number; lon: number; timezone: string };
  current: {
    temp_c: number;
    feels_like_c: number;
    condition: string;
    wind_kph: number;
    precip_mm: number;
  };
  hourly: { time: string; temp_c: number; precip_prob: number }[];
  daily: { date: string; min_c: number; max_c: number; precip_prob: number }[];
  meta: { source: string; cached: boolean; fetched_at: string };
};

export default function Home() {
  const [query, setQuery] = useState("London");
  const [data, setData] = useState<WeatherResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchWeather() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/weather?query=${encodeURIComponent(query)}`
      );
      if (!res.ok) throw new Error(`Backend error: ${res.status}`);
      const json = (await res.json()) as WeatherResponse;
      setData(json);
    } catch (e: any) {
      setError(e?.message ?? "Something went wrong");
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 16 }}>
        Weather Forecaster
      </h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter city or postcode"
          style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
        />
        <button
          onClick={fetchWeather}
          disabled={loading}
          style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #111", background: "#111", color: "#fff" }}
        >
          {loading ? "Loading…" : "Search"}
        </button>
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {data && (
        <div style={{ display: "grid", gap: 16 }}>
          {/* Current */}
          <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <h2 style={{ margin: 0 }}>{data.location.name}</h2>
              <span style={{ fontSize: 12, color: "#666" }}>{data.location.timezone}</span>
            </div>
            <div style={{ fontSize: 22, marginTop: 8 }}>
              {data.current.temp_c}°C — {data.current.condition}
            </div>
            <div style={{ color: "#666", marginTop: 6 }}>
              Feels like {data.current.feels_like_c}°C · Wind {data.current.wind_kph} kph · Precip {data.current.precip_mm} mm
            </div>
          </section>

          {/* Hourly */}
          <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>Next 12 hours</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 10 }}>
              {data.hourly.map((h) => (
                <div key={h.time} style={{ border: "1px solid #f0f0f0", borderRadius: 10, padding: 10 }}>
                  <div style={{ fontSize: 12, color: "#666" }}>
                    {new Date(h.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </div>
                  <div style={{ fontSize: 18, fontWeight: 600 }}>{h.temp_c}°C</div>
                  <div style={{ fontSize: 12, color: "#666" }}>Rain {h.precip_prob}%</div>
                </div>
              ))}
            </div>
          </section>

          {/* Daily */}
          <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
            <h3 style={{ marginTop: 0 }}>7-day forecast</h3>
            <div style={{ display: "grid", gap: 8 }}>
              {data.daily.map((d) => (
                <div key={d.date} style={{ display: "flex", justifyContent: "space-between", border: "1px solid #f0f0f0", borderRadius: 10, padding: 10 }}>
                  <div>{new Date(d.date).toDateString()}</div>
                  <div style={{ fontWeight: 600 }}>{d.min_c}°C / {d.max_c}°C</div>
                  <div style={{ color: "#666" }}>Rain {d.precip_prob}%</div>
                </div>
              ))}
            </div>
          </section>

          <p style={{ fontSize: 12, color: "#777" }}>
            Source: {data.meta.source} · Cached: {String(data.meta.cached)} · Fetched:{" "}
            {new Date(data.meta.fetched_at).toLocaleString()}
          </p>
        </div>
      )}
    </main>
  );
}