import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

// react-leaflet has no built-in heatmap component, so this wraps
// leaflet.heat imperatively via useMap(). Fed entirely by real per-point
// scores from /risk/grid (district_grid.py) — every point plotted here
// is an actual computed risk score, not a decorative gradient.
export default function HeatmapLayer({ points }) {
  const map = useMap()

  useEffect(() => {
    if (!points || points.length === 0) return

    // leaflet.heat expects [lat, lon, intensity] with intensity 0-1
    const heatData = points.map((p) => [p.lat, p.lon, p.score / 100])

    const heatLayer = L.heatLayer(heatData, {
      radius: 55,
      blur: 40,
      maxZoom: 13,
      minOpacity: 0.3,
      gradient: { 0.0: '#2ecc71', 0.35: '#f1c40f', 0.6: '#e67e22', 0.85: '#e74c3c' },
    })

    heatLayer.addTo(map)
    return () => { map.removeLayer(heatLayer) }
  }, [points, map])

  return null
}
