import {
  ArrowDown,
  ArrowRight,
  CalendarBlank,
  CheckCircle,
  CloudSun,
  Pulse,
  Sparkle,
  Wind,
  X,
} from "@phosphor-icons/react";
import React, { useEffect, useMemo, useState } from "react";
import { cities, driftFeatures, modelResults } from "./data";

export function Navigation({ onForecast }) {
  const [open, setOpen] = useState(false);
  return (
    <header className="site-header">
      <nav className="nav-shell" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="Airwise home">
          <span className="brand-mark"><Wind weight="bold" /></span>
          <span>airwise</span>
        </a>
        <div className={`nav-links ${open ? "is-open" : ""}`}>
          <a href="#intelligence" onClick={() => setOpen(false)}>Intelligence</a>
          <a href="#cities" onClick={() => setOpen(false)}>Cities</a>
          <a href="#model" onClick={() => setOpen(false)}>Model</a>
        </div>
        <button className="nav-cta" onClick={onForecast}>Forecast air <ArrowRight /></button>
        <button className="menu-button" onClick={() => setOpen(!open)} aria-label="Toggle navigation" aria-expanded={open}>
          {open ? <X /> : <span />}
        </button>
      </nav>
    </header>
  );
}

export function Hero({ onForecast }) {
  return (
    <section className="hero" id="top">
      <div className="hero-ambient" aria-hidden="true" />
      <div className="hero-content">
        <p className="eyebrow"><span /> Next-day intelligence for five Indian cities</p>
        <h1>Tomorrow's air, <span className="inline-air-image" aria-hidden="true" /> made visible.</h1>
        <p className="hero-copy">A calmer way to understand what's coming. Airwise turns years of pollution signals into a clear, city-specific forecast you can act on.</p>
        <div className="hero-actions">
          <button className="button button-primary" onClick={onForecast}>Get tomorrow's forecast <ArrowRight /></button>
          <a className="button button-secondary" href="#intelligence">Explore the signals <ArrowDown /></a>
        </div>
      </div>
      <div className="hero-visual visual-reveal">
        <img src="https://picsum.photos/seed/india-air-dawn/1920/1080" alt="Atmospheric city skyline at dawn" />
        <div className="hero-visual-overlay" />
        <div className="air-reading">
          <span className="reading-orbit"><span /></span>
          <div><small>Delhi tomorrow</small><strong>214</strong><span>Poor air</span></div>
        </div>
        <p className="visual-caption">Model confidence <strong>91.96%</strong></p>
      </div>
    </section>
  );
}

function TinyLineChart() {
  return (
    <svg className="tiny-chart" viewBox="0 0 600 170" role="img" aria-label="AQI trend declining from 208 to 146">
      <defs>
        <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d6ff4b" stopOpacity=".35" />
          <stop offset="1" stopColor="#d6ff4b" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path className="chart-area" d="M0 40 C55 70, 85 18, 145 58 S245 122, 310 88 S410 52, 470 96 S545 122,600 105 L600 170 L0 170Z" />
      <path className="chart-line" d="M0 40 C55 70, 85 18, 145 58 S245 122, 310 88 S410 52, 470 96 S545 122,600 105" />
    </svg>
  );
}

export function Intelligence() {
  return (
    <section className="section light-section" id="intelligence">
      <div className="section-heading">
        <p className="eyebrow dark"><span /> Read the atmosphere</p>
        <h2>One signal is noise.<br />The pattern is intelligence.</h2>
        <p>We combine yesterday's readings, rolling particulate averages, location and seasonality to see what a single sensor cannot.</p>
      </div>
      <div className="bento-grid">
        <article className="bento-card bento-trend interactive-card">
          <div className="card-top"><span>Seven-day outlook</span><Pulse /></div>
          <div className="trend-summary"><strong>146</strong><span><b>–18%</b> by Sunday<br />Delhi, NCR</span></div>
          <TinyLineChart />
          <div className="chart-days"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span><span>SUN</span></div>
        </article>

        <article className="bento-card bento-model interactive-card">
          <div className="card-top"><span>Forecast engine</span><Sparkle /></div>
          <div className="model-ring"><span><strong>91.96</strong>%</span></div>
          <div><h3>Built to explain,<br />not overwhelm.</h3><p>Six models tested. One clear signal selected through tracked, reproducible experiments.</p></div>
        </article>

        <article className="bento-card bento-drift interactive-card">
          <div className="card-top"><span>Drift watch</span><CloudSun /></div>
          <div><strong>1</strong><span>signal needs<br />attention</span></div>
          <p>The 3-day AQI average has moved beyond its normal operating range.</p>
          <span className="status-chip"><i /> Retraining advised</span>
        </article>

        <article className="bento-card bento-data interactive-card">
          <div className="card-top"><span>Signal health</span><CheckCircle /></div>
          <div className="drift-list">
            {driftFeatures.map((item) => (
              <div className="drift-row" key={item.name}>
                <span>{item.name}</span>
                <div><i style={{ width: `${Math.min(item.value / 0.25, 1) * 100}%` }} /></div>
                <strong className={item.status === "Alert" ? "alert" : ""}>{item.value.toFixed(3)}</strong>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

export function CityAccordion() {
  const [active, setActive] = useState(0);
  return (
    <section className="section dark-section city-section" id="cities">
      <div className="section-heading city-heading">
        <p className="eyebrow"><span /> Five cities, five climates</p>
        <h2>Air is always local.</h2>
        <p>Open a city to see how geography, traffic, rainfall and seasonal conditions create a different atmospheric rhythm.</p>
      </div>
      <div className="city-accordion visual-reveal">
        {cities.map((city, index) => (
          <button
            key={city.name}
            className={`city-panel ${index === active ? "active" : ""}`}
            onMouseEnter={() => setActive(index)}
            onFocus={() => setActive(index)}
            onClick={() => setActive(index)}
            style={{ "--city-accent": city.accent }}
            aria-expanded={index === active}
          >
            <img src={city.image} alt={`${city.name} atmospheric view`} />
            <span className="city-shade" />
            <span className="city-name">{city.name}</span>
            <span className="city-detail">
              <span className="city-aqi"><strong>{city.aqi}</strong><small>AQI now<br />{city.category}</small></span>
              <span className="city-copy">{city.copy}</span>
              <span className="city-link">View city signal <ArrowRight /></span>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}

export function ModelStory() {
  return (
    <section className="section model-section" id="model">
      <div className="model-intro">
        <p className="eyebrow dark"><span /> Tested in the open</p>
        <h2>Clarity earns trust.</h2>
        <p>Every forecast is backed by visible evidence: six compared models, tracked experiments, reproducible data and continuous drift monitoring.</p>
      </div>
      <div className="stack-zone">
        <article className="stack-card stack-card-one">
          <span className="stack-index">01</span>
          <div><small>Performance</small><h3>91.96% of variance explained.</h3></div>
          <div className="model-bars">
            {modelResults.map((item) => <div key={item.model}><span>{item.model}</span><i><b style={{ width: `${item.r2 * 100}%` }} /></i><strong>{item.r2.toFixed(3)}</strong></div>)}
          </div>
        </article>
        <article className="stack-card stack-card-two">
          <span className="stack-index">02</span>
          <div><small>Precision</small><h3>About 15 AQI points of average error.</h3></div>
          <div className="precision-display"><span>±</span><strong>14.68</strong><small>mean absolute error</small></div>
        </article>
        <article className="stack-card stack-card-three">
          <span className="stack-index">03</span>
          <div><small>Discipline</small><h3>A pipeline that keeps watching itself.</h3></div>
          <div className="pipeline-flow"><span>Raw air</span><i /><span>Features</span><i /><span>Forecast</span><i /><span>Monitor</span></div>
        </article>
      </div>
    </section>
  );
}

function defaultDate() {
  const value = new Date();
  value.setDate(value.getDate() + 1);
  return value.toISOString().slice(0, 10);
}

export function ForecastModal({ open, onClose }) {
  const [form, setForm] = useState({ city: "Delhi", forecast_date: defaultDate(), aqi_yesterday: 150, aqi_3day_avg: 145, pm25_yesterday: 80, pm25_3day_avg: 75, pm10_yesterday: 150, pm10_3day_avg: 140 });
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("idle");

  useEffect(() => {
    if (!open) return;
    const close = (event) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", close);
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", close); document.body.style.overflow = ""; };
  }, [open, onClose]);

  const category = useMemo(() => {
    if (!result) return null;
    return result.aqi_category?.toLowerCase().replace(" ", "-");
  }, [result]);

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  async function submit(event) {
    event.preventDefault();
    setStatus("loading");
    setResult(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, ...Object.fromEntries(Object.entries(form).filter(([key]) => !["city", "forecast_date"].includes(key)).map(([key, value]) => [key, Number(value)])) }),
      });
      if (!response.ok) throw new Error("The forecast service is not available yet.");
      setResult(await response.json());
      setStatus("success");
    } catch (error) {
      setStatus("error");
    }
  }

  if (!open) return null;
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div className="forecast-modal" role="dialog" aria-modal="true" aria-labelledby="forecast-title">
        <button className="modal-close" onClick={onClose} aria-label="Close forecast"><X /></button>
        <div className="modal-heading"><p className="eyebrow dark"><span /> Personal forecast</p><h2 id="forecast-title">See tomorrow clearly.</h2><p>Use your most recent readings to generate a next-day city forecast.</p></div>
        {status !== "success" ? (
          <form onSubmit={submit}>
            <div className="form-primary">
              <label>City<select value={form.city} onChange={(e) => update("city", e.target.value)}>{cities.map((city) => <option key={city.name}>{city.name}</option>)}</select></label>
              <label>Forecast date<span className="input-icon"><CalendarBlank /></span><input type="date" value={form.forecast_date} onChange={(e) => update("forecast_date", e.target.value)} required /></label>
            </div>
            <p className="form-note">Recent air readings</p>
            <div className="reading-grid">
              {[
                ["aqi_yesterday", "AQI yesterday"], ["aqi_3day_avg", "AQI 3-day average"],
                ["pm25_yesterday", "PM2.5 yesterday"], ["pm25_3day_avg", "PM2.5 3-day average"],
                ["pm10_yesterday", "PM10 yesterday"], ["pm10_3day_avg", "PM10 3-day average"],
              ].map(([key, label]) => <label key={key}>{label}<input type="number" min="0" step="0.1" value={form[key]} onChange={(e) => update(key, e.target.value)} required /></label>)}
            </div>
            {status === "error" && <p className="form-error">The API is offline. Start the forecast service on port 8000 and try again.</p>}
            <button className="button button-primary modal-submit" disabled={status === "loading"}>{status === "loading" ? "Reading the signals…" : "Generate forecast"}<ArrowRight /></button>
          </form>
        ) : (
          <div className={`forecast-result ${category}`}>
            <p>{result.city} · {new Date(`${result.forecast_date}T00:00:00`).toLocaleDateString("en-IN", { day: "numeric", month: "long" })}</p>
            <strong>{result.predicted_aqi}</strong>
            <h3>{result.aqi_category} air</h3>
            <span>Forecast by {result.model_used} · {(result.r2_score * 100).toFixed(1)}% model score</span>
            <button className="button result-reset" onClick={() => setStatus("idle")}>Adjust readings</button>
          </div>
        )}
      </div>
    </div>
  );
}

export function Closing({ onForecast }) {
  return (
    <>
      <section className="closing-section">
        <div className="closing-orb" aria-hidden="true" />
        <p className="eyebrow"><span /> Your next breath starts here</p>
        <h2>Plan the day.<br />Not the uncertainty.</h2>
        <button className="button button-primary" onClick={onForecast}>Forecast my city <ArrowRight /></button>
      </section>
      <div className="marquee" aria-hidden="true"><div>{[...cities, ...cities].map((city, index) => <span key={`${city.name}-${index}`}>{city.name}<i /></span>)}</div></div>
      <footer><a className="brand footer-brand" href="#top"><span className="brand-mark"><Wind weight="bold" /></span><span>airwise</span></a><p>Next-day AQI forecasting for India.<br />Built with monitored machine learning.</p><div><a href="#intelligence">Intelligence</a><a href="#cities">Cities</a><a href="#model">Model</a></div><small>Data coverage 2018—2024</small></footer>
    </>
  );
}
