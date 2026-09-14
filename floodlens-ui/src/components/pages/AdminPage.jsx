import { useState, useEffect } from 'react'
import { getAdminStatus } from '../../api.js'

const TIER_COLORS = { Low: '#22c55e', Moderate: '#eab308', High: '#f97316', Severe: '#ef4444' }

export default function AdminPage() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    function load() {
      getAdminStatus().then(setStatus).catch((e) => console.error(e))
    }
    load()
    const interval = setInterval(load, 15000) // refresh every 15s
    return () => clearInterval(interval)
  }, [])

  if (!status) return <p className="fl-card-subtext">Loading...</p>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 640 }}>
      <div className="fl-card">
        <h4>System Status <span className="fl-card-subtext" style={{ fontWeight: 400 }}>(auto-refreshing)</span></h4>
        <p className="fl-card-text">Registered subscribers: <b>{status.subscriber_count}</b></p>
        <p className="fl-card-text">
          Last water-level scrape:{' '}
          <b>{status.last_water_level_scrape ? new Date(status.last_water_level_scrape).toLocaleString() : 'Never'}</b>
        </p>
      </div>
      <div className="fl-card">
        <h4>Recent Alerts</h4>
        {status.recent_alerts.length === 0 ? (
          <p className="fl-card-subtext">No alerts sent yet.</p>
        ) : (
          status.recent_alerts.map((a, i) => (
            <div key={i} className="fl-activity-row">
              <span>{a.label} ({a.phone})</span>
              <span style={{ color: TIER_COLORS[a.tier], fontWeight: 700 }}>{a.tier}</span>
              <span className="fl-card-subtext">{new Date(a.alert_at).toLocaleString()}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}