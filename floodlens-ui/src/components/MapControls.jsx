import { Navigation2, Layers } from 'lucide-react'

export default function MapControls({ onUseLocation, mapType, onToggleMapType }) {
  return (
    <>
      <div className="fl-map-controls">
        <button className="fl-map-control-btn" onClick={onToggleMapType} title="Switch map view">
          <Layers size={18} />
        </button>
        <button className="fl-map-control-btn" onClick={onUseLocation} title="Use My Location">
          <Navigation2 size={18} />
        </button>
        <div className="fl-compass" title="North">N</div>
      </div>

      {/* Small label showing the current view, so the layer toggle's effect is clear */}
      <div className="fl-maptype-label">{mapType === 'satellite' ? 'Satellite' : 'Standard'}</div>
    </>
  )
}
