import { useState, useEffect } from 'react'
import { Smartphone } from 'lucide-react'
import { registerSubscriber, sendOtp, verifyOtp, getOtpEnabled } from '../api.js'
import { useToast } from './Toast.jsx'

export default function RegisterForm({ selectedPoint, language, profile }) {
  const [phone, setPhone] = useState('')
  const [label, setLabel] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState('phone')
  const [otpEnabled, setOtpEnabled] = useState(false)
  const toast = useToast()

  useEffect(() => { getOtpEnabled().then(setOtpEnabled).catch(() => setOtpEnabled(false)) }, [])

  async function register() {
    await registerSubscriber({
      phone_number: phone, latitude: selectedPoint.lat, longitude: selectedPoint.lon,
      location_label: label, language, profile,
    })
    toast(`Registered ${phone} for alerts at ${label}!`, 'success')
    setPhone(''); setLabel(''); setCode(''); setStep('phone')
  }

  async function handleSubmitPhone(e) {
    e.preventDefault()
    if (!selectedPoint) { toast('Select a location first, then register.', 'warning'); return }
    if (!otpEnabled) {
      try { await register() } catch (err) { toast(`Failed: ${err.message}`, 'warning') }
      return
    }
    try {
      await sendOtp(phone)
      setStep('code')
      toast('Code sent — check your phone.', 'success')
    } catch (err) {
      toast(`Couldn't send code: ${err.message}`, 'warning')
    }
  }

  async function handleVerifyAndRegister(e) {
    e.preventDefault()
    try {
      const result = await verifyOtp(phone, code)
      if (!result.verified) { toast('Incorrect code.', 'warning'); return }
      await register()
    } catch (err) {
      toast(`Failed: ${err.message}`, 'warning')
    }
  }

  return (
    <div className="fl-card">
      <h4><Smartphone size={16} style={{ verticalAlign: 'middle', marginRight: 6 }} />Register for Alerts</h4>
      {step === 'phone' ? (
        <form onSubmit={handleSubmitPhone} className="fl-form">
          <input type="text" placeholder="Phone number (e.g. +91...)" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          <input type="text" placeholder="Location name (e.g. 'My home')" value={label} onChange={(e) => setLabel(e.target.value)} required />
          <button type="submit" className="fl-btn">{otpEnabled ? 'Send Verification Code' : 'Register'}</button>
        </form>
      ) : (
        <form onSubmit={handleVerifyAndRegister} className="fl-form">
          <input type="text" placeholder="6-digit code" value={code} onChange={(e) => setCode(e.target.value)} required />
          <button type="submit" className="fl-btn">Verify & Register</button>
        </form>
      )}
    </div>
  )
}