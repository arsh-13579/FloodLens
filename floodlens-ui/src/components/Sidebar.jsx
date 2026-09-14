import { Home, Map, Lightbulb, CloudRain, User, Clock, ShieldCheck, Settings, X } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'map', label: 'Map', Icon: Map },
  { id: 'advisory', label: 'AI Advisory', Icon: Lightbulb },
  { id: 'whatif', label: 'Rainfall What-If', Icon: CloudRain },
  { id: 'profile', label: 'Profile & Needs', Icon: User },
  { id: 'activity', label: 'Recent Activity', Icon: Clock },
  { id: 'admin', label: 'Admin', Icon: Settings },
]

export default function Sidebar({ activePage, onNavigate, mobileOpen, onCloseMobile }) {
  return (
    <>
      {mobileOpen && <div className="fl-sidebar-overlay" onClick={onCloseMobile} />}
      <div className={`fl-sidebar ${mobileOpen ? 'fl-sidebar-open' : ''}`}>
        <button className="fl-sidebar-close" onClick={onCloseMobile}><X size={20} /></button>
        <nav>
          {NAV_ITEMS.map(({ id, label, Icon }) => (
            <button
              key={id}
              className={`fl-nav-item ${activePage === id ? 'fl-nav-active' : ''}`}
              onClick={() => { onNavigate(id); onCloseMobile() }}
            >
              <Icon size={18} className="fl-nav-icon" />
              {label}
            </button>
          ))}
        </nav>
        <div className="fl-sidebar-footer">
          <ShieldCheck size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
          Safer Communities.<br />Stronger Tomorrow.
        </div>
      </div>
    </>
  )
}
