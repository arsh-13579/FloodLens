self.addEventListener('push', (event) => {
  console.log('Push event received!', event.data)
  let data = { title: 'FloodLens', body: 'Flood risk update' }
  try {
    data = event.data.json()
    console.log('Parsed JSON:', data)
  } catch (e) {
    if (event.data) data.body = event.data.text()
    console.log('Used text fallback:', data)
  }
  event.waitUntil(
    self.registration.showNotification(data.title, { body: data.body })
      .then(() => console.log('showNotification resolved OK'))
      .catch((err) => console.error('showNotification FAILED:', err))
  )
})