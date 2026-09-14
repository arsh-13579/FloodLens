import { MapPin } from 'lucide-react'
import MapView from '../MapView.jsx'
import { RiskAlertCard, RiskBreakdownCard, AdvisoryCard, ShelterRouteCard, WeatherLocationBar } from '../HomeCards.jsx'

export default function HomePage({
  villages, selectedPoint, onSelect, onUseLocation,
  gridPoints, shelters, route, weather,
  riskData, advisoryText, advisoryLoading,
  error,
}) {
  const nearestShelter = shelters && shelters.length > 0 ? shelters[0] : null

  return (
    <div className="fl-page-grid">
      <div className="fl-map-col">
        <div className="fl-map-toolbar">
          <button className="fl-btn" onClick={onUseLocation} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <MapPin size={16} /> Use My Location
          </button>
        </div>
        <MapView
          villages={villages}
          selectedPoint={selectedPoint}
          onSelect={onSelect}
          gridPoints={gridPoints}
          shelters={shelters}
          routeToShelter={route}
        />
        <WeatherLocationBar selectedPoint={selectedPoint} weather={weather} />
      </div>

      <div className="fl-panel-col">
        {error && <div className="fl-card fl-status-warning">{error}</div>}
        {!selectedPoint && (
          <div className="fl-card">
            <h4>Get Started</h4>
            <p className="fl-card-subtext">Click a point on the map, or use "Use My Location", to see your real-time risk report.</p>
          </div>
        )}
        {selectedPoint && riskData && (
          <>
            <RiskAlertCard riskData={riskData} />
            <RiskBreakdownCard breakdown={riskData.breakdown} />
            <AdvisoryCard advisoryText={advisoryText} loading={advisoryLoading} />
            <ShelterRouteCard nearestShelter={nearestShelter} route={route} onViewRoute={() => {}} />
          </>
        )}
      </div>
    </div>
  )
}
