@echo off
echo Stopping and removing Docker containers...
docker-compose down

echo Removing old containers (if any)...
docker rm sgii-web-1 sgii-db-1 2>NUL

echo Rebuilding images...
docker-compose build --no-cache

echo Starting services...
docker-compose up -d

echo Checking logs...
timeout /t 5 /nobreak > NUL
docker-compose logs --tail 50

echo Done! The application should be running at http://localhost:8000
