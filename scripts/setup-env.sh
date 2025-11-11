#!/bin/bash

# SEIM Environment Setup Script
# This script helps set up the .env file for Docker development

set -e

echo "🔧 SEIM Environment Setup"
echo "========================"

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. .env file unchanged."
        exit 1
    fi
fi

# Copy from template
echo "📝 Creating .env file from template..."
cp env.example .env

# Generate a secure secret key
echo "🔑 Generating secure Django secret key..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-$(openssl rand -hex 32)")

# Update the secret key in .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
else
    # Linux
    sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
fi

echo "✅ Environment setup complete!"
echo ""
echo "📋 Configuration summary:"
echo "   Database: postgresql://seimuser:seimpass@db:5432/seim"
echo "   Redis: redis://redis:6379/0"
echo "   Django Secret Key: Generated and set"
echo ""
echo "🚀 Next steps:"
echo "   1. Review .env file if needed: cat .env"
echo "   2. Start services: docker-compose up -d --build"
echo "   3. Access application: http://localhost:8000"
echo ""
echo "📚 For more information, see README.md" 