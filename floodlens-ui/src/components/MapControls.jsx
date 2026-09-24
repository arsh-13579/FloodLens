import { Navigation2 } from 'lucide-react'

export default function MapControls({ onUseLocation }) {
  return (
    <div className="fl-map-controls">
      <button className="fl-map-control-btn" onClick={onUseLocation} title="Use My Location">
        <Navigation2 size={18} />
      </button>
    </div>
  )
}
