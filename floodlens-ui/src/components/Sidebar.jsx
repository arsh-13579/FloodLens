import { Home, Map, Lightbulb, CloudRain, User, Clock, ShieldCheck, X, Waves } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'map', label: 'Map', Icon: Map },
  { id: 'advisory', label: 'AI Advisory', Icon: Lightbulb },
  { id: 'whatif', label: 'Rainfall What-If', Icon: CloudRain },
  { id: 'profile', label: 'Profile & Needs', Icon: User },
  { id: 'activity', label: 'Recent Activity', Icon: Clock },
  { id: 'admin', label: 'Admin', Icon: ShieldCheck },
]

export default function Sidebar({
  activePage, onNavigate, mobileOpen, onCloseMobile,
  floating = false, language, setLanguage,
}) {
  return (
    <>
      {mobileOpen && <div className="fl-sidebar-overlay" onClick={onCloseMobile} />}
      <div className={`fl-sidebar ${floating ? 'fl-sidebar-floating' : ''} ${mobileOpen ? 'fl-sidebar-open' : ''}`}>
        {floating && (
          <div className="fl-sidebar-brand">
            <div className="fl-sidebar-brand-row">
              <div className="fl-sidebar-logo"><Waves size={18} className="fl-accent" /> Flood<span className="fl-accent">Lens</span></div>
              {setLanguage && (
                <select className="fl-lang-select fl-lang-select-small" value={language} onChange={(e) => setLanguage(e.target.value)}>
                  <option value="English">EN</option>
                  <option value="Hindi">HI</option>
                </select>
              )}
            </div>
            <div className="fl-sidebar-tagline">Know the Risk. Choose the Safer Path.</div>
          </div>
        )}

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
