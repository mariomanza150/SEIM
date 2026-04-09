# SEIM Vue.js Frontend

Modern Vue.js 3 SPA frontend for the Student Exchange Information Management (SEIM) system.

## 🚀 Tech Stack

- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vite** - Next-generation frontend build tool
- **Vue Router 4** - Official routing library
- **Pinia** - Official state management
- **Axios** - HTTP client for API calls
- **Bootstrap 5** - CSS framework
- **Bootstrap Icons** - Icon library

## 📁 Project Structure

```
frontend-vue/
├── public/              # Static assets
├── src/
│   ├── assets/         # Images, fonts, etc.
│   ├── components/     # Reusable Vue components
│   ├── composables/    # Composition API composables
│   ├── router/         # Vue Router configuration
│   ├── services/       # API services (axios)
│   ├── stores/         # Pinia stores (state management)
│   ├── utils/          # Utility functions
│   ├── views/          # Page components
│   ├── App.vue         # Root component
│   ├── main.js         # Application entry point
│   └── style.css       # Global styles
├── .env                # Base environment variables
├── .env.development    # Development environment variables
├── .env.production     # Production environment variables
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies and scripts
```

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+ and npm
- Django backend running (via Docker)

### 1. Install Dependencies

```bash
cd frontend-vue
npm install
```

### 2. Start Django Backend (Docker)

In the project root directory:

```bash
# Start all services (Django, PostgreSQL, Redis, Celery)
docker-compose up -d

# Check services are running
docker-compose ps

# View Django logs
docker-compose logs -f web
```

Django will be available at: `http://localhost:8001`

### 3. Start Vue Dev Server

```bash
# From frontend-vue directory
npm run dev
```

Vue dev server will be available at: `http://localhost:5173`

The Vite dev server automatically proxies API calls to Django:
- `/api/*` → `http://localhost:8001/api/*`
- `/media/*` → `http://localhost:8001/media/*`
- `/seim/admin/*` → `http://localhost:8001/seim/admin/*`
- `/cms/*` → `http://localhost:8001/cms/*`

### 4. Access the Application

Open your browser to `http://localhost:5173`

**Test Credentials** (if test data is seeded):
- Email: `test@example.com`
- Password: `testpass123`

## 📝 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests in watch mode
npm run test

# Run tests once
npm run test:run
```

## 🔗 API Integration

### Authentication

The app uses JWT token authentication with Django:

1. **Login**: POST `/api/token/` with email and password
2. **Token Refresh**: POST `/api/token/refresh/` with refresh token
3. **Profile**: GET `/api/accounts/profile/` with Bearer token

### API Service (`src/services/api.js`)

Pre-configured Axios instance with:
- Base URL from environment variable
- JWT token injection
- Automatic token refresh on 401
- Request/response interceptors

### Auth Store (`src/stores/auth.js`)

Pinia store managing:
- User state
- JWT tokens (localStorage)
- Login/logout actions
- Token refresh logic
- User profile fetching

## 🧭 Routing

Routes are defined in `src/router/index.js`:

| Route | Component | Auth Required | Description |
|-------|-----------|---------------|-------------|
| `/login` | Login | No | Login page |
| `/` | - | Yes | Redirects to dashboard |
| `/dashboard` | Dashboard | Yes | Main dashboard |
| `/applications` | Applications | Yes | Application list |
| `/applications/new` | ApplicationForm | Yes | Create application |
| `/applications/:id/edit` | ApplicationForm | Yes | Edit application |
| `/applications/:id` | ApplicationDetail | Yes | Application details |
| `/documents` | Documents | Yes | Documents list |
| `/documents/:id` | DocumentDetail | Yes | Document details |
| `/notifications` | Notifications | Yes | Notifications list |
| `/profile` | Profile | Yes | User profile |
| `/settings` | - | Yes | Redirects to profile |
| `/:pathMatch(.*)*` | NotFound | No | 404 page |

### Route Guards

The router automatically:
- Redirects unauthenticated users to `/login`
- Redirects authenticated users away from `/login`
- Checks token validity on protected routes
- Updates page titles

## 🔧 Configuration

### Environment Variables

Set in `.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_WS_BASE_URL=ws://localhost:8001
VITE_APP_NAME=SEIM
VITE_APP_VERSION=2.0.0-vue
VITE_DEBUG=true
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

### Vite Proxy

Configured in `vite.config.js` to forward requests to Django:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
  }
}
```

## 🏗️ Building for Production

### Development Build (Local)

```bash
npm run build
```

Output: `dist/` directory

### Docker Build (Integrated)

The main `Dockerfile` includes a multi-stage build:

1. **Stage 1**: Build Vue.js with Node.js
2. **Stage 2**: Copy Vue dist to Django static files

```bash
# Build and run production
docker-compose -f docker-compose.yml up --build
```

Django will serve the Vue app from `frontend-vue/dist/` and static assets from `frontend-vue/dist/assets/`.

## 📚 Key Features

### ✅ Implemented

- JWT authentication with automatic refresh
- Login page with form validation
- Dashboard with user info and navigation
- Applications list, detail, create, and edit flows
- Documents list and detail views
- Notifications center
- User profile view
- WebSocket notification service integration
- API service with interceptors
- Auth state management (Pinia)
- Route guards
- Responsive design (Bootstrap 5)
- Error handling
- Unit tests with Vitest for services, stores, and login flow

### 🚧 In Progress / Follow-up Work

- Settings page currently redirects to profile
- Analytics dashboard
- Multi-language support
- Accessibility features
- Broader component and route coverage in Vitest
- Expanded Playwright coverage

## 🐛 Troubleshooting

### CORS Errors

Make sure Django CORS settings allow `http://localhost:5173`:

```python
# seim/settings/development.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### API 404 Errors

1. Check Django is running: `docker-compose ps`
2. Check Django logs: `docker-compose logs web`
3. Verify API endpoints: `http://localhost:8001/api/docs/`

### Authentication Loop

1. Clear browser localStorage
2. Check JWT token expiration in Django settings
3. Verify token refresh logic in auth store

### Vue Dev Server Won't Start

1. Check port 5173 is not in use
2. Delete `node_modules` and reinstall: `npm ci`
3. Check Node.js version: `node --version` (need 18+)

## 📖 Documentation

- [Vue.js 3 Docs](https://vuejs.org/)
- [Vite Docs](https://vitejs.dev/)
- [Vue Router Docs](https://router.vuejs.org/)
- [Pinia Docs](https://pinia.vuejs.org/)
- [Bootstrap 5 Docs](https://getbootstrap.com/)
- [Axios Docs](https://axios-http.com/)

## 🤝 Contributing

1. Create a feature branch from `feature/vue-migration`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages
5. Create a pull request

## 📄 License

Same as the main SEIM project.

---

**Built with ❤️ for SEIM**
