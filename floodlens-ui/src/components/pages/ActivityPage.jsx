import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function ActivityPage({ recentActivity }) {
  // recentActivity comes newest-first from /history — reverse for a left-to-right timeline
  const chartData = [...recentActivity].reverse().map((r) => ({
    time: r.timestamp.slice(11, 16),
    score: r.score,
  }))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 640 }}>
      <div className="fl-card">
        <h4>Risk Score Trend</h4>
        {chartData.length < 2 ? (
          <p className="fl-card-subtext">Need at least 2 queries to show a trend.</p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="time" fontSize={12} stroke="#64748b" />
              <YAxis domain={[0, 100]} fontSize={12} stroke="#64748b" />
              <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8 }} />
              <Line type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="fl-card">
        <h4>Recent Activity</h4>
        {recentActivity.length === 0 ? (
          <p className="fl-card-subtext">No queries yet — select a location on Home or Map.</p>
        ) : (
          recentActivity.map((r, i) => (
            <div key={i} className="fl-activity-row">
              <span>{r.latitude.toFixed(3)}, {r.longitude.toFixed(3)}</span>
              <span className="fl-activity-score">{r.score}</span>
              <span className="fl-card-subtext">{r.timestamp.slice(11, 16)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
