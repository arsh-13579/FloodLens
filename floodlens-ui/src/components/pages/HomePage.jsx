import { useState } from 'react'
import { Menu } from 'lucide-react'
import MapView from '../MapView.jsx'
import FloatingInfoPanel from '../FloatingInfoPanel.jsx'
import MapControls from '../MapControls.jsx'

export default function HomePage({
  villages, selectedPoint, onSelect, onUseLocation, onClearSelection, onOpenMobile,
  gridPoints, shelters, route, weather,
  riskData, advisoryText, advisoryLoading,
  error,
}) {
  const [mapType, setMapType] = useState('satellite')
  const nearestShelter = shelters && shelters.length > 0 ? shelters[0] : null

  function toggleMapType() {
    setMapType((prev) => (prev === 'satellite' ? 'standard' : 'satellite'))
  }

  return (
    <div className="fl-home-fullscreen">
      <div className="fl-home-map-bg">
        <MapView
          villages={villages}
          selectedPoint={selectedPoint}
          onSelect={onSelect}
          gridPoints={gridPoints}
          shelters={shelters}
          routeToShelter={route}
          height="100vh"
          mapType={mapType}
          zoomPosition="bottomleft"
        />
      </div>

      {/* Mobile-only hamburger — the normal Header (which hosts this elsewhere) is hidden on this page */}
      <button className="fl-home-hamburger" onClick={onOpenMobile}><Menu size={20} /></button>

      <MapControls onUseLocation={onUseLocation} mapType={mapType} onToggleMapType={toggleMapType} />

      <FloatingInfoPanel
        selectedPoint={selectedPoint}
        villages={villages}
        riskData={riskData}
        advisoryText={advisoryText}
        advisoryLoading={advisoryLoading}
        nearestShelter={nearestShelter}
        route={route}
        onClose={onClearSelection}
        onViewRoute={() => {}}
      />

      {!selectedPoint && (
        <div className="fl-floating-hint">
          Click a point on the map, or use the locate button, to see a real-time risk report.
        </div>
      )}

      {error && <div className="fl-floating-error">{error}</div>}

      {weather && selectedPoint && (
        <div className="fl-floating-weather">
          {weather.condition}, {weather.temperature_c}°C
        </div>
      )}
    </div>
  )
}
