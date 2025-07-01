#!/bin/bash
# Docker management script for SGII project

ACTION=$1

case $ACTION in
  "rebuild")
    echo "Rebuilding Docker containers..."
    cd docker
    docker-compose down
    docker-compose build
    docker-compose up -d
    docker-compose logs -f
    ;;
  "start")
    echo "Starting Docker containers..."
    cd docker
    docker-compose up -d
    docker-compose logs -f
    ;;
  "stop")
    echo "Stopping Docker containers..."
    cd docker
    docker-compose down
    ;;
  "logs")
    echo "Showing logs..."
    cd docker
    docker-compose logs -f
    ;;
  "clean")
    echo "Cleaning up Docker environment..."
    cd docker
    docker-compose down -v
    docker system prune -af
    ;;
  *)
    echo "Usage: $0 {rebuild|start|stop|logs|clean}"
    echo "  rebuild - Rebuild and start containers"
    echo "  start   - Start containers"
    echo "  stop    - Stop containers"
    echo "  logs    - Show logs"
    echo "  clean   - Clean up everything (including volumes)"
    exit 1
    ;;
esac
