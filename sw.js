// SAB FX RADAR service worker: app works offline with the last downloaded data.
// Same-origin files: network first, cache as fallback. Rate API calls pass through untouched.
const VERSION = 'fxradar-v2';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'data.json',
  'icon-192.png', 'icon-512.png', 'icon-maskable.png', 'apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  const key = url.pathname.endsWith('data.json') ? new Request(url.origin + url.pathname) : e.request;
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(key, copy)); }
      return res;
    }).catch(() => caches.match(key).then(r => r || caches.match('index.html')))
  );
});
