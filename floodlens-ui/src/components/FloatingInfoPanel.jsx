import { X, Navigation, AlertTriangle } from 'lucide-react'

const TIER_COLORS = { Low: '#22c55e', Moderate: '#eab308', High: '#f97316', Severe: '#ef4444' }

const FACTOR_META = {
  rainfall_mm: 'Heavy Rainfall',
  water_level_m: 'Rising Water Level',
  low_elevation: 'Low Elevation',
  drainage_poor: 'Poor Drainage',
  flood_history: 'Flood History',
}

// Real distance calc (haversine) to find the nearest known village name,
// so the panel can show something more meaningful than raw coordinates
// without faking a geocoded address we don't actually have.
function nearestVillageName(villages, lat, lon) {
  if (!villages || villages.length === 0) return null
  let closest = null
  let minDist = Infinity
  for (const v of villages) {
    const d = Math.hypot(v.lat - lat, v.lon - lon)
    if (d < minDist) { minDist = d; closest = v }
  }
  // ~0.05 degrees is roughly 5-6km — only label it if genuinely close to a known point
  return minDist < 0.05 ? closest.name : null
}

export default function FloatingInfoPanel({
  selectedPoint, villages, riskData, advisoryText, advisoryLoading,
  nearestShelter, route, onClose, onViewRoute,
}) {
  if (!selectedPoint) return null

  const villageName = nearestVillageName(villages, selectedPoint.lat, selectedPoint.lon)
  const tierColor = riskData ? TIER_COLORS[riskData.tier] : '#64748b'

  return (
    <div className="fl-floating-panel">
      <div className="fl-floating-panel-header">
        <div>
          <div className="fl-floating-title">{villageName || 'Selected Location'}</div>
          <div className="fl-floating-subtitle">
            {selectedPoint.lat}° N, {selectedPoint.lon}° E
          </div>
        </div>
        <button className="fl-floating-close" onClick={onClose}><X size={18} /></button>
      </div>

      {riskData && (
        <>
          <div className="fl-floating-badge-row">
            <span className="fl-floating-badge" style={{ background: `${tierColor}20`, color: tierColor }}>
              <AlertTriangle size={14} /> {riskData.tier} Risk — {riskData.score}/100
            </span>
          </div>

          {route && (
            <button className="fl-floating-directions-btn" onClick={onViewRoute}>
              <Navigation size={16} /> Route to {nearestShelter?.name || 'Nearest Shelter'}
            </button>
          )}

          {riskData.breakdown && (
            <div className="fl-floating-chips">
              {Object.entries(riskData.breakdown)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3)
                .map(([key, points]) => (
                  <span key={key} className="fl-floating-chip">
                    {FACTOR_META[key] || key} +{points}
                  </span>
                ))}
            </div>
          )}

          <div className="fl-floating-about">
            <h5>About this risk</h5>
            <p>{advisoryLoading ? 'Generating advisory...' : advisoryText}</p>
          </div>

          {nearestShelter && (
            <div className="fl-floating-shelter">
              <span>🏢 {nearestShelter.name}</span>
              <span className="fl-floating-shelter-dist">{nearestShelter.distance_km} km</span>
            </div>
          )}
        </>
      )}
    </div>
  )
}
