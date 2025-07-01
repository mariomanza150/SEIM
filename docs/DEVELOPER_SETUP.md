# Developer Setup Guide

This guide helps developers set up their local development environment for the SEIM project.

---

## Prerequisites
- **Git** for version control
- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Python 3.12+** (for local development without Docker)
- **Code Editor** (VS Code, PyCharm, etc.)
- **PostgreSQL client** (optional, for database access)

---

## Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd SGII
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your settings:
# - SECRET_KEY (generate a new one)
# - DATABASE_URL (if not using Docker)
# - REDIS_URL (for Celery)
# - AWS_* (if using S3)
```

---

## Docker-based Development (Recommended)

### 3. Start Services
```bash
docker-compose up
```

### 4. Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 5. Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

- Access the app: http://localhost:8000
- Access the database: localhost:5432 (seim/seim_user/seim_pass)

---

## Local Python Development (Advanced/Optional)

1. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables as above.
4. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

---

## Useful Commands
- Run tests: `docker-compose exec web python manage.py test`
- Collect static files: `docker-compose exec web python manage.py collectstatic`
- Access Django shell: `docker-compose exec web python manage.py shell`

---

## Troubleshooting
See [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Revision History
- 2025-05-31: Updated for Python 3.12, Docker Compose, and new environment variables.
