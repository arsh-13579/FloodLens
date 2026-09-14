export default function AdvisoryPage({ selectedPoint, riskData, advisoryText, advisoryLoading, profile }) {
  if (!selectedPoint || !riskData) {
    return (
      <div className="fl-card">
        <h4>AI Advisory</h4>
        <p className="fl-card-subtext">Select a location on the Home or Map page first to generate a real, location-specific advisory.</p>
      </div>
    )
  }

  return (
    <div className="fl-card" style={{ maxWidth: 640 }}>
      <h4>AI Advisory — {riskData.tier} Risk ({riskData.score}/100)</h4>
      <p className="fl-card-subtext">
        Location: {selectedPoint.lat}, {selectedPoint.lon}
        {profile.length > 0 && ` • Tailored for: ${profile.join(', ')}`}
      </p>
      <div className="fl-advisory-box">
        {advisoryLoading ? 'Generating advisory...' : advisoryText}
      </div>
    </div>
  )
}
