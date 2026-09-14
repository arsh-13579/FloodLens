import { AlertTriangle, CloudRain, Waves, Mountain, RotateCw, Clock, Bot, Home, Navigation, MapPin, CloudSun } from 'lucide-react'
import Spinner from './Spinner.jsx'

const TIER_COLORS = { Low: '#22c55e', Moderate: '#eab308', High: '#f97316', Severe: '#ef4444' }

const FACTOR_META = {
  rainfall_mm: { label: 'Heavy Rainfall', Icon: CloudRain },
  water_level_m: { label: 'Rising Water Level', Icon: Waves },
  low_elevation: { label: 'Low Elevation', Icon: Mountain },
  drainage_poor: { label: 'Poor Drainage', Icon: RotateCw },
  flood_history: { label: 'Flood History', Icon: Clock },
}

export function RiskAlertCard({ riskData }) {
  if (!riskData) return null
  const color = TIER_COLORS[riskData.tier] || '#64748b'
  return (
    <div className="fl-alert-card fl-fade-in" style={{ borderColor: color, background: `${color}0d` }}>
      <div className="fl-alert-left">
        <AlertTriangle size={26} style={{ color }} className="fl-alert-icon" />
        <div>
          <div className="fl-alert-title">Flood Alert</div>
          <div className="fl-alert-sub">{riskData.tier} risk in your area</div>
        </div>
      </div>
      <div className="fl-alert-score" style={{ borderColor: color }}>
        <div className="fl-alert-score-label">Risk Score</div>
        <div className="fl-alert-score-num" style={{ color }}>
          {riskData.score}<span className="fl-alert-score-max">/100</span>
        </div>
      </div>
    </div>
  )
}

export function RiskBreakdownCard({ breakdown }) {
  if (!breakdown) return null
  return (
    <div className="fl-card fl-fade-in fl-fade-in-delay-1">
      <h4>Why this risk?</h4>
      <div className="fl-breakdown-grid">
        {Object.entries(breakdown).map(([key, points]) => {
          const meta = FACTOR_META[key] || { label: key, Icon: AlertTriangle }
          const Icon = meta.Icon
          return (
            <div key={key} className="fl-breakdown-item">
              <Icon size={22} className="fl-breakdown-icon" />
              <div className="fl-breakdown-label">{meta.label}</div>
              <div className="fl-breakdown-points">+{points}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function AdvisoryCard({ advisoryText, loading }) {
  return (
    <div className="fl-card fl-advisory-card fl-fade-in fl-fade-in-delay-2">
      <Bot size={24} className="fl-advisory-icon" />
      <div style={{ flex: 1 }}>
        <h4>AI Advisory</h4>
        {loading ? <Spinner label="Generating advisory..." /> : <p className="fl-card-text">{advisoryText}</p>}
      </div>
    </div>
  )
}

export function ShelterRouteCard({ nearestShelter, route, onViewRoute }) {
  return (
    <div className="fl-card fl-fade-in fl-fade-in-delay-3">
      <h4>Safe Route & Shelter</h4>
      {nearestShelter && (
        <div className="fl-shelter-row">
          <Home size={20} className="fl-shelter-icon" />
          <div style={{ flex: 1 }}>
            <div className="fl-shelter-name">{nearestShelter.name}</div>
            <div className="fl-card-subtext">
              {nearestShelter.distance_km} km
              {route && ` • ${route.duration_min} min`}
            </div>
          </div>
          <span className="fl-safe-badge">Safe</span>
        </div>
      )}
      {route ? (
        <>
          <div className="fl-route-row">
            <Navigation size={20} />
            <div>
              <div className="fl-shelter-name">Real Driving Route</div>
              <div className="fl-card-subtext">{route.distance_km} km • {route.duration_min} min (via OSRM)</div>
            </div>
          </div>
          <div className="fl-route-legend">
            <span><span className="fl-legend-dot" style={{ background: '#ef4444' }} /> High risk</span>
            <span><span className="fl-legend-dot" style={{ background: '#f97316' }} /> Moderate</span>
            <span><span className="fl-legend-dot" style={{ background: '#22c55e' }} /> Low risk</span>
          </div>
          <button className="fl-btn fl-btn-block" onClick={onViewRoute}>View Route on Map</button>
        </>
      ) : (
        <p className="fl-card-subtext">Route currently unavailable — routing service may be busy.</p>
      )}
    </div>
  )
}

export function WeatherLocationBar({ selectedPoint, weather }) {
  return (
    <div className="fl-bottombar">
      <div className="fl-bottombar-item">
        <MapPin size={20} className="fl-bottombar-icon" />
        <div>
          <div className="fl-bottombar-label">Your Location</div>
          <div className="fl-bottombar-value">
            {selectedPoint ? `${selectedPoint.lat}° N, ${selectedPoint.lon}° E` : 'Not selected'}
          </div>
        </div>
      </div>
      {weather && (
        <div className="fl-bottombar-item">
          <CloudSun size={20} className="fl-bottombar-icon" />
          <div>
            <div className="fl-bottombar-value">{weather.condition}</div>
            <div className="fl-bottombar-label">{weather.temperature_c}°C</div>
          </div>
        </div>
      )}
    </div>
  )
}
