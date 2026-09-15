// api.js — every function maps 1:1 to a real FastAPI endpoint in api.py.
// Nothing here is mocked; if an endpoint fails, the caller sees a real
// error/loading state rather than fabricated data.

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function handle(res) {
  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(`API error ${res.status}: ${detail}`)
  }
  return res.json()
}

export async function getRisk(lat, lon, rainfallOverride = null) {
  const params = new URLSearchParams({ lat, lon })
  if (rainfallOverride !== null) params.append('rainfall_override', rainfallOverride)
  return handle(await fetch(`${BASE_URL}/risk?${params}`))
}

export async function getRiskGrid() {
  return handle(await fetch(`${BASE_URL}/risk/grid`))
}

export async function getVillages() {
  return handle(await fetch(`${BASE_URL}/villages`))
}

export async function getHistory(limit = 5) {
  return handle(await fetch(`${BASE_URL}/history?limit=${limit}`))
}

export async function getAdvisory(riskScore, tier, profile, language, rainfallMm, waterLevelM, breakdown) {
  return handle(await fetch(`${BASE_URL}/advisory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      risk_score: riskScore, tier, profile, language,
      rainfall_mm: rainfallMm, water_level_m: waterLevelM, breakdown,
    }),
  }))
}

export async function getShelters(lat, lon) {
  return handle(await fetch(`${BASE_URL}/shelters?lat=${lat}&lon=${lon}`))
}

export async function getRouteToShelter(lat, lon) {
  // Deliberately NOT wrapped to silently return [] like roads — a missing
  // route should surface as "unavailable" in the UI, not disappear silently.
  const res = await fetch(`${BASE_URL}/route-to-shelter?lat=${lat}&lon=${lon}`)
  if (!res.ok) return null
  return res.json()
}

export async function getWeather(lat, lon) {
  const res = await fetch(`${BASE_URL}/weather?lat=${lat}&lon=${lon}`)
  if (!res.ok) return null
  return res.json()
}

export async function registerSubscriber(payload) {
  return handle(await fetch(`${BASE_URL}/subscribers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
}

export async function sendOtp(phone) {
  return handle(await fetch(`${BASE_URL}/otp/send`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phone }),
  }))
}
export async function verifyOtp(phone, code) {
  return handle(await fetch(`${BASE_URL}/otp/verify`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phone, code }),
  }))
}

export async function getOtpEnabled() {
  const res = await fetch(`${BASE_URL}/otp/enabled`)
  const data = await res.json()
  return data.enabled
}

export async function getAdminStatus() {
  return handle(await fetch(`${BASE_URL}/admin/status`))
}

export async function getVapidPublicKey() {
  const res = await fetch(`${BASE_URL}/push/vapid-public-key`)
  return (await res.json()).key
}
export async function pushSubscribe(payload) {
  return handle(await fetch(`${BASE_URL}/push/subscribe`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }))
}