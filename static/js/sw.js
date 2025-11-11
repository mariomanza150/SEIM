/**
 * SEIM Service Worker
 * Provides caching, offline support, and performance optimization
 */

const CACHE_NAME = 'seim-v1.0.0';
const STATIC_CACHE = 'seim-static-v1.0.0';
const API_CACHE = 'seim-api-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/auth.js',
    '/templates/base.html',
    '/static/img/logo.png'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/programs/',
    '/api/application-statuses/',
    '/api/document-types/',
    '/api/notification-types/'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache static files
            caches.open(STATIC_CACHE).then(cache => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            }),
            
            // Cache API endpoints
            caches.open(API_CACHE).then(cache => {
                console.log('Caching API endpoints');
                return cache.addAll(API_ENDPOINTS);
            })
        ]).then(() => {
            console.log('Service Worker installed successfully');
            return self.skipWaiting();
        })
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
        }).then(() => {
            console.log('Service Worker activated successfully');
            return self.clients.claim();
        })
    );
});

// Fetch event - handle requests
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle static files
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(handleStaticFile(request));
        return;
    }
    
    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }
    
    // Handle HTML pages
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(handleHtmlRequest(request));
        return;
    }
});

/**
 * Handle static file requests
 */
async function handleStaticFile(request) {
    try {
        // Try network first, fallback to cache
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache the response for future use
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
    } catch (error) {
        console.log('Network failed for static file:', request.url);
    }
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // Return offline page if available
    return new Response('Offline - Static file not available', {
        status: 503,
        statusText: 'Service Unavailable'
    });
}

/**
 * Handle API requests
 */
async function handleApiRequest(request) {
    const url = new URL(request.url);
    
    // For GET requests, try cache first, then network
    if (request.method === 'GET') {
        try {
            // Check cache first
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
                // Return cached response immediately
                return cachedResponse;
            }
            
            // Try network
            const networkResponse = await fetch(request);
            
            if (networkResponse.ok) {
                // Cache successful responses
                const cache = await caches.open(API_CACHE);
                cache.put(request, networkResponse.clone());
                return networkResponse;
            }
        } catch (error) {
            console.log('Network failed for API request:', request.url);
        }
        
        // Return cached response if available
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
    } else {
        // For non-GET requests, try network first
        try {
            const networkResponse = await fetch(request);
            return networkResponse;
        } catch (error) {
            console.log('Network failed for API request:', request.url);
        }
    }
    
    // Return error response
    return new Response(JSON.stringify({
        error: 'Offline - API not available',
        message: 'Please check your internet connection and try again.'
    }), {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

/**
 * Handle HTML requests
 */
async function handleHtmlRequest(request) {
    try {
        // Try network first for HTML
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            return networkResponse;
        }
    } catch (error) {
        console.log('Network failed for HTML request:', request.url);
    }
    
    // Return offline page
    return new Response(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SEIM - Offline</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background-color: #f8f9fa;
                }
                .offline-container {
                    text-align: center;
                    padding: 2rem;
                    background: white;
                    border-radius: 0.375rem;
                    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
                    max-width: 400px;
                }
                .offline-icon {
                    font-size: 3rem;
                    color: #6c757d;
                    margin-bottom: 1rem;
                }
                h1 {
                    color: #212529;
                    margin-bottom: 1rem;
                }
                p {
                    color: #6c757d;
                    margin-bottom: 1.5rem;
                }
                .btn {
                    background-color: #0d6efd;
                    color: white;
                    padding: 0.5rem 1rem;
                    border: none;
                    border-radius: 0.375rem;
                    text-decoration: none;
                    display: inline-block;
                }
                .btn:hover {
                    background-color: #0b5ed7;
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📡</div>
                <h1>You're Offline</h1>
                <p>Please check your internet connection and try again.</p>
                <a href="/" class="btn">Retry</a>
            </div>
        </body>
        </html>
    `, {
        status: 200,
        headers: {
            'Content-Type': 'text/html'
        }
    });
}

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(performBackgroundSync());
    }
});

/**
 * Perform background sync
 */
async function performBackgroundSync() {
    try {
        // Get stored offline actions
        const offlineActions = await getOfflineActions();
        
        for (const action of offlineActions) {
            try {
                // Retry the action
                const response = await fetch(action.url, action.options);
                
                if (response.ok) {
                    // Remove successful action from storage
                    await removeOfflineAction(action.id);
                }
            } catch (error) {
                console.log('Background sync failed for action:', action.id);
            }
        }
    } catch (error) {
        console.log('Background sync failed:', error);
    }
}

/**
 * Store offline action for later sync
 */
async function storeOfflineAction(action) {
    const actions = await getOfflineActions();
    actions.push({
        id: Date.now().toString(),
        ...action,
        timestamp: Date.now()
    });
    
    localStorage.setItem('offline-actions', JSON.stringify(actions));
}

/**
 * Get stored offline actions
 */
async function getOfflineActions() {
    try {
        const actions = localStorage.getItem('offline-actions');
        return actions ? JSON.parse(actions) : [];
    } catch (error) {
        return [];
    }
}

/**
 * Remove offline action
 */
async function removeOfflineAction(actionId) {
    const actions = await getOfflineActions();
    const filteredActions = actions.filter(action => action.id !== actionId);
    localStorage.setItem('offline-actions', JSON.stringify(filteredActions));
}

/**
 * Push notification handling
 */
self.addEventListener('push', event => {
    console.log('Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from SEIM',
        icon: '/static/img/logo.png',
        badge: '/static/img/badge.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View',
                icon: '/static/img/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/img/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('SEIM Notification', options)
    );
});

/**
 * Notification click handling
 */
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', event => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_API') {
        event.waitUntil(
            caches.open(API_CACHE).then(cache => {
                return cache.add(event.data.url);
            })
        );
    }
}); 