self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.use?.then((cache) => {})
  );
});
self.addEventListener('fetch', (e) => {});
