import { Waves, Menu } from 'lucide-react'

export default function Header({ language, setLanguage, onOpenMobile }) {
  return (
    <div className="fl-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="fl-hamburger" onClick={onOpenMobile}><Menu size={22} /></button>
        <div>
          <div className="fl-header-logo">
            <Waves size={20} className="fl-accent" style={{ verticalAlign: 'middle', marginRight: 6 }} />
            Flood<span className="fl-accent">Lens</span>
          </div>
          <div className="fl-header-tagline">Know the Risk. Choose the Safer Path.</div>
        </div>
      </div>
      <select className="fl-lang-select" value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="English">EN</option>
        <option value="Hindi">HI</option>
      </select>
    </div>
  )
}
