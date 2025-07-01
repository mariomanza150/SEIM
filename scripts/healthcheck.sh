#!/bin/bash
# Health check script for the Django application

# Check if the application is responding
curl -f http://localhost:8000/health/ || exit 1
