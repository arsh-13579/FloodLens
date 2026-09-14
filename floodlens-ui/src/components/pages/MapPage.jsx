import MapView from '../MapView.jsx'

const LEGEND = [
  { tier: 'Severe', color: '#ef4444' },
  { tier: 'High', color: '#f97316' },
  { tier: 'Moderate', color: '#eab308' },
  { tier: 'Low', color: '#22c55e' },
]

export default function MapPage({ villages, selectedPoint, onSelect, gridPoints, shelters, route }) {
  return (
    <div>
      <div className="fl-legend-row">
        <h4 style={{ margin: 0 }}>Flood Risk (district-wide, live)</h4>
        <div className="fl-legend-items">
          {LEGEND.map((l) => (
            <span key={l.tier} className="fl-legend-item">
              <span className="fl-legend-dot" style={{ background: l.color }} /> {l.tier}
            </span>
          ))}
        </div>
      </div>
      <MapView
        villages={villages}
        selectedPoint={selectedPoint}
        onSelect={onSelect}
        gridPoints={gridPoints}
        shelters={shelters}
        routeToShelter={route}
        height="70vh"
      />
      <p className="fl-card-subtext" style={{ marginTop: 10 }}>
        Background shading is computed live across the whole district (district_grid.py). Click anywhere for a detailed, real-time reading.
      </p>
    </div>
  )
}
