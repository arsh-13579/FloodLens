import { useState, useEffect } from 'react'
import { getRisk } from '../../api.js'

const TIER_COLORS = { Low: '#22c55e', Moderate: '#eab308', High: '#f97316', Severe: '#ef4444' }

export default function WhatIfPage({ selectedPoint, riskData }) {
  const [rainfall, setRainfall] = useState(50)
  const [whatifResult, setWhatifResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedPoint) return
    setLoading(true)
    getRisk(selectedPoint.lat, selectedPoint.lon, rainfall)
      .then((r) => setWhatifResult(r))
      .catch((e) => console.error('What-if fetch failed:', e))
      .finally(() => setLoading(false))
  }, [selectedPoint, rainfall])

  if (!selectedPoint) {
    return (
      <div className="fl-card">
        <h4>Rainfall What-If</h4>
        <p className="fl-card-subtext">Select a location on the Home or Map page first.</p>
      </div>
    )
  }

  return (
    <div className="fl-card" style={{ maxWidth: 640 }}>
      <h4>Rainfall What-If Simulation</h4>
      <p className="fl-card-subtext">Location: {selectedPoint.lat}, {selectedPoint.lon}</p>

      <div className="fl-whatif-compare">
        <div>
          <div className="fl-card-subtext">Current</div>
          <div className="fl-whatif-score" style={{ color: TIER_COLORS[riskData?.tier] }}>
            {riskData?.score ?? '—'}
          </div>
          <div>{riskData?.tier ?? ''}</div>
        </div>
        <div className="fl-whatif-arrow">→</div>
        <div>
          <div className="fl-card-subtext">If rainfall = {rainfall}mm</div>
          <div className="fl-whatif-score" style={{ color: TIER_COLORS[whatifResult?.tier] }}>
            {loading ? '...' : (whatifResult?.score ?? '—')}
          </div>
          <div>{loading ? '' : (whatifResult?.tier ?? '')}</div>
        </div>
      </div>

      <input
        type="range" min="0" max="300" value={rainfall}
        onChange={(e) => setRainfall(Number(e.target.value))}
        style={{ width: '100%', marginTop: 20 }}
      />
      <div className="fl-card-subtext">{rainfall}mm rainfall (drag to simulate)</div>
    </div>
  )
}
