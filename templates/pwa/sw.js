const CACHE = 'sportsvision-v1';

const PRECACHE = [
  '/',
  '/dashboard/',
  '/static/css/sportsvision.css',
  '/static/images/logo.png',
  '/static/images/gym_bg.jpg',
];

// Instalación: cachear recursos esenciales
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// Activación: limpiar caches viejos
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network first, cache como fallback
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (e.request.url.includes('/admin/')) return;

  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
