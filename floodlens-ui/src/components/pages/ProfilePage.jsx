import { useState } from 'react'
import RegisterForm from '../RegisterForm.jsx'
import { getVapidPublicKey, pushSubscribe } from '../../api.js'
import { useToast } from '../Toast.jsx'

const VULNERABLE_OPTIONS = ['Elderly', 'Accessibility', 'Child', 'Medical', 'Pet']

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)))
}

export default function ProfilePage({ profile, setProfile, selectedPoint, language }) {
  const toast = useToast()
  const [pushLoading, setPushLoading] = useState(false)

  function toggle(item) {
    setProfile((prev) => (prev.includes(item) ? prev.filter((p) => p !== item) : [...prev, item]))
  }

  async function enablePush() {
    if (!selectedPoint) {
      toast('Select a location first (Home or Map page).', 'warning')
      return
    }
    setPushLoading(true)
    try {
      const reg = await navigator.serviceWorker.ready
      const key = await getVapidPublicKey()
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(key),
      })
      const subJson = sub.toJSON()
      await pushSubscribe({
        endpoint: subJson.endpoint,
        keys: subJson.keys,
        latitude: selectedPoint.lat,
        longitude: selectedPoint.lon,
        location_label: 'Push subscription',
      })
      toast('Push notifications enabled!', 'success')
    } catch (err) {
      toast(`Push setup failed: ${err.message}`, 'warning')
    } finally {
      setPushLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 480 }}>
      <div className="fl-card">
        <h4>Vulnerable Groups</h4>
        <p className="fl-card-subtext">Tailors your AI Advisory wording. Used for every location you select.</p>
        <div className="fl-profile-grid">
          {VULNERABLE_OPTIONS.map((item) => (
            <label key={item} className="fl-checkbox">
              <input type="checkbox" checked={profile.includes(item)} onChange={() => toggle(item)} />
              {item}
            </label>
          ))}
        </div>
      </div>

      <div className="fl-card">
        <h4>Push Notifications</h4>
        <p className="fl-card-subtext">Free alert channel, no phone number needed — works in this browser.</p>
        <button className="fl-btn" onClick={enablePush} disabled={pushLoading}>
          {pushLoading ? 'Enabling...' : 'Enable Push Notifications'}
        </button>
      </div>

      <RegisterForm selectedPoint={selectedPoint} language={language} profile={profile} />
    </div>
  )
}
