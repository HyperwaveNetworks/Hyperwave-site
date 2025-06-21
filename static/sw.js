// Service Worker for Hyperwave Networks
// Version 1.0 - Performance Optimization

const CACHE_NAME = 'hyperwave-v1.0';
const STATIC_CACHE = 'hyperwave-static-v1.0';
const API_CACHE = 'hyperwave-api-v1.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/critical.css',
    '/static/css/style.css',
    '/static/css/responsive.css',
    '/static/js/main.js',
    '/static/js/mobile-menu.js',
    '/static/images/logo.png',
    '/about/',
    '/services/',
    '/contact/',
    '/packages/',
    '/blog/',
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);

    // Handle static files
    if (request.url.includes('/static/') || request.url.includes('/media/')) {
        event.respondWith(
            caches.match(request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(request).then(fetchResponse => {
                        const responseClone = fetchResponse.clone();
                        caches.open(STATIC_CACHE)
                            .then(cache => cache.put(request, responseClone));
                        return fetchResponse;
                    });
                })
        );
        return;
    }

    // Handle page requests - Cache First for better performance
    if (request.method === 'GET' && request.headers.get('accept') && request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            caches.match(request)
                .then(response => {
                    if (response) {
                        // Serve from cache immediately
                        fetch(request).then(fetchResponse => {
                            if (fetchResponse.ok) {
                                caches.open(CACHE_NAME)
                                    .then(cache => cache.put(request, fetchResponse));
                            }
                        }).catch(() => {});
                        return response;
                    }
                    
                    // Not in cache, fetch from network
                    return fetch(request).then(fetchResponse => {
                        if (fetchResponse.ok) {
                            const responseClone = fetchResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => cache.put(request, responseClone));
                        }
                        return fetchResponse;
                    }).catch(() => {
                        // Network failed, serve basic offline response
                        return new Response('Offline - Please check your connection', { status: 503 });
                    });
                })
        );
        return;
    }

    // Default: network first
    event.respondWith(
        fetch(request).catch(() => caches.match(request))
    );
});

// Check if cached response is still fresh (5 minutes for API)
function isResponseFresh(response) {
    const cachedTime = response.headers.get('sw-cached-time');
    if (!cachedTime) return false;
    
    const now = Date.now();
    const cacheTime = parseInt(cachedTime);
    return (now - cacheTime) < 300000; // 5 minutes
}

// Background sync for offline form submissions
self.addEventListener('sync', event => {
    if (event.tag === 'contact-form') {
        event.waitUntil(syncContactForms());
    }
});

async function syncContactForms() {
    // Implementation for offline form sync
    console.log('Syncing contact forms...');
}

// Push notifications (future feature)
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        event.waitUntil(
            self.registration.showNotification(data.title, {
                body: data.body,
                icon: '/static/images/logo.png',
                badge: '/static/images/logo.png'
            })
        );
    }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
}); 