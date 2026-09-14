import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Header from './components/Header.jsx'
import HomePage from './components/pages/HomePage.jsx'
import MapPage from './components/pages/MapPage.jsx'
import AdvisoryPage from './components/pages/AdvisoryPage.jsx'
import WhatIfPage from './components/pages/WhatIfPage.jsx'
import ProfilePage from './components/pages/ProfilePage.jsx'
import ActivityPage from './components/pages/ActivityPage.jsx'
import AdminPage from './components/pages/AdminPage.jsx'
import { useToast } from './components/Toast.jsx'
import {
  getRisk, getVillages, getAdvisory, getShelters, getRouteToShelter,
  getWeather, getHistory, getRiskGrid,
} from './api.js'

export default function App() {
  const [activePage, setActivePage] = useState('home')
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const toast = useToast()

  const [villages, setVillages] = useState([])
  const [gridPoints, setGridPoints] = useState([])
  const [selectedPoint, setSelectedPoint] = useState(null)

  const [language, setLanguage] = useState('English')
  const [profile, setProfile] = useState([])

  const [riskData, setRiskData] = useState(null)
  const [advisoryText, setAdvisoryText] = useState('')
  const [advisoryLoading, setAdvisoryLoading] = useState(false)
  const [shelters, setShelters] = useState([])
  const [route, setRoute] = useState(null)
  const [weather, setWeather] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])
  const [error, setError] = useState(null)

  // One-time real data loads.
  useEffect(() => {
    getVillages().then(setVillages).catch((e) => console.error(e))
    getRiskGrid().then((d) => setGridPoints(d.points)).catch((e) => console.error('Grid load failed:', e))
    refreshActivity()
  }, [])

  function refreshActivity() {
    getHistory(8).then(setRecentActivity).catch((e) => console.error(e))
  }

  // Core reaction: whenever a point is selected, fetch everything real for it.
  useEffect(() => {
    if (!selectedPoint) return
    let cancelled = false
    setError(null)

    async function loadAll() {
      try {
        const risk = await getRisk(selectedPoint.lat, selectedPoint.lon)
        if (cancelled) return
        setRiskData(risk)
        if (risk.alert_sent) toast(`🚨 SMS alert triggered — tier: ${risk.tier}`, 'warning')
        refreshActivity()

        setAdvisoryLoading(true)
        getAdvisory(risk.score, risk.tier, profile, language, risk.rainfall_mm, risk.water_level_m, risk.breakdown)
          .then((a) => { if (!cancelled) setAdvisoryText(a.advisory) })
          .catch((e) => setError(`Advisory failed: ${e.message}`))
          .finally(() => { if (!cancelled) setAdvisoryLoading(false) })

        getShelters(selectedPoint.lat, selectedPoint.lon)
          .then((s) => { if (!cancelled) setShelters(s) })
          .catch((e) => console.error('Shelters failed:', e))

        getRouteToShelter(selectedPoint.lat, selectedPoint.lon)
          .then((r) => { if (!cancelled) setRoute(r) })
          .catch((e) => console.error('Route failed:', e))

        getWeather(selectedPoint.lat, selectedPoint.lon)
          .then((w) => { if (!cancelled) setWeather(w) })
          .catch((e) => console.error('Weather failed:', e))
      } catch (e) {
        if (!cancelled) setError(`Couldn't fetch risk: ${e.message}`)
      }
    }

    loadAll()
    return () => { cancelled = true }
  }, [selectedPoint, language])

  function handleSelect(lat, lon) {
    setSelectedPoint({ lat: Number(lat.toFixed(4)), lon: Number(lon.toFixed(4)) })
  }

  function handleUseLocation() {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.')
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => handleSelect(pos.coords.latitude, pos.coords.longitude),
      (err) => alert(`Couldn't get your location: ${err.message}`)
    )
  }

  const pageProps = {
    villages, selectedPoint, onSelect: handleSelect, onUseLocation: handleUseLocation,
    gridPoints, shelters, route, weather,
    riskData, advisoryText, advisoryLoading, error,
    profile, setProfile, language, recentActivity,
  }

  return (
      <div className="fl-shell">
        <Sidebar
          activePage={activePage}
          onNavigate={setActivePage}
          mobileOpen={mobileNavOpen}
          onCloseMobile={() => setMobileNavOpen(false)}
        />
        <div className="fl-main">
          <Header language={language} setLanguage={setLanguage} onOpenMobile={() => setMobileNavOpen(true)} />
          <div className="fl-content" key={activePage}>
            {activePage === 'home' && <HomePage {...pageProps} />}
            {activePage === 'map' && <MapPage {...pageProps} />}
            {activePage === 'advisory' && <AdvisoryPage {...pageProps} />}
            {activePage === 'whatif' && <WhatIfPage {...pageProps} />}
            {activePage === 'profile' && <ProfilePage {...pageProps} />}
            {activePage === 'activity' && <ActivityPage {...pageProps} />}
            {activePage === 'admin' && <AdminPage {...pageProps} />}
          </div>
        </div>
      </div>
  )
}
