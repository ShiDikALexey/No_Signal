const CACHE = 'nosignal-v1';

const SHELL = [
    '/',
    '/static/style.css',
    '/static/main.js',
    '/static/socket.io.min.js',
    '/static/favicon.svg'
];

self.addEventListener('install', evt => {
    evt.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(SHELL))
    );
    self.skipWaiting();
});

self.addEventListener('activate', evt => {
    evt.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', evt => {
    const url = new URL(evt.request.url);

    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/auth/') || url.pathname.startsWith('/socket.io/')) {
        return;
    }

    evt.respondWith(
        caches.match(evt.request).then(cached => cached || fetch(evt.request))
    );
});
