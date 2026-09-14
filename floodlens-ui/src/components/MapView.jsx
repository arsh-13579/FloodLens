import { MapContainer, TileLayer, Marker, CircleMarker, Popup, Polyline, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import HeatmapLayer from './HeatmapLayer.jsx'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const shelterIcon = L.divIcon({
  className: 'fl-shelter-icon',
  html: '🏠',
  iconSize: [28, 28],
})

function ClickHandler({ onSelect }) {
  useMapEvents({ click(e) { onSelect(e.latlng.lat, e.latlng.lng) } })
  return null
}

export default function MapView({
  villages, selectedPoint, onSelect,
  gridPoints, shelters, routeToShelter,
  height = '560px', showHeatmap = true,
}) {
  return (
    <MapContainer center={[26.7606, 83.3732]} zoom={11} style={{ height, width: '100%', borderRadius: '14px' }}>
      {/* Real Esri satellite imagery — free, no API key required */}
      <TileLayer
        attribution='Tiles &copy; Esri'
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
      />

      <ClickHandler onSelect={onSelect} />

      {showHeatmap && gridPoints && gridPoints.length > 0 && <HeatmapLayer points={gridPoints} />}

      {villages.map((v) => (
        <CircleMarker key={v.name} center={[v.lat, v.lon]} radius={5} color="#60a5fa" fillOpacity={0.6}>
          <Popup>{v.name}</Popup>
        </CircleMarker>
      ))}

      {shelters && shelters.map((s) => (
        <Marker key={s.name} position={[s.lat, s.lon]} icon={shelterIcon}>
          <Popup>{s.name} — {s.distance_km} km away</Popup>
        </Marker>
      ))}

      {selectedPoint && (
        <Marker position={[selectedPoint.lat, selectedPoint.lon]}>
          <Popup>Selected Location</Popup>
        </Marker>
      )}

      {routeToShelter && routeToShelter.segments && routeToShelter.segments.length > 0 ? (
        routeToShelter.segments.map((seg, i) => (
          <Polyline
            key={i}
            positions={seg.coordinates}
            pathOptions={{ color: seg.color, weight: 6, opacity: 0.9 }}
          />
        ))
      ) : (
        routeToShelter && routeToShelter.coordinates && (
          <Polyline
            positions={routeToShelter.coordinates}
            pathOptions={{ color: '#3b82f6', weight: 5, dashArray: '8, 8' }}
          />
        )
      )}
    </MapContainer>
  )
}
