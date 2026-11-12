self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('medical-ai-cache-v1').then((cache) => cache.addAll(['/']))
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;

      return fetch(event.request).then((response) => {
        const copy = response.clone();
        caches.open('medical-ai-cache-v1').then((cache) => cache.put(event.request, copy));
        return response;
      }).catch(() => cached || responseFallback(event.request));
    })
  );
});

function responseFallback(request) {
  if (request.mode === 'navigate') {
    return caches.match('/');
  }
  return new Response('Offline', { status: 503, statusText: 'Offline' });
}
